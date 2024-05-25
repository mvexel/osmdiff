from posixpath import join as urljoin
from gzip import GzipFile
from xml.etree import ElementTree

import requests

from osmdiff.osm import OSMObject

REPLICATION_URL = "https://planet.openstreetmap.org/replication"


class OSMChange(object):
    def __init__(
        self,
        url=REPLICATION_URL,
        frequency="minute",
        file=None,
        sequence_number=None,
        debug=False,
    ):
        self.base_url = url
        self.debug = debug
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

    def get_state(self):
        """Get the current state from the OSM API"""
        state_url = urljoin(self.base_url, self._frequency, "state.txt")
        response = requests.get(state_url, timeout=5)
        if response.status_code != 200:
            return False
        for line in response.text.split("\n"):
            if self.debug:
                print(line)
            if line.startswith("sequenceNumber"):
                self._sequence_number = int(line[15:])
        return True

    def _build_sequence_url(self):
        seqno = str(self._sequence_number).zfill(9)
        url = urljoin(
            self.base_url,
            self._frequency,
            seqno[:3],
            seqno[3:6],
            "{}{}".format(seqno[6:], ".osc.gz"),
        )
        if self.debug:
            print(url)
        return url

    def _parse_xml(self, xml):
        for event, elem in xml:
            # if self.debug:
            #     print(event, elem)
            if elem.tag in ("create", "modify", "delete"):
                self._build_action(elem)
                if self.debug:
                    print("======={action}========".format(action=elem.tag))

    def _build_action(self, elem):
        for thing in elem:
            o = OSMObject.from_xml(thing)
            self.__getattribute__(elem.tag).append(o)
            if self.debug:
                print(o)
                print(o.attribs)
                print(o.tags)
                print(o.bounds)

    def retrieve(self, clear_cache=False) -> int:
        """
        Retrieve the OSM diff corresponding to the OSMChange sequence_number.
        """
        if not self._sequence_number:
            raise Exception("invalid sequence number")
        if clear_cache:
            self.create, self.modify, self.delete = ([], [], [])
        try:
            r = requests.get(self._build_sequence_url(), stream=True, timeout=30)
            if r.status_code != 200:
                return r.status_code
            gzfile = GzipFile(fileobj=r.raw)
            xml = ElementTree.iterparse(gzfile, events=("start", "end"))
            self._parse_xml(xml)
            return r.status_code
        except ConnectionError:
            # FIXME catch this?
            return 0

    @classmethod
    def from_xml(cls, xml):
        """
        Initialize OSMChange object from an XML object.

        If you used this method before version 0.3, please note that this
        method now takes an XML object. If you want to initialize from a file,\
        use the from_xml_file method.

        :param path: path to the XML file
        :type path: str
        :return: OSMChange object
        :rtype: OSMChange

        """
        new_osmchange_obj = cls()
        new_osmchange_obj._parse_xml(xml)
        return new_osmchange_obj

    @classmethod
    def from_xml_file(cls, path):
        """
        Initialize OSMChange object from an XML file.

        :param path: path to the XML file
        :type path: str
        :return: OSMChange object
        :rtype: OSMChange

        """
        with open(path, "r") as fh:
            xml = ElementTree.iterparse(fh, events=("start", "end"))
            return cls.from_xml(xml)

    def sequence_number(self):
        return self._sequence_number

    def set_sequence_number(self, sn):
        self._sequence_number = int(sn)

    sequence_number = property(sequence_number, set_sequence_number)

    def __repr__(self):
        return "OSMChange ({create} created, {modify} modified, \
{delete} deleted)".format(
            create=len(self.create), modify=len(self.modify), delete=len(self.delete)
        )
