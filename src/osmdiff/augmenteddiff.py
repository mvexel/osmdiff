from posixpath import join as urljoin
from xml.etree import ElementTree
from datetime import datetime
from typing import Optional
import time

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

    def get_state(self) -> bool:
        """Get the current state from the OSM API.

        Returns:
            True if state was successfully retrieved, False otherwise
        """
        state_url = urljoin(self.base_url, "augmented_diff_status")
        response = requests.get(
            state_url, timeout=self.timeout or 5  # Use instance timeout with fallback
        )
        if response.status_code != 200:
            return False
        self.sequence_number = int(response.text)
        return True

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
            if old is not None:
                for child in old:
                    osm_obj_old = OSMObject.from_xml(child)
                    self.delete.append({"old": osm_obj_old})

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
