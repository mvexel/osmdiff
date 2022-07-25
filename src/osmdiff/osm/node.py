from .base import OSMElement


class Node(OSMElement):
    def __init__(self, osm_id, lon=None, lat=None, tags=None, role=None):
        self._lon = lon
        self._lat = lat
        self._role = role
        super().__init__(osm_id=osm_id, tags=tags, role=role)

    def get_lon(self):
        return self._lon

    def set_lon(self, lon):
        self._lon = float(lon)

    lon = property(get_lon, set_lon)

    def get_lat(self):
        return self._lat

    def set_lat(self, lat):
        self._lat = float(lat)

    lat = property(get_lat, set_lat)

    def get_has_geometry(self):
        return self.lat is not None and self.lon is not None

    has_geometry = property(get_has_geometry)

    def get_is_on_earth(self):
        return (
                self.has_geometry
                and 90.0 > self.lat > -90.0
                and 180.0 > self.lon > -180.0
        )

    is_on_earth = property(get_is_on_earth)

    def get_geo_interface(self):
        return {"type": "Point", "coordinates": [self.lon, self.lat]}

    __geo_interface__ = property(get_geo_interface)

    def fetch(self):
        """Fetch the node data from Overpass"""
        # fixme DRY?
        import overpass
        overpass_api = overpass.API()
        overpass_response = overpass_api.get("node({id})".format(id=self.osm_id), responseformat="json")

        # Check if we have a non-empty reponse
        overpass_elements = overpass_response.get("elements")
        if overpass_elements is None or len(overpass_elements) == 0:
            # todo do something meaningful when an empty response is returned
            return

        node = next(element for element in overpass_elements if int(element["id"]) == self.osm_id)
        self._lon = node.get("lon")
        self._lat = node.get("lat")
        self._tags = node.get("tags")

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.osm_id == other.osm_id
