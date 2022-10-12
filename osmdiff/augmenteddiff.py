import os
from xml.etree import cElementTree

import dateutil.parser
import requests

from .osm import OSMObject

OVERPASS_URL = "http://overpass-api.de/api"


class AugmentedDiff(object):
    base_url = OVERPASS_URL
    minlon = None
    minlat = None
    maxlon = None
    maxlat = None
    timestamp = None
    debug = False

    def __init__(
        self,
        minlon=None,
        minlat=None,
        maxlon=None,
        maxlat=None,
        debug=False,
        file=None,
        sequence_number=None,
        timestamp=None,
    ):
        self.debug = debug
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

    def get_state(self):
        """Get the current state from the OSM API"""
        state_url = os.path.join(self.base_url, "augmented_diff_status")
        if self.debug:
            print("getting state from", state_url)
        response = requests.get(state_url, timeout=5)
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
        if self.debug:
            print(url)
        return url

    def _build_action(self, elem):
        if elem.attrib["type"] == "create":
            for child in elem:
                e = OSMObject.from_xml(child)
                self.__getattribute__("create").append(e)
                if self.debug:
                    print(elem.attrib["type"], e)
        else:
            new = elem.find("new")
            old = elem.find("old")
            osm_obj_old = None
            osm_obj_new = None
            for child in old:
                osm_obj_old = OSMObject.from_xml(child)
            for child in new:
                osm_obj_new = OSMObject.from_xml(child)
            if self.debug:
                print(elem.attrib["type"], ": old", osm_obj_old, ", new", osm_obj_new)
            self.__getattribute__(elem.attrib["type"]).append(
                {"old": osm_obj_old, "new": osm_obj_new}
            )

    def _parse_stream(self, stream):
        for event, elem in cElementTree.iterparse(stream):
            # if self.debug:
            #     print(event, elem)
            if elem.tag == "remark":
                raise Exception("Augmented Diff API returned an error:", elem.text)
            if elem.tag == "meta":
                timestamp = dateutil.parser.parse(elem.attrib.get("osm_base"))
                self.timestamp = timestamp
            if elem.tag == "action":
                self._build_action(elem)

    def retrieve(self, clear_cache=False) -> int:
        """
        Retrieve the Augmented diff corresponding to the sequence_number.
        """
        if not self.sequence_number:
            raise Exception("invalid sequence number")
        if clear_cache:
            self.create, self.modify, self.delete = ([], [], [])
        url = self._build_adiff_url()
        if self.debug:
            print("retrieving...")
        try:
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code != 200:
                return r.status_code
            r.raw.decode_content = True
            if self.debug:
                print("parsing...")
            self._parse_stream(r.raw)
            return r.status_code
        except ConnectionError:
            # FIXME should we catch instead?
            return 0

    def __repr__(self):
        return "AugmentedDiff ({create} created, {modify} modified, \
{delete} deleted)".format(
            create=len(self.create), modify=len(self.modify), delete=len(self.delete)
        )
