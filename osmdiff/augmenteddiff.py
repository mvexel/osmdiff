import os
from datetime import datetime
from xml.etree import cElementTree

import dateutil.parser
import requests

from osmdiff.osm.osm import Node

from .osm import OSMObject, Way

OVERPASS_URL = "http://overpass-api.de/api"


class AugmentedDiff:
    base_url = OVERPASS_URL
    minlon = None
    minlat = None
    maxlon = None
    maxlat = None
    timestamp = None

    def __init__(
        self,
        minlon=None,
        minlat=None,
        maxlon=None,
        maxlat=None,
        file=None,
        sequence_number=None,
        timestamp=None,
    ) -> None:
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
    def for_datetime(cls, dt: datetime):
        """
        Returns an instance of AugmentedDiff populated with the sequence_number for
        the minutely augmented diff preceding the datetime given. You will still need
        to retrieve() the actual augmented diff to populate the instance with data from OSM.
        """
        if dt > datetime.now():
            return None
        return AugmentedDiff(sequence_number=int(dt.timestamp()) // 60 - 22457216)

    def get_state(self):
        """Get the current state from the OSM API"""
        state_url = os.path.join(self.base_url, "augmented_diff_status")
        response = requests.get(state_url, timeout=5)
        if response.status_code != 200:
            return False
        self.sequence_number = int(response.text)
        return self.sequence_number

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
        if elem.attrib["type"] == "create":
            for child in elem:
                e = OSMObject.from_xml(child)
                self.__getattribute__("create").append(e)
        else:
            new = elem.find("new")
            old = elem.find("old")
            osm_obj_old = None
            osm_obj_new = None
            for child in old:
                osm_obj_old = OSMObject.from_xml(child)
            for child in new:
                osm_obj_new = OSMObject.from_xml(child)
            self.__getattribute__(elem.attrib["type"]).append(
                {"old": osm_obj_old, "new": osm_obj_new}
            )

    def _parse_stream(self, stream):
        for event, elem in cElementTree.iterparse(stream):
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
        try:
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code != 200:
                return r.status_code
            r.raw.decode_content = True
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
