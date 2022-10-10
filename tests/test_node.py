from osmdiff import Node
from osmdiff.osm import OSMObject
from typing_extensions import assert_type


class TestNode:
    "tests for Node object"

    def test_init_node(self):
        "Test Node init"
        node = Node()
        assert_type(node, Node)
        assert_type(node, OSMObject)
        assert_type(node.attribs, dict)
        assert_type(node.tags, dict)
        assert len(node.attribs) == 0
        assert len(node.tags) == 0
        assert node.lat == 0.0
        assert node.lon == 0.0
