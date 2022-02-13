from .osmobject import OSMObject


class Node(OSMObject):

    def __init__(self, lon=None, lat=None, id=None):
        self._lon = lon
        self._lat = lat
        super().__init__(id=id)

    def get_lon(self):
        return self._lon

    def set_lon(self, lon):
        self._lon = lon

    lon = property(get_lon, set_lon)

    def get_lat(self):
        return self._lat

    def set_lat(self, lat):
        self._lat = lat 
    
    lat = property(get_lat, set_lat)

    def get_geo_interface(self):
        return {
            'type': 'Point',
            'coordinates': [self.lon, self.lat]
        }

    __geo_interface__ = property(get_geo_interface)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.id == other.id