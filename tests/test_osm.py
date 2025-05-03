import pytest
from osmdiff.osm.osm import OSMObject, Way, Relation, Node

def test_osmobject_init_defaults():
    obj = OSMObject()
    assert obj.tags == {}
    assert obj.attribs == {}
    assert obj.bounds is None

def test_osmobject_init_with_values():
    tags = {"amenity": "cafe"}
    attribs = {"id": "123", "version": "1"}
    bounds = [0.0, 1.0, 2.0, 3.0]
    obj = OSMObject(tags=tags, attribs=attribs, bounds=bounds)
    assert obj.tags == tags
    assert obj.attribs == attribs
    assert obj.bounds == bounds

def test_osmobject_repr():
    obj = OSMObject(attribs={"id": "42"})
    assert "OSMObject 42" in repr(obj)

import xml.etree.ElementTree as ET
import tempfile
import os

def test_osmobject_parse_tags_and_bounds():
    xml = '''<node id="1" lat="10.0" lon="20.0"><tag k="amenity" v="cafe"/><bounds minlon="0" minlat="1" maxlon="2" maxlat="3"/></node>'''
    elem = ET.fromstring(xml)
    obj = OSMObject()
    obj._parse_tags(elem)
    assert obj.tags["amenity"] == "cafe"
    obj._parse_bounds(elem)
    assert obj.bounds == ["0", "1", "2", "3"]

def test_osmobject_to_dict_and_json():
    obj = OSMObject(tags={"foo": "bar"}, attribs={"id": "1"}, bounds=[0,1,2,3])
    d = obj.to_dict()
    assert d["tags"] == {"foo": "bar"}
    assert d["id"] == "1"
    assert d["bounds"] == [0,1,2,3]
    j = obj.to_json()
    assert '"foo": "bar"' in j

def test_osmobject_from_file(tmp_path):
    xml = '<node id="1" lat="10.0" lon="20.0"/>'
    file_path = tmp_path / "test.xml"
    file_path.write_text(xml)
    obj = OSMObject.from_file(str(file_path))
    assert isinstance(obj, OSMObject)
    assert obj.attribs["id"] == "1"

def test_osmobject_init_with_values():
    tags = {"amenity": "cafe"}
    attribs = {"id": "123", "version": "1"}
    bounds = [0.0, 1.0, 2.0, 3.0]
    obj = OSMObject(tags=tags, attribs=attribs, bounds=bounds)
    assert obj.tags == tags
    assert obj.attribs == attribs
    assert obj.bounds == bounds

def test_osmobject_repr():
    obj = OSMObject(attribs={"id": "42"})
    assert "OSMObject 42" in repr(obj)
    way = Way(attribs={"id": "99"})
    way.nodes = [1, 2, 3]
    assert "Way 99 (3 nodes)" in repr(way)
    rel = Relation(attribs={"id": "7"})
    rel.members = [1, 2]
    assert "Relation 7 (2 members)" in repr(rel)

def test_way_is_closed():
    way = Way()
    way.nodes = [1, 2, 1]
    assert way.is_closed() is True
    way.nodes = [1, 2, 3]
    assert way.is_closed() is False

def test_node_geo_interface_and_equality():
    node1 = Node(attribs={"lat": 10.0, "lon": 20.0})
    node2 = Node(attribs={"lat": 10.0, "lon": 20.0})
    node3 = Node(attribs={"lat": 10.1, "lon": 20.1})
    # __geo_interface__ property
    gi = node1.__geo_interface__
    assert gi["type"] == "Point"
    assert gi["coordinates"] == [node1.lon, node1.lat]
    # __eq__
    assert node1 == node2
    assert node1 != node3


def test_way_init_defaults():
    way = Way()
    assert way.tags == {}
    assert way.attribs == {}
    assert way.bounds is None
    assert way.nodes == []


def test_way_init_with_values():
    tags = {"amenity": "cafe"}
    attribs = {"id": "123", "version": "1"}
    bounds = [0.0, 1.0, 2.0, 3.0]
    nodes = ["1", "2", "3"]
    way = Way(tags=tags, attribs=attribs, bounds=bounds)
    way.nodes = nodes
    assert way.tags == tags
    assert way.attribs == attribs
    assert way.bounds == bounds
    assert way.nodes == nodes


def test_relation_init_defaults():
    relation = Relation()
    assert relation.tags == {}
    assert relation.attribs == {}
    assert relation.bounds is None
    assert relation.members == []
    
def test_relation_init_with_values():
    tags = {"amenity": "cafe"}
    attribs = {"id": "123", "version": "1"}
    bounds = [0.0, 1.0, 2.0, 3.0]
    members = ["1", "2", "3"]
    relation = Relation(tags=tags, attribs=attribs, bounds=bounds)
    relation.members = members
    assert relation.tags == tags
    assert relation.attribs == attribs
    assert relation.bounds == bounds
    assert relation.members == members
    