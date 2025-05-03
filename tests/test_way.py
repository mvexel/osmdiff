from osmdiff import Way
from osmdiff.osm import OSMObject
from typing_extensions import assert_type


def test_way_init():
    way = Way()
    assert isinstance(way, Way)
    assert isinstance(way, OSMObject)
    assert isinstance(way.attribs, dict)
    assert isinstance(way.tags, dict)
    assert len(way.tags) == 0
    assert len(way.attribs) == 0
    assert isinstance(way.nodes, list)
    assert len(way.nodes) == 0

def test_way_is_closed():
    way = Way()
    way.nodes = [1, 2, 1]
    assert way.is_closed() is True
    way.nodes = [1, 2, 3]
    assert way.is_closed() is False

def test_way_from_xml():
    import xml.etree.ElementTree as ET
    xml = '<way id="1"><nd ref="1"/><nd ref="2"/><tag k="highway" v="residential"/></way>'
    elem = ET.fromstring(xml)
    way = Way.from_xml(elem)
    assert isinstance(way, Way)
    assert way.attribs["id"] == "1"
    assert way.tags["highway"] == "residential"

# Optionally, add test for geo interface if implemented
