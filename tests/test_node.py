from osmdiff import Node
from osmdiff.osm import OSMObject
from typing_extensions import assert_type


def test_node_init():
    node = Node()
    assert isinstance(node, Node)
    assert isinstance(node, OSMObject)
    assert isinstance(node.attribs, dict)
    assert isinstance(node.tags, dict)
    assert len(node.attribs) == 0
    assert len(node.tags) == 0
    assert node.lat == 0.0
    assert node.lon == 0.0

def test_node_geo_interface_and_equality():
    node1 = Node(attribs={"lat": 10.0, "lon": 20.0})
    node2 = Node(attribs={"lat": 10.0, "lon": 20.0})
    node3 = Node(attribs={"lat": 10.1, "lon": 20.1})
    gi = node1.__geo_interface__
    assert gi["type"] == "Point"
    assert gi["coordinates"] == [node1.lon, node1.lat]
    assert node1 == node2
    assert node1 != node3

def test_node_from_xml():
    import xml.etree.ElementTree as ET
    xml = '<node id="1" lat="10.0" lon="20.0"><tag k="name" v="TestNode"/></node>'
    elem = ET.fromstring(xml)
    node = Node.from_xml(elem)
    assert isinstance(node, Node)
    assert node.attribs["id"] == "1"
    assert node.attribs["lat"] == "10.0"
    assert node.tags["name"] == "TestNode"
