class OSMObject:
    def __init__(self) -> None:
        self.tags = {}
        self.attribs = {}
        self.bounds = None

    def _id(self):
        return self.attribs.get("id", 0)

    id = property(_id, doc="Returns the OSM identifer, or 0 if not set")

    def __repr__(self) -> str:
        out = "{type} {id}".format(type=type(self).__name__, id=self.id)
        if type(self) == Way:
            out += " ({ways} nodes)".format(ways=len(self.nodes))
        if type(self) == Relation:
            out += " ({mem} members)".format(mem=len(self.members))
        return out

    def _parse_tags(self, elem) -> None:
        for tagelem in elem.findall("tag"):
            self.tags[tagelem.attrib["k"]] = tagelem.attrib["v"]

    def _parse_bounds(self, elem) -> None:
        be = elem.find("bounds")
        if be is not None:
            self.bounds = [
                be.attrib["minlon"],
                be.attrib["minlat"],
                be.attrib["maxlon"],
                be.attrib["maxlat"],
            ]

    @classmethod
    def from_xml(cls, elem):
        osmtype = ""
        if elem.tag == "member":
            osmtype = elem.attrib["type"]
        else:
            osmtype = elem.tag
        if osmtype == "node" or osmtype == "nd":
            if ("lon", "lat") in elem.attrib:
                o = Node((float(elem.attrib.get("lon")), float(elem.attrib.get("lat"))))
            else:
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
    def __init__(self, location: tuple[float | None, float | None] | None = None):
        super().__init__()
        self._location = location

    def _location(self):
        return self._location

    location = property(_location)

    @property
    def __geo_interface__(self):
        return {"type": "Point", "coordinates": self.location}

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        if self.id == 0 or other.id == 0:
            return False
        return self.id == other.id


class Way(OSMObject):
    def __init__(self, nodes: tuple[Node] | None = None) -> None:
        self.nodes = list(nodes) if nodes else []
        super().__init__()

    def _parse_nodes(self, elem):
        for node in elem.findall("nd"):
            self.nodes.append(OSMObject.from_xml(node))

    def _is_area(self) -> bool:
        return self.nodes[0].location == self.nodes[-1].location

    is_area = property(_is_area)

    @property
    def __geo_interface__(self):
        geom_type = "Polygon" if self.is_area else "Linestring"
        return {
            "type": geom_type,
            "coordinates": tuple([(n.lon, n.lat) for n in self.nodes]),
        }


class Relation(OSMObject):
    def __init__(self):
        self.members = []
        super().__init__()

    def _parse_members(self, elem):
        for member in elem.findall("member"):
            self.members.append(OSMObject.from_xml(member))

    def _geo_interface(self):
        return {
            "type": "FeatureCollection",
            "Features": (tuple([f.__geo_interface__ for f in self.members])),
        }

    __geo_interface__ = property(_geo_interface)
