from osmdiff import Way
from osmdiff.osm import OSMObject
from osmdiff.osm.osm import Node
from shapely.geometry import shape
from typing_extensions import assert_type
from pytest import raises


class TestWay:
    "tests for Way object"

    def test_init_way(self):
        "Test initializion of a valid Way"
        way = Way()
        assert_type(way, Way)
        assert_type(way, OSMObject)
        assert_type(way.attribs, dict)
        assert_type(way.tags, dict)
        assert len(way.tags) == 0
        assert len(way.attribs) == 0
        assert_type(way.nodes, list)
        assert len(way.nodes) == 0

    def test_geom_interface(test_nodes):
        w = Way(test_nodes.square())
        assert w.has_geometry
        assert shape(w)
        assert list(shape(w).coords) == [n.location for n in w.nodes]
        w = Way(test_nodes.square())
        assert not w.has_geometry
