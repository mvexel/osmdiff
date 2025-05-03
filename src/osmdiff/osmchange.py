from posixpath import join as urljoin
from gzip import GzipFile
from xml.etree import ElementTree
from typing import Optional

import requests

from osmdiff.osm import OSMObject
from osmdiff.config import API_CONFIG, DEFAULT_HEADERS


class OSMChange(object):
    """
    Class to represent an OSMChange object.

    Parameters:
        url (str | None): URL of the OSM replication server
        frequency (str): frequency of the replication diff
        file (str | None): path to the XML file
        sequence_number (int | None): sequence number of the diff
        timeout (int | None): request timeout

    Attributes:
        base_url (str): URL of the OSM replication server
        timeout (int): request timeout
        create (list): list of created OSM objects
        modify (list): list of modified OSM objects
        delete (list): list of deleted OSM objects

    Raises:
        Exception: If an invalid sequence number is provided
        ValueError: If frequency is not one of the valid options

    Example:
        ```python
        # Create an OSMChange object with a URL and frequency
        osmchange = OSMChange(
            url="https://osm.example.com",
            frequency="minute",
            file="path/to/osmchange.xml",
            sequence_number=123456789,
        )
        ```
    """

    def __init__(
        self,
        url: Optional[str] = None,
        frequency: str = "minute",
        file: Optional[str] = None,
        sequence_number: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        # Initialize with defaults from config
        self.base_url = url or API_CONFIG["osm"]["base_url"]
        self.timeout = timeout or API_CONFIG["osm"]["timeout"]

        self.create = []
        self.modify = []
        self.delete = []

        if file:
            with open(file, "r") as fh:
                xml = ElementTree.iterparse(fh, events=("start", "end"))
                self._parse_xml(xml)
        else:
            self._frequency = frequency
            self._sequence_number = sequence_number

    def get_state(self) -> bool:
        """
        Retrieve the current state from the OSM API.

        Returns:
            bool: True if state was successfully retrieved, False otherwise

        Raises:
            requests.RequestException: If the API request fails
        """
        state_url = urljoin(self.base_url, "api/0.6/changesets/state")
        response = requests.get(
            state_url, timeout=self.timeout, headers=DEFAULT_HEADERS
        )
        if response.status_code != 200:
            return False
        
        # Parse XML response
        root = ElementTree.fromstring(response.content)
        state = root.find('state')
        if state is not None:
            seq = state.find('sequenceNumber')
            if seq is not None and seq.text:
                self._sequence_number = int(seq.text)
                return True
        return False

    def _build_sequence_url(self) -> str:
        seqno = str(self._sequence_number).zfill(9)
        url = urljoin(
            self.base_url,
            self._frequency,
            seqno[:3],
            seqno[3:6],
            "{}{}".format(seqno[6:], ".osc.gz"),
        )
        return url

    def _parse_xml(self, xml) -> None:
        for event, elem in xml:
            if elem.tag in ("create", "modify", "delete"):
                self._build_action(elem)

    def _build_action(self, elem: ElementTree.Element) -> None:
        """
        Build OSM objects from XML elements and add them to the appropriate list.

        Args:
            elem (ElementTree.Element): XML element containing OSM objects
        """
        for thing in elem:
            o = OSMObject.from_xml(thing)
            getattr(self, elem.tag).append(o)  # Use getattr instead of __getattribute__

    def retrieve(self, clear_cache: bool = False, timeout: Optional[int] = None) -> int:
        """
        Retrieve the OSM diff corresponding to the OSMChange sequence_number.

        Parameters:
            clear_cache (bool): clear the cache
            timeout (int): request timeout

        Returns:
            int: HTTP status code

        Raises:
            Exception: If an invalid sequence number is provided
        """
        if not self._sequence_number:
            raise Exception("invalid sequence number")
        if clear_cache:
            self.create, self.modify, self.delete = ([], [], [])
        try:
            r = requests.get(
                self._build_sequence_url(),
                stream=True,
                timeout=timeout or self.timeout,
                headers=DEFAULT_HEADERS,
            )
            if r.status_code != 200:
                return r.status_code
            # Handle both gzipped and plain XML responses
            content = r.content
            if content.startswith(b'\x1f\x8b'):  # Gzip magic number
                gzfile = GzipFile(fileobj=r.raw)
                xml = ElementTree.iterparse(gzfile, events=("start", "end"))
            else:
                xml = ElementTree.iterparse(r.raw, events=("start", "end"))
            self._parse_xml(xml)
            return r.status_code
        except ConnectionError:
            # FIXME catch this?
            return 0

    @classmethod
    def from_xml(cls, xml: ElementTree.Element) -> "OSMChange":
        """
        Initialize OSMChange object from an XML object.

        If you used this method before version 0.3, please note that this
        method now takes an XML object. If you want to initialize from a file,\
        use the from_xml_file method.

        Parameters:
            xml (ElementTree.Element): XML object

        Returns:
            OSMChange: OSMChange object
        """
        new_osmchange_obj = cls()
        new_osmchange_obj._parse_xml(xml)
        return new_osmchange_obj

    @classmethod
    def from_xml_file(cls, path) -> "OSMChange":
        """
        Initialize OSMChange object from an XML file.

        Parameters:
            path (str): path to the XML file

        Returns:
            OSMChange: OSMChange object
        """
        with open(path, "r") as fh:
            xml = ElementTree.iterparse(fh, events=("start", "end"))
            return cls.from_xml(xml)

    @property
    def sequence_number(self) -> int:
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
    def frequency(self) -> str:
        return self._frequency

    @frequency.setter
    def frequency(self, f: str) -> None:
        """
        Set the frequency for OSM changes.

        Args:
            f (str): Frequency ('minute', 'hour', or 'day')

        Raises:
            ValueError: If frequency is not one of the valid options
        """
        VALID_FREQUENCIES = {"minute", "hour", "day"}
        if f not in VALID_FREQUENCIES:
            raise ValueError(
                f"Frequency must be one of: {', '.join(VALID_FREQUENCIES)}"
            )
        self._frequency = f

    @property
    def actions(self):
        """Get all actions combined in a single list."""
        return {
            'create': self.create,
            'modify': self.modify, 
            'delete': self.delete
        }

    def __repr__(self):
        return "OSMChange ({create} created, {modify} modified, \
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
