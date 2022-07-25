from . import Node
from .base import OSMElement


class Way(OSMElement):
    def __init__(self, osm_id, nodes=None, tags=None, attributes=None, role=None):
        if nodes is None:
            nodes = []
        self._nodes = nodes
        super().__init__(osm_id=osm_id, tags=tags, attributes=attributes, role=role)

    def _get_nodes(self):
        return self._nodes

    def _set_nodes(self, nodes):
        for node in nodes:
            if isinstance(node, Node):
                self._nodes.append(node)

    nodes = property(_get_nodes, _set_nodes)

    def get_is_on_earth(self):
        return all([n.is_on_earth for n in self.nodes])

    is_on_earth = property(get_is_on_earth)

    def _geo_interface(self):
        # do not allow geo_interface when way has no geometry
        if not self.has_geometry:
            return None
        geom_type = "LineString" if self.nodes[0] == self.nodes[-1] else "Polygon"
        return {
            "type": geom_type,
            "coordinates": [[[n.lon, n.lat] for n in self.nodes]],
        }

    __geo_interface__ = property(_geo_interface)

    def _is_closed(self):
        return self._has_geometry and self.nodes[0] == self.nodes[-1]

    is_closed = property(_is_closed)

    def _has_geometry(self):
        for node in self._nodes:
            if not node.has_geometry:
                return False
        return True

    has_geometry = property(_has_geometry)

    def fetch(self):
        """Fetch the way data from Overpass"""
        # fixme DRY?
        import overpass
        overpass_api = overpass.API()
        overpass_response = overpass_api.get("way({id});(._;>;)".format(id=self.osm_id), responseformat="json")

        # Check if we have a non-empty reponse
        overpass_elements = overpass_response.get("elements")
        if overpass_elements is None or len(overpass_elements) == 0:
            # todo do something meaningful when an empty response is returned
            return

        nodes = [element for element in overpass_elements if element["type"] == "node"]
        ways = [element for element in overpass_elements if element["type"] == "way"]

        way_nodes = []

        way_dict = next(item for item in ways if item["id"] == self.osm_id)
        nodes = (item for item in nodes if item["id"] in way_dict["nodes"])

        self._tags = way_dict.get("tags")

        for node_dict in nodes:
            self._nodes.append(Node(
                osm_id=node_dict.get("id"),
                lon=node_dict.get("lon"),
                lat=node_dict.get("lat"),
                tags=node_dict.get("tags")
            ))
