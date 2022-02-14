from osmdiff.osm.osmobject import OSMElement


class Relation(OSMElement):

    def __init__(self, id=None):
        self._members = []
        self._elements = []
        super().__init__(id=id)

    def _parse_members(self, elem):
        for member in elem.findall("member"):
            self.members.append(OSMElement.from_xml(member))

    def fetch_elements(self):
        for member in self.members:
            self._elements.append(member.fetch_element())

    def get_members(self):
        return self._members

    members = property(get_members)

    def get_elements(self):
        return self._elements

    def set_elements(self, elements):
        self._elements = elements

    elements = property(get_elements, set_elements)

    def _geo_interface(self):
        return {
            'type': 'FeatureCollection',
            'Features': [
                [f.__geo_interface__ for f in self.members]
            ]
        }

    __geo_interface__ = property(_geo_interface)
