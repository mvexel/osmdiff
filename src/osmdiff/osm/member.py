from osmdiff.osm.osmobject import OSMElement


class ElementReference(OSMElement):

    def __init__(self, id=None, osmtype=None, role=None):
        self.osmtype = osmtype
        self.role = role
        super().__init__(id=id)
    
    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, ElementReference) and self.ref == __o.ref and self.osmtype == __o.osmtype
