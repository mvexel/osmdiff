import xml.etree.ElementTree as ET
import osmdiff

class OSMElement(object):

    def __init__(self, id=None):
        self.tags = {}
        self._attrib = {}
        self._bounds = None
        self._id = id

    def __repr__(self):
        out = "{type} {id}".format(
            type=type(self).__name__,
            id=self.id)
        if type(self) == osmdiff.osm.Way:
            out += " ({ways} nodes)".format(
                ways=len(self.nodes))
        if type(self) == osmdiff.osm.Relation:
            out += " ({mem} members)".format(
                mem=len(self.members))
        return out

    def _parse_tags(self, elem):
        for tagelem in elem.findall("tag"):
            self.tags[tagelem.attrib["k"]] = tagelem.attrib["v"]

    def _parse_bounds(self, elem):
        be = elem.find("bounds")
        if be is not None:
            self._bounds = [
                be.attrib["minlon"],
                be.attrib["minlat"],
                be.attrib["maxlon"],
                be.attrib["maxlat"]]

    @classmethod
    def from_xml(cls, xml):
        if isinstance(xml, ET.Element):
            root = xml
        else:
            root = ET.ElementTree(ET.fromstring(xml)).getroot()
        if root.tag == "osm":
            elem = root[0]
        else:
            elem = root
        if elem.tag == "node":
            o = osmdiff.osm.Node(
                lon=float(elem.attrib['lon']),
                lat=float(elem.attrib['lat']),
                id=int(elem.attrib['id']))
        elif elem.tag == "nd":
            o = osmdiff.osm.member.ElementReference(
                id=int(elem.attrib['ref']))
        elif elem.tag == "way":
            o = osmdiff.osm.Way(
                id=int(elem.attrib['id']))
            o._parse_elementreferences(elem)
        elif elem.tag == "relation":
            o = osmdiff.osm.Relation(
                id=int(elem.attrib['id']))
            o._parse_members(elem)
        elif elem.tag == "member":
            o = osmdiff.osm.ElementReference(
                id=int(elem.attrib['ref']),
                osmtype=elem.attrib['type'])
        else:
            pass
        o._attrib = elem.attrib
        o._parse_tags(elem)
        o._parse_bounds(elem)
        return o

    def get_id(self):
        return self._id

    id = property(get_id)

    def get_bounds(self):
        return self._bounds

    bounds = property(get_bounds)

    def get_attrib(self):
        return self._attrib

    attrib = property(get_attrib)