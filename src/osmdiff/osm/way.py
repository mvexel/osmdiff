from osmdiff.osm.api.api import OverpassAPI
from osmdiff.osm.node import Node
from osmdiff.osm.osmobject import OSMObject


class Way(OSMObject):

    def __init__(self, id=None):
        self._nodes = []
        self._waynodes = []
        super().__init__(id=id)

    def retrieve_geometry(self):
        if self.has_geometry:
            return
        OverpassAPI.geometry_for(self)

    def _parse_waynodes(self, elem):
        for nd in elem.findall("nd"):
            way_node = WayNode()
            way_node.ref = nd.attrib["ref"]
            self._waynodes.append(way_node)

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
        return self._waynodes[0] == self._waynodes[-1]

    closed = property(_closed)

    def _has_geometry(self):
        return len(self._nodes) == len(self._waynodes) and all ([n.lat and n.lon for n in self._nodes])

    has_geometry = property(_has_geometry)

    def get_waynodes(self):
        return self._waynodes

    waynodes = property(get_waynodes)

    def get_nodes(self):
        return self._nodes

    nodes = property(get_nodes)


class WayNode(OSMObject):

    def __init__(self, id=None):
        self._ref = None
        super().__init__(id=id)

    def set_ref(self, ref):
        self._ref = ref

    def get_ref(self):
        return int(self._ref)

    ref = property(get_ref, set_ref)
    
    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, WayNode) and self.ref == __o.ref
