from osmdiff.osm.member import ElementReference
from osmdiff.osm.osmobject import OSMElement


class Way(OSMElement):

    def __init__(self, id=None):
        self.nodes = []
        self.members = []
        super().__init__(id=id)

    def _parse_members(self, elem):
        for nd in elem.findall("nd"):
            ref = ElementReference(id=nd.attrib['ref'])
            self.members.append(ref)

    def _geo_interface(self):
        if not self.has_geometry:
            return None
        geom_type = 'LineString' if self.nodes[0] == self.nodes[-1] else 'Polygon'
        return {
            'type': geom_type,
            'coordinates': [
                [[n.lon, n.lat] for n in self.nodes]
            ]
        }
    
    __geo_interface__ = property(_geo_interface)

    def _closed(self):
        return self.members[0] == self.members[-1]

    closed = property(_closed)

    def _has_geometry(self):
        return len(self.nodes) == len(self.members) and all ([n.lat and n.lon for n in self.nodes])

    has_geometry = property(_has_geometry)
