from xml.etree import ElementTree

import osmdiff


def _compute_bounds():
    # todo implement compute bounds function
    return [0.0, 0.0], [1.0, 1.0]


class OSMElement(object):
    def __init__(self, osm_id, tags=None, attributes=None, role=None):
        if attributes is None:
            attributes = {}
        if tags is None:
            tags = {}
        self._attributes = attributes
        self._tags = tags
        self._id = osm_id
        self._bounds = None
        self._role = role
        self._has_geometry = False

    def get_id(self):
        return self._id

    osm_id = property(get_id)

    def _get_role(self):
        return self._role

    def _set_role(self, role):
        self._role = role

    role = property(_get_role, _set_role)

    def _get_bounds(self):
        return _compute_bounds()

    bounds = property(_get_bounds)

    def _get_attributes(self):
        return self._attributes

    def _set_attributes(self, attributes):
        self._attributes = attributes

    attributes = property(_get_attributes, _set_attributes)

    def _get_tags(self):
        return self._tags

    def _set_tags(self, tags):
        self._tags = tags

    tags = property(_get_tags, _set_tags)

    def fetch(self):
        pass

    @staticmethod
    def from_xml(xml):
        from osmdiff.osm import Node, Way, Relation
        if isinstance(xml, ElementTree.Element):
            root = xml
        else:
            root = ElementTree.ElementTree(ElementTree.fromstring(xml)).getroot()
        if root.tag == "osm":
            elem = root[0]
        else:
            elem = root
        if elem.tag == "node":
            o = Node(
                lon=float(elem.attrib["lon"]),
                lat=float(elem.attrib["lat"]),
                osm_id=int(elem.attrib["id"]),
            )
        elif elem.tag == "nd":
            o = Node(osm_id=int(elem.attrib["ref"]))
        elif elem.tag == "way":
            o = Way(osm_id=int(elem.attrib["id"]))
            for nd in elem.findall("nd"):
                o.nodes.append(Node(osm_id=nd.attrib.get("id")))
        elif elem.tag == "relation":
            o = Relation(osm_id=int(elem.attrib["id"]))
            # parse members
            for member in elem.findall("member"):
                role = member.attrib.get("role")
                osm_type = member.attrib.get("type")
                osm_id = member.attrib.get("ref")
                if osm_type == "node":
                    o.members.append(Node(osm_id=osm_id, role=role))
                elif osm_type == "way":
                    o.members.append(Way(osm_id=osm_id, role=role))
                elif osm_type == "relation":
                    o.members.append(Relation(osm_id=osm_id, role=role))
        for tag_element in elem.findall("tag"):
            o.tags[tag_element.attrib["k"]] = tag_element.attrib["v"]
        o.attributes = elem.attrib

        return o

    def __repr__(self):
        out = "{type} {id}".format(type=type(self).__name__, id=self.osm_id)
        if type(self) == osmdiff.osm.Way:
            out += " ({ways} nodes)".format(ways=len(self.nodes))
        if type(self) == osmdiff.osm.Relation:
            out += " ({mem} members)".format(mem=len(self.members))
        return out
