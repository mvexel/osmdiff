class OSMObject(object):

    def __init__(self):
        self.tags = {}
        self.attribs = {}
        self.bounds = None

    def __repr__(self):
        out = "{type} {id}".format(
            type=type(self).__name__,
            id=self.attribs.get("id"))
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
    def from_xml(cls, root):
        osmtype = ""
        if root.tag == "osm":
            elem = root[0]
        else:
            elem = root
        if elem.tag == "member":
            osmtype = elem.attrib["type"]
        else:
            osmtype = elem.tag
        if osmtype in ("node", "nd"):
            o = Node()
        elif osmtype == "way":
            o = Way()
            o._parse_nodes(elem)
        elif osmtype == "relation":
            o = Relation()
            o._parse_members(elem)
        else:
            pass
        o.attribs = elem.attrib
        o._parse_tags(elem)
        o._parse_bounds(elem)
        return o


class Node(OSMObject):

    def __init__(self):
        super().__init__()

    def _lon(self):
        return float(self.attribs.get('lon', 0))

    lon = property(_lon)

    def _lat(self):
        return float(self.attribs.get('lat', 0))        

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
        return self.attribs["id"] == other.attribs["id"]


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
    
