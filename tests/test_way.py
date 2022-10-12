from osmdiff import Way
from osmdiff.osm import OSMObject
from osmdiff.osm.osm import Node
from shapely.geometry import shape
from typing_extensions import assert_type


class TestWay:
    "tests for Way object"

    def test_init_way(self):
        "Test Way init"
        way = Way()
        assert_type(way, Way)
        assert_type(way, OSMObject)
        assert_type(way.attribs, dict)
        assert_type(way.tags, dict)
        assert len(way.tags) == 0
        assert len(way.attribs) == 0
        assert_type(way.nodes, list)
        assert len(way.nodes) == 0

    def test_geom_interface(self):
        n1 = Node((0.0, 0.0))
        n2 = Node((1.0, 0.0))
        n3 = Node((1.0, 1.0))
        n4 = Node((0.0, 1.0))
        w = Way((n1, n2, n3, n4))
        s = shape(w)
