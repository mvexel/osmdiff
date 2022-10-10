from osmdiff import Way
from osmdiff.osm import OSMObject
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
