from osmdiff.osm.osmobject import OSMElement


class Relation(OSMElement):

    def __init__(self, id=None):
        self.members = []
        self.elements = []
        super().__init__(id=id)

    def _parse_members(self, elem):
        for member in elem.findall("member"):
            self.members.append(OSMElement.from_xml(member))

    def _geo_interface(self):
        return {
            'type': 'FeatureCollection',
            'Features': [
                [f.__geo_interface__ for f in self.members]
            ]
        }

    __geo_interface__ = property(_geo_interface)
