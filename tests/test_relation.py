from osmdiff import Relation
from osmdiff.osm import OSMObject
from typing_extensions import assert_type


def test_relation_init():
    relation = Relation()
    assert isinstance(relation, Relation)
    assert isinstance(relation, OSMObject)
    assert isinstance(relation.attribs, dict)
    assert isinstance(relation.tags, dict)
    assert len(relation.tags) == 0
    assert len(relation.attribs) == 0
    assert isinstance(relation.members, list)
    assert len(relation.members) == 0

def test_relation_from_xml():
    import xml.etree.ElementTree as ET
    xml = '<relation id="1"><member type="way" ref="1" role="outer"/><tag k="type" v="multipolygon"/></relation>'
    elem = ET.fromstring(xml)
    relation = Relation.from_xml(elem)
    assert isinstance(relation, Relation)
    assert relation.attribs["id"] == "1"
    assert relation.tags["type"] == "multipolygon"
    assert len(relation.members) == 1

# Optionally, add test for geo interface if implemented
