from osmdiff.osm.osmobject import OSMObject


class Relation(OSMObject):

    def __init__(self, id=None):
        self.members = []
        super().__init__(id=id)

    def _parse_members(self, elem):
        for member in elem.findall("member"):
            self.members.append(OSMObject.from_xml(member))

    def _geo_interface(self):
        return {
            'type': 'FeatureCollection',
            'Features': [
                [f.__geo_interface__ for f in self.members]
            ]
        }

    __geo_interface__ = property(_geo_interface)
    

class Member(OSMObject):

    def __init__(self, id=None):
        super().__init__(id=id)

    def get_type(self):
        return self._attrib["type"]
    
    type = property(get_type)
