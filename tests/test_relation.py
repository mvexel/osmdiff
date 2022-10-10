from osmdiff import Relation
from osmdiff.osm import OSMObject
from typing_extensions import assert_type


class TestRelation:
    "tests for Relation object"

    def test_init_relation(self):
        "Test Relation init"
        relation = Relation()
        assert_type(relation, Relation)
        assert_type(relation, OSMObject)
        assert_type(relation.attribs, dict)
        assert_type(relation.tags, dict)
        assert len(relation.tags) == 0
        assert len(relation.attribs) == 0
        assert_type(relation.members, list)
        assert len(relation.members) == 0
