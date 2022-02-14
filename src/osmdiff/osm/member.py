from osmdiff.osm.api.api import OSMAPI
from osmdiff.osm.osmobject import OSMElement


class ElementReference(OSMElement):

    def __init__(self, id=None, osmtype=None):
        self._osmtype = osmtype
        super().__init__(id=id)

    def fetch_element(self):
        return OSMElement.from_xml(OSMAPI.fetch(self.osmtype, self.id))
    
    def get_osmtype(self):
        return self._osmtype

    def set_osmtype(self, osmtype):
        self._osmtype = osmtype

    osmtype = property(get_osmtype, set_osmtype)

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, ElementReference) and self.ref == __o.ref and self.osmtype == __o.osmtype
