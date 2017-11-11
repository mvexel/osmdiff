import os
import gzip
from xml.etree import cElementTree
import requests
from osmdiff.osm import OSMObject


class AugmentedDiff(object):
    base_url = "http://overpass-api.de/api"
    minlon = None
    minlat = None
    maxlon = None
    maxlat = None
    debug = False

    def __init__(
            self,
            minlon=None,
            minlat=None,
            maxlon=None,
            maxlat=None,
            debug=False,
            file=None,
            sequence_number=None):
        self.debug = debug
        self.create = []
        self.modify = []
        self.delete = []
        if file:
            with open(file, 'r') as file_handle:
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
        state_url = os.path.join(
            self.base_url,
            "augmented_diff_status")
        if self.debug:
            print("getting state from", state_url)
        response = requests.get(state_url, timeout=5)
        if response.status_code != 200:
            return False
        self.sequence_number = int(response.text)
        return True

    def _build_adiff_url(self):
        url = "{base}/augmented_diff?id={sequence_number}".format(
            base=self.base_url,
            sequence_number=self.sequence_number)
        if self.minlon and self.minlat and self.maxlon and self.maxlat:
            url += "&bbox={minlon},{minlat},{maxlon},{maxlat}".format(
                minlon=self.minlon,
                minlat=self.minlat,
                maxlon=self.maxlon,
                maxlat=self.maxlat)
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
                print(
                    elem.attrib["type"],
                    ": old",
                    osm_obj_old,
                    ", new",
                    osm_obj_new)
            self.__getattribute__(
                elem.attrib["type"]).append({
                    "old": osm_obj_old,
                    "new": osm_obj_new})

    def _parse_stream(self, stream):
        for event, elem in cElementTree.iterparse(stream):
            # if self.debug:
            #     print(event, elem)
            if elem.tag == "remark":
                raise Exception(
                    "Augmented Diff API returned an error:",
                    elem.text)
            if elem.tag == "action":
                self._build_action(elem)

    def retrieve(self):
        if not self.sequence_number:
            raise Exception("invalid sequence number")
        url = self._build_adiff_url()
        if self.debug:
            print("retrieving...")
        r = requests.get(url, stream=True, timeout=30)
        r.raw.decode_content = True
        if self.debug:
            print("parsing...")
        self._parse_stream(r.raw)

    def __repr__(self):
        return "AugmentedDiff ({create} created, {modify} modified, \
{delete} deleted)".format(
            create=len(self.create),
            modify=len(self.modify),
            delete=len(self.delete))


class OSMChange(object):
    base_url = "https://planet.openstreetmap.org/replication"
    sequence_number = None
    debug = False

    def __init__(
            self,
            frequency="minute",
            file=None,
            sequence_number=None,
            debug=False):
        self.debug = debug
        self.create = []
        self.modify = []
        self.delete = []
        if file:
            with open(file, 'r') as fh:
                self._parse_stream(fh)
        else:
            self.frequency = frequency
            self.sequence_number = sequence_number

    def get_state(self):
        """Get the current state from the OSM API"""
        state_url = os.path.join(self.base_url, self.frequency, "state.txt")
        response = requests.get(state_url, timeout=5)
        if response.status_code != 200:
            return False
        for line in response.text.split("\n"):
            if self.debug:
                print(line)
            if line.startswith("sequenceNumber"):
                self.sequence_number = int(line[15:])
        return True

    def _build_sequence_url(self):
        seqno = str(self.sequence_number).zfill(9)
        url = os.path.join(
            self.base_url,
            self.frequency,
            seqno[:3],
            seqno[3:6],
            "{}{}".format(seqno[6:], ".osc.gz"))
        if self.debug:
            print(url)
        return url

    def _parse_stream(self, stream):
        for event, elem in cElementTree.iterparse(stream):
            # if self.debug:
            #     print(event, elem)
            if elem.tag in ("create", "modify", "delete"):
                self._build_action(elem)
                if self.debug:
                    print("======={action}========".format(
                        action=elem.tag))

    def _build_action(self, elem):
        for thing in elem:
            o = OSMObject.from_xml(thing)
            self.__getattribute__(elem.tag).append(o)
            if self.debug:
                print(o)
                print(o.attribs)
                print(o.tags)
                print(o.bounds)

    def retrieve(self):
        if not self.sequence_number:
            raise Exception("invalid sequence number")
        r = requests.get(self._build_sequence_url(), stream=True, timeout=30)
        gzfile = gzip.GzipFile(fileobj=r.raw)
        self._parse_stream(gzfile)

    def __repr__(self):
        return "OSMChange ({create} created, {modify} modified, \
{delete} deleted)".format(
            create=len(self.create),
            modify=len(self.modify),
            delete=len(self.delete))
