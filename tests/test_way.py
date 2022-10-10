import unittest

from osmdiff import Way
from osmdiff.osm import OSMObject


class WayTests(unittest.TestCase):
    "tests for Way object"

    def test_init_way(self):
        "Test Way init"
        way = Way()
        self.assertIsInstance(way, Way)
        self.assertIsInstance(way, OSMObject)
        self.assertIsInstance(way.attribs, dict)
        self.assertIsInstance(way.tags, dict)
        self.assertEqual(len(way.tags), 0)
        self.assertEqual(len(way.attribs), 0)
        self.assertIsInstance(way.nodes, list)
        self.assertEqual(len(way.nodes), 0)


if __name__ == "__main__":
    unittest.main()
