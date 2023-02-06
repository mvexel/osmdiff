import pytest
from osmdiff import Node
from osmdiff.osm import OSMObject
from shapely.geometry import shape
from typing_extensions import assert_type


class TestNode:
    "tests for Node object"

    def test_init_node(self):
        "Test Node init"
        node = Node((0.0, 0.0))
        assert_type(node, Node)
        assert_type(node, OSMObject)
        assert_type(node.attribs, dict)
        assert_type(node.tags, dict)
        assert len(node.attribs) == 0
        assert len(node.tags) == 0
        assert node.location == (0.0, 0.0)

        loc = (-113.5, 40.1)
        n2 = Node(loc)
        assert n2.location == loc

        loc = ("abc", "abc")
        with pytest.raises(TypeError):
            n3 = Node(loc)

    def test_node_repr(self):
        loc = (-113.5, 40.1)
        n1 = Node(loc)
        n1.attribs["id"] = 12345
        assert n1.__repr__() == "Node 12345"

    def test_geom_interface(self):
        n1 = Node((0.0, 0.0))
        s = shape(n1)
        assert (s.y, s.x) == n1.location
