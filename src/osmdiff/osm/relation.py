from .base import OSMElement
from .node import Node
from .way import Way


class Relation(OSMElement):
    def __init__(self, osm_id, members=None, tags=None, role=None):
        if members is None:
            members = []
        self._members = members
        self._is_complete = False
        super().__init__(osm_id=osm_id, tags=tags, role=role)

    def get_members(self):
        return self._members

    def set_members(self, members):
        for member in members:
            # only allow OSMElement as members
            if isinstance(member, OSMElement):
                self._members.append(member)

    members = property(get_members, set_members)

    def get_has_geometry(self):
        for member in self._members:
            if not member.has_geometry:
                return False
        return True

    has_geometry = property(get_has_geometry)

    def get_is_complete(self):
        return self._is_complete

    is_complete = property(get_is_complete)

    def get_is_on_earth(self):
        return all([n.is_on_earth for n in self.members])

    is_on_earth = property(get_is_on_earth)

    def _geo_interface(self):
        return {
            "type": "FeatureCollection",
            "Features": [[f.__geo_interface__ for f in self.members]],
        }

    def fetch(self):
        """Fetch the relation data from Overpass"""
        # fixme DRY?
        import overpass
        overpass_api = overpass.API()
        overpass_response = overpass_api.get("rel({id});(._;>;)".format(id=self.osm_id), responseformat="json")

        # Check if we have a non-empty response
        overpass_elements = overpass_response.get("elements")
        if overpass_elements is None or len(overpass_elements) == 0:
            # todo do something meaningful when an empty response is returned
            return

        nodes = [element for element in overpass_elements if element["type"] == "node"]
        ways = [element for element in overpass_elements if element["type"] == "way"]
        relations = [element for element in overpass_elements if element["type"] == "relation"]

        relation_dict = next(item for item in relations if item["id"] == self.osm_id)

        self._tags = relation_dict.get("tags")

        # Parse members
        for member in relation_dict.get("members"):
            if member["type"] == "node":
                member_node_dict = next(item for item in nodes if item["id"] == member["ref"])
                self._members.append(Node(
                    osm_id=member_node_dict.get("id"),
                    lon=member_node_dict.get("lon"),
                    lat=member_node_dict.get("lat"),
                    tags=member_node_dict.get("tags"),
                    role=member_node_dict.get("role")
                ))
            elif member["type"] == "way":
                member_way_dict = next(item for item in ways if item["id"] == member["ref"])
                member_way = Way(
                    osm_id=member_way_dict.get("id"),
                    tags=member_way_dict.get("tags"),
                    role=member_way_dict.get("role")
                )

                for node_dict in nodes:
                    member_way.nodes.append(Node(
                        osm_id=node_dict.get("id"),
                        lon=node_dict.get("lon"),
                        lat=node_dict.get("lat")))

            elif member["type"] == "relation":
                # todo implement full support for nested relations.
                # currently we only build a skeleton relation object
                member_rel_dict = next(item for item in relations if item["id"] == member["ref"])
                self._members.append(Relation(
                    osm_id=member_rel_dict.get("id"),
                    role=member_rel_dict.get("role"),
                    tags=member_rel_dict.get("tags")
                ))

    __geo_interface__ = property(_geo_interface)
