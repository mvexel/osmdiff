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
    def from_xml(cls, elem):
        osmtype = ""
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


class Way(OSMObject):

    def __init__(self):
        self.nodes = []
        super().__init__()

    def _parse_nodes(self, elem):
        for node in elem.findall("nd"):
            self.nodes.append(OSMObject.from_xml(node))


class Relation(OSMObject):

    def __init__(self):
        self.members = []
        super().__init__()

    def _parse_members(self, elem):
        for member in elem.findall("member"):
            self.members.append(OSMObject.from_xml(member))
