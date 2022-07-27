import os
from xml.etree import cElementTree

import dateutil.parser
import requests

from osmdiff.osm import OSMElement

OVERPASS_URL = "http://overpass-api.de/api"


class AugmentedDiff(object):
    base_url = OVERPASS_URL
    min_lon = None
    min_lat = None
    max_lon = None
    max_lat = None
    timestamp = None

    def __init__(
            self,
            minlon=None,
            minlat=None,
            maxlon=None,
            maxlat=None,
            debug=False,
            file=None,
            sequence_number=None,
            timestamp=None):
        self.debug = debug
        self.create = []
        self.modify = []
        self.delete = []
        if file:
            with open(file, 'r') as file_handle:
                self._parse_xml(file_handle)
        else:
            self.sequence_number = sequence_number
            if minlon and minlat and maxlon and maxlat:
                if maxlon > minlon and maxlat > minlat:
                    self.min_lon = minlon
                    self.min_lat = minlat
                    self.max_lon = maxlon
                    self.max_lat = maxlat
                else:
                    raise Exception("invalid bbox.")

    def get_state(self):
        """Get the current state from the OSM API"""
        state_url = os.path.join(
            self.base_url,
            "augmented_diff_status")
        response = requests.get(state_url, timeout=5)
        if response.status_code != 200:
            return False
        self.sequence_number = int(response.text)
        return True

    def _build_adiff_url(self):
        url = "{base}/augmented_diff?id={sequence_number}".format(
            base=self.base_url,
            sequence_number=self.sequence_number)
        if self.min_lon and self.min_lat and self.max_lon and self.max_lat:
            url += "&bbox={minlon},{minlat},{maxlon},{maxlat}".format(
                minlon=self.min_lon,
                minlat=self.min_lat,
                maxlon=self.max_lon,
                maxlat=self.max_lat)
        return url

    def _build_action(self, elem):
        if elem.attrib["type"] == "create":
            for child in elem:
                e = OSMElement.from_xml(child)
                self.__getattribute__("create").append(e)
        else:
            new = elem.find("new")
            old = elem.find("old")
            osm_obj_old = None
            osm_obj_new = None
            for child in old:
                osm_obj_old = OSMElement.from_xml(child)
            for child in new:
                osm_obj_new = OSMElement.from_xml(child)
            self.__getattribute__(
                elem.attrib["type"]).append({
                "old": osm_obj_old,
                "new": osm_obj_new})

    def _parse_xml(self, xml_str):
        for event, elem in cElementTree.iterparse(xml_str):
            if elem.tag == "remark":
                raise Exception(
                    "Augmented Diff API returned an error:",
                    elem.text)
            if elem.tag == "meta":
                timestamp = dateutil.parser.parse(elem.attrib.get("osm_base"))
                self.timestamp = timestamp
            if elem.tag == "action":
                self._build_action(elem)

    def retrieve(self, clear_cache=False):
        if not self.sequence_number:
            raise Exception("invalid sequence number")
        if clear_cache:
            self.create, self.modify, self.delete = ([], [], [])
        url = self._build_adiff_url()
        r = requests.get(url, stream=True, timeout=30)
        r.raw.decode_content = True
        self._parse_xml(r.raw)

    @classmethod
    def from_xml(cls, xml_str):
        o = cls()
        o._parse_xml(xml_str)
        return o

    def __repr__(self):
        return "AugmentedDiff ({create} created, {modify} modified, \
{delete} deleted)".format(
            create=len(self.create),
            modify=len(self.modify),
            delete=len(self.delete))
