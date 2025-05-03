from posixpath import join as urljoin
from xml.etree import ElementTree
from datetime import datetime, timedelta
from typing import Optional
import time
import logging
from contextlib import contextmanager

import dateutil.parser
import requests

from .osm import OSMObject
from .config import API_CONFIG, AUGMENTED_DIFF_CONFIG, DEFAULT_HEADERS

from osmdiff.settings import DEFAULT_OVERPASS_URL


class AugmentedDiff(object):
    """An Augmented Diff representation for OpenStreetMap changes.

    This class handles the retrieval and parsing of OpenStreetMap augmented diffs,
    which contain detailed information about changes made to OSM data, including
    creations, modifications, and deletions.

    Parameters:
        minlon (float | None): Minimum longitude of bounding box
        minlat (float | None): Minimum latitude of bounding box
        maxlon (float | None): Maximum longitude of bounding box
        maxlat (float | None): Maximum latitude of bounding box
        file (str | None): Path to an augmented diff file to parse
        sequence_number (int | None): Sequence number of the augmented diff
        timestamp (datetime | None): Timestamp of the augmented diff

    Attributes:
        base_url: Base URL for the Overpass API
        create: List of created OSM objects
        modify: List of modified OSM objects (containing old and new versions)
        delete: List of deleted OSM objects
        remarks: List of remarks from the augmented diff
        timestamp: Timestamp of the augmented diff

    Raises:
        Exception: If an invalid bounding box is provided
        ValueError: If sequence_number is not parseable as an integer

    Example:
        ```python
        # Create an AugmentedDiff instance with a bounding box
        adiff = AugmentedDiff(
            minlon=-0.489,
            minlat=51.28,
            maxlon=0.236,
            maxlat=51.686
        )

        # Get the current state
        adiff.get_state()

        # Retrieve the diff
        status = adiff.retrieve()
        if status == 200:
            print(f"Created: {len(adiff.create)}")
            print(f"Modified: {len(adiff.modify)}")
            print(f"Deleted: {len(adiff.delete)}")
        ```
    """

    base_url = DEFAULT_OVERPASS_URL
    minlon = None
    minlat = None
    maxlon = None
    maxlat = None
    timestamp = None
    remarks = []

    def __init__(
        self,
        minlon: Optional[float] = None,
        minlat: Optional[float] = None,
        maxlon: Optional[float] = None,
        maxlat: Optional[float] = None,
        file: Optional[str] = None,
        sequence_number: Optional[int] = None,
        timestamp: Optional[datetime] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        # Initialize with defaults from config
        self.base_url = base_url or API_CONFIG["overpass"]["base_url"]
        self.timeout = timeout or API_CONFIG["overpass"]["timeout"]

        # Initialize other config values
        self.minlon = minlon
        self.minlat = minlat
        self.maxlon = maxlon
        self.maxlat = maxlat
        self.timestamp = timestamp
        self._remarks = []
        self._sequence_number = None
        self.create = []
        self.modify = []
        self.delete = []
        if file:
            with open(file, "r") as file_handle:
                self._parse_stream(file_handle)
        else:
            self.sequence_number = sequence_number
            if minlon and minlat and maxlon and maxlat:
                if maxlon > minlon and maxlat > minlat:
                    self.minlon = minlon
                    self.minlat = minlat
                    self.maxlon = maxlon
                    self.maxlat = maxlat
                else:
                    raise Exception("invalid bbox.")

    @classmethod
    def get_state(cls, base_url: Optional[str] = None, timeout: Optional[int] = None) -> Optional[dict]:
        """Get the current state from the OSM API.

        Args:
            base_url: Optional override for API base URL
            timeout: Optional override for request timeout

        Returns:
            Dictionary with state info if successful, None if failed
        """
        base = base_url or API_CONFIG["overpass"]["base_url"]
        state_url = urljoin(base, "api/0.6/changesets/state")
        try:
            response = requests.get(
                state_url, 
                timeout=timeout or 5,
                headers=DEFAULT_HEADERS
            )
            if response.status_code != 200:
                return None
            
            # Parse XML response
            root = ElementTree.fromstring(response.content)
            state = root.find('state')
            if state is None:
                return None
                
            result = {}
            for child in state:
                if child.text:
                    result[child.tag] = child.text
            return result
            
        except (requests.exceptions.RequestException, ValueError, ElementTree.ParseError):
            return None

    def _build_adiff_url(self):
        url = "{base}/augmented_diff?id={sequence_number}".format(
            base=self.base_url, sequence_number=self.sequence_number
        )
        if self.minlon and self.minlat and self.maxlon and self.maxlat:
            url += "&bbox={minlon},{minlat},{maxlon},{maxlat}".format(
                minlon=self.minlon,
                minlat=self.minlat,
                maxlon=self.maxlon,
                maxlat=self.maxlat,
            )
        return url

    def _build_action(self, elem):
        """Parse an action element from an augmented diff.

        Actions in augmented diffs are ordered: nodes first, then ways, then relations.
        Within each type, elements are ordered by ID.
        """
        action_type = elem.attrib["type"]

        if action_type == "create":
            for child in elem:
                osm_obj = OSMObject.from_xml(child)
                self.create.append(osm_obj)
        elif action_type == "modify":
            old = elem.find("old")
            new = elem.find("new")
            if old is not None and new is not None:
                osm_obj_old = None
                osm_obj_new = None
                for child in old:
                    osm_obj_old = OSMObject.from_xml(child)
                for child in new:
                    osm_obj_new = OSMObject.from_xml(child)
                if osm_obj_old and osm_obj_new:
                    self.modify.append({"old": osm_obj_old, "new": osm_obj_new})
        elif action_type == "delete":
            old = elem.find("old")
            new = elem.find("new")
            osm_obj_old = None
            osm_obj_new = None
            if old is not None:
                for child in old:
                    osm_obj_old = OSMObject.from_xml(child)
            if new is not None:
                for child in new:
                    osm_obj_new = OSMObject.from_xml(child)
            if osm_obj_old is not None or osm_obj_new is not None:
                # Store both old and new, and optionally meta info
                deletion_info = {"old": osm_obj_old, "new": osm_obj_new, "meta": elem.attrib.copy()}
                self.delete.append(deletion_info)

    def _parse_stream(self, stream):
        for event, elem in ElementTree.iterparse(stream):
            if elem.tag == "remark":
                self._remarks.append(elem.text)
            if elem.tag == "meta":
                timestamp = dateutil.parser.parse(elem.attrib.get("osm_base"))
                self.timestamp = timestamp
            if elem.tag == "action":
                self._build_action(elem)

    def retrieve(
        self,
        clear_cache: bool = False,
        timeout: Optional[int] = None,
        auto_increment: bool = True,
        max_retries: int = 3,
    ) -> int:
        """Retrieve the Augmented diff corresponding to the sequence_number.

        Args:
            clear_cache: Whether to clear existing data before retrieval.
            timeout: Request timeout in seconds.
            auto_increment: Whether to automatically increment sequence number after retrieval.
            max_retries: Maximum number of retry attempts for failed requests.

        Returns:
            HTTP status code of the request (200 for success)

        Raises:
            Exception: If sequence_number is not set
            requests.exceptions.RequestException: If all retry attempts fail
        """
        if not self.sequence_number:
            raise Exception("invalid sequence number")

        if clear_cache:
            self.create, self.modify, self.delete = ([], [], [])

        url = self._build_adiff_url()

        # Store current data before making request
        prev_create = self.create.copy()
        prev_modify = self.modify.copy()
        prev_delete = self.delete.copy()

        # Use a longer timeout if none specified
        request_timeout = (
            timeout or self.timeout or 120
        )  # 2 minutes default, this will still fail for very large diffs, like 12346

        for attempt in range(max_retries):
            try:
                # Exponential backoff between retries
                if attempt > 0:
                    time.sleep(2**attempt)  # 2, 4, 8 seconds...

                r = requests.get(
                    url, stream=True, timeout=request_timeout, headers=DEFAULT_HEADERS
                )

                if r.status_code != 200:
                    return r.status_code

                r.raw.decode_content = True

                # Clear current lists but keep previous data
                self.create, self.modify, self.delete = ([], [], [])

                # Parse new data
                self._parse_stream(r.raw)

                # Merge with previous data
                self.create = prev_create + self.create
                self.modify = prev_modify + self.modify
                self.delete = prev_delete + self.delete

                # Automatically increment sequence number after successful retrieval
                if auto_increment:
                    self.sequence_number += 1

                return r.status_code

            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
            ) as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise
                continue

        return 0  # Should never reach here due to raise in except block

    @property
    def remarks(self):
        return self._remarks

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def sequence_number(self):
        return self._sequence_number

    @sequence_number.setter
    def sequence_number(self, value):
        try:
            # value can be none
            if value is None:
                self._sequence_number = None
                return
            self._sequence_number = int(value)
        except ValueError:
            raise ValueError(
                "sequence_number must be an integer or parsable as an integer"
            )

    @property 
    def actions(self):
        """Get all actions combined in a single list."""
        return {
            'create': self.create,
            'modify': self.modify,
            'delete': self.delete
        }

    def __repr__(self):
        return "AugmentedDiff ({create} created, {modify} modified, \
{delete} deleted)".format(
            create=len(self.create), modify=len(self.modify), delete=len(self.delete)
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clear all changes when exiting context."""
        self.create.clear()
        self.modify.clear()
        self.delete.clear()


class ContinuousAugmentedDiff:
    """Iterator class for continuously fetching augmented diffs.

    This class handles the continuous retrieval of augmented diffs with proper
    backoff and state checking. It yields AugmentedDiff objects as new diffs
    become available.

    Parameters:
        minlon (float | None): Minimum longitude of bounding box
        minlat (float | None): Minimum latitude of bounding box
        maxlon (float | None): Maximum longitude of bounding box
        maxlat (float | None): Maximum latitude of bounding box
        base_url (str | None): Override default Overpass API URL
        timeout (int | None): Request timeout in seconds
        min_interval (int): Minimum seconds between checks (default: 30)
        max_interval (int): Maximum seconds between checks (default: 120)

    Example:
        ```python
        # Create continuous fetcher for London area
        fetcher = ContinuousAugmentedDiff(
            minlon=-0.489,
            minlat=51.28,
            maxlon=0.236,
            maxlat=51.686
        )

        # Iterate over diffs as they become available
        for diff in fetcher:
            print(f"Got diff {diff.sequence_number} with {len(diff.create)} creates")
        ```
    """

    def __init__(
        self,
        minlon: Optional[float] = None,
        minlat: Optional[float] = None,
        maxlon: Optional[float] = None,
        maxlat: Optional[float] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        min_interval: int = 30,
        max_interval: int = 120,
    ):
        self.bbox = (minlon, minlat, maxlon, maxlat)
        self.base_url = base_url
        self.timeout = timeout
        self.min_interval = min_interval
        self.max_interval = max_interval
        
        self._current_sequence = None
        self._current_interval = min_interval
        self._last_check = None
        self._logger = logging.getLogger(__name__)

    def _wait_for_next_check(self) -> None:
        """Wait appropriate time before next check, using exponential backoff."""
        now = datetime.now()
        if self._last_check:
            elapsed = (now - self._last_check).total_seconds()
            wait_time = max(0, self._current_interval - elapsed)
            if wait_time > 0:
                time.sleep(wait_time)

        self._last_check = datetime.now()

    def _backoff(self) -> None:
        """Increase check interval, up to max_interval."""
        self._current_interval = min(
            self._current_interval * 2,
            self.max_interval
        )

    def _reset_backoff(self) -> None:
        """Reset check interval to minimum."""
        self._current_interval = self.min_interval

    def __iter__(self):
        return self

    def __next__(self) -> AugmentedDiff:
        """Get next available augmented diff.
        
        Yields:
            AugmentedDiff: Next available diff
            
        Raises:
            StopIteration: Never raised, iterates indefinitely
        """
        while True:
            self._wait_for_next_check()
            
            # Get current state
            new_sequence = AugmentedDiff.get_state(
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            if new_sequence is None:
                self._logger.warning("Failed to get state, backing off")
                self._backoff()
                continue
                
            # Initialize sequence number on first run
            if self._current_sequence is None:
                self._current_sequence = new_sequence
                continue
                
            # Check if new diff is available
            if new_sequence <= self._current_sequence:
                self._backoff()
                continue
                
            # Create diff object for new sequence
            diff = AugmentedDiff(
                minlon=self.bbox[0],
                minlat=self.bbox[1],
                maxlon=self.bbox[2],
                maxlat=self.bbox[3],
                sequence_number=self._current_sequence + 1,
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            # Try to retrieve the diff
            try:
                status = diff.retrieve(auto_increment=False)
                if status != 200:
                    self._logger.warning(f"Failed to retrieve diff: HTTP {status}")
                    self._backoff()
                    continue
                    
                # Success! Reset backoff and update sequence
                self._reset_backoff()
                self._current_sequence += 1
                return diff
                
            except Exception as e:
                self._logger.warning(f"Error retrieving diff: {e}")
                self._backoff()
                continue
