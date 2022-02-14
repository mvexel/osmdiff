from osmdiff.osm.api.api import OverpassAPI
from osmdiff.osm.member import ElementReference
from osmdiff.osm.node import Node
from osmdiff.osm.osmobject import OSMElement


class Way(OSMElement):

    def __init__(self, id=None):
        self._nodes = []
        self._elementreferences = []
        super().__init__(id=id)

    def retrieve_geometry(self):
        if self.has_geometry:
            return
        OverpassAPI.geometry_for_way(self)

    def _parse_elementreferences(self, elem):
        for nd in elem.findall("nd"):
            ref = ElementReference(id=nd.attrib['ref'])
            self._elementreferences.append(ref)

    def _geo_interface(self):
        if not self.has_geometry:
            return None
        geom_type = 'LineString' if self._nodes[0] == self._nodes[-1] else 'Polygon'
        return {
            'type': geom_type,
            'coordinates': [
                [[n.lon, n.lat] for n in self._nodes]
            ]
        }
    
    __geo_interface__ = property(_geo_interface)

    def _closed(self):
        return self._elementreferences[0] == self._elementreferences[-1]

    closed = property(_closed)

    def _has_geometry(self):
        return len(self._nodes) == len(self._elementreferences) and all ([n.lat and n.lon for n in self._nodes])

    has_geometry = property(_has_geometry)

    def get_elementreferences(self):
        return self._elementreferences

    element_references = property(get_elementreferences)

    def get_nodes(self):
        return self._nodes

    nodes = property(get_nodes)
