import unittest
from osmdiff.osm import OSMObject, Relation


class RelationTests(unittest.TestCase):
    "tests for Relation object"

    def test_init_relation(self):
        "Test Relation init"
        relation = Relation()
        self.assertIsInstance(relation, Relation)
        self.assertIsInstance(relation, OSMObject)
        self.assertIsInstance(relation._attrib, dict)
        self.assertIsInstance(relation.tags, dict)
        self.assertEqual(len(relation.tags), 0)
        self.assertEqual(len(relation._attrib), 0)
        self.assertIsInstance(relation.members, list)
        self.assertEqual(len(relation.members), 0)


if __name__ == '__main__':
    unittest.main()
