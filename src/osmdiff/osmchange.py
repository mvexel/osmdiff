from gzip import GzipFile
import os
import requests
from osmdiff.osm import OSMObject
import xml.etree.ElementTree as ET

REPLICATION_URL = "https://planet.openstreetmap.org/replication"

class OSMChange(object):

    def __init__(
            self,
            url=REPLICATION_URL,
            frequency="minute",
            file=None,
            sequence_number=None):
        self.base_url = url
        self.create = []
        self.modify = []
        self.delete = []
        if file:
            with open(file, 'r') as fh:
                self._parse_xml(fh)
        else:
            self._frequency = frequency
            self._sequence_number = sequence_number

    def get_state(self):
        """Get the current state from the OSM API"""
        state_url = os.path.join(self.base_url, self._frequency, "state.txt")
        response = requests.get(state_url, timeout=5)
        if response.status_code != 200:
            return False
        for line in response.text.split("\n"):
            if line.startswith("sequenceNumber"):
                self._sequence_number = int(line[15:])
        return True

    def _build_sequence_url(self):
        seqno = str(self._sequence_number).zfill(9)
        url = os.path.join(
            self.base_url,
            self._frequency,
            seqno[:3],
            seqno[3:6],
            "{}{}".format(seqno[6:], ".osc.gz"))
        return url

    def _parse_xml(self, xml_str):
        root = ET.ElementTree(ET.fromstring(xml_str)).getroot()
        for child in root:
            if child.tag in ("create", "modify", "delete"):
                self._build_action(child)
                    
    def _build_action(self, elem):
        for thing in elem:
            o = OSMObject.from_xml(thing)
            self.__getattribute__(elem.tag).append(o)

    def retrieve(self, clear_cache=False):
        if not self._sequence_number:
            raise Exception("invalid sequence number")
        if clear_cache:
            self.create, self.modify, self.delete = ([], [], [])
        r = requests.get(self._build_sequence_url(), stream=True, timeout=30)
        gzfile = GzipFile.GzipFile(fileobj=r.raw)
        self._parse_xml(gzfile)

    @classmethod
    def from_xml(cls, xml_str):
        o = cls()
        o._parse_xml(xml_str)
        return o

    def sequence_number(self):
        return self._sequence_number
    
    def set_sequence_number(self, sn):
        self._sequence_number = int(sn)
    
    sequence_number = property(sequence_number, set_sequence_number)

    def __repr__(self):
        return "OSMChange ({create} created, {modify} modified, \
{delete} deleted)".format(
            create=len(self.create),
            modify=len(self.modify),
            delete=len(self.delete))
