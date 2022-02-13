from xml.etree import ElementPath
import xml.etree.ElementTree as ET


class OSMObject(object):

    def __init__(self):
        self.tags = {}
        self.attribs = {}
        self.bounds = None

    def __repr__(self):
        out = "{type} {id}".format(
            type=type(self).__name__,
            id=self.id)
        if type(self) == Way:
            out += " ({ways} nodes)".format(
                ways=len(self.nodes))
        if type(self) == Relation:
            out += " ({mem} members)".format(
                mem=len(self.members))
        return out

    def _parse_tags(self, elem):
        for tagelem in elem.findall("tag"):
            self.tags[tagelem.attrib["k"]] = tagelem.attrib["v"]

    def _parse_bounds(self, elem):
        be = elem.find("bounds")
        if be is not None:
            self.bounds = [
                be.attrib["minlon"],
                be.attrib["minlat"],
                be.attrib["maxlon"],
                be.attrib["maxlat"]]

    @classmethod
    def from_xml(cls, xml):
        osmtype = ""
        if isinstance(xml, ET.Element):
            root = xml
        else:
            root = ET.ElementTree(ET.fromstring(xml)).getroot()
        if root.tag == "osm":
            elem = root[0]
        else:
            elem = root
        if elem.tag in ("node", "nd"):
            o = Node()
        elif elem.tag == "way":
            o = Way()
            o._parse_nodes(elem)
        elif elem.tag == "relation":
            o = Relation()
            o._parse_members(elem)
        elif elem.tag == "member":
            o = Member()
        else:
            pass
        o.attribs = elem.attrib
        o._parse_tags(elem)
        o._parse_bounds(elem)
        return o

    def get_id(self):
        if isinstance(self, Member):
            return int(self.attribs['ref'])
        return int(self.attribs['id'])

    id = property(get_id)


class Node(OSMObject):

    def __init__(self):
        super().__init__()

    def _lon(self):
        _lon = self.attribs.get('lon')
        if _lon is not None:
            return float(_lon)
        return None

    lon = property(_lon)

    def _lat(self):
        _lat = self.attribs.get('lat')
        if _lat is not None:    
            return float(_lat)
        return None        

    lat = property(_lat)

    def _geo_interface(self):
        return {
            'type': 'Point',
            'coordinates': [self.lon, self.lat]
        }

    __geo_interface__ = property(_geo_interface)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.id == other.id


class Way(OSMObject):

    def __init__(self):
        self.nodes = []
        super().__init__()

    def _parse_nodes(self, elem):
        for node in elem.findall("nd"):
            way_node = Node()
            way_node.attribs["id"] = node.attrib["ref"]
            self.nodes.append(way_node)

    def _geo_interface(self):
        geom_type = 'LineString' if self.nodes[0] == self.nodes[-1] else 'Polygon'
        return {
            'type': geom_type,
            'coordinates': [
                [[n.lon, n.lat] for n in self.nodes]
            ]
        }
    
    def _closed(self):
        return self.nodes[0] == self.nodes[-1]

    closed = property(_closed)

    def _has_geometry(self):
        return all([nd.lon and nd.lat for nd in self.nodes])

    has_geometry = property(_has_geometry)

    __geo_interface__ = property(_geo_interface)


class Relation(OSMObject):

    def __init__(self):
        self.members = []
        super().__init__()

    def _parse_members(self, elem):
        for member in elem.findall("member"):
            self.members.append(OSMObject.from_xml(member))

    def _geo_interface(self):
        return {
            'type': 'FeatureCollection',
            'Features': [
                [f.__geo_interface__ for f in self.members]
            ]
        }

    __geo_interface__ = property(_geo_interface)
    

class Member(OSMObject):

    def __init__(self):
        super().__init__()

    def get_type(self):
        return self.attribs["type"]
    
    type = property(get_type)
