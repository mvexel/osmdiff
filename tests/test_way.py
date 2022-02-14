from pathlib import Path
import unittest
from osmdiff.osm.way import Way, OSMElement

class WayTests(unittest.TestCase):
    "tests for Way object"

    def setUp(self) -> None:
        self.way_xml_file = Path(__file__).parent.joinpath('fixtures/way_clearcreek.xml')
        return super().setUp()

    def test_init_way(self):
        "Test Way init"
        way = Way()
        self.assertIsInstance(way, Way)
        self.assertIsInstance(way, OSMElement)
        self.assertIsInstance(way.attrib, dict)
        self.assertIsInstance(way.tags, dict)
        self.assertEqual(len(way.tags), 0)
        self.assertEqual(len(way.attrib), 0)
        self.assertIsInstance(way.nodes, list)
        self.assertEqual(len(way.nodes), 0)

    def test_way_from_xml(self):
        "Test read way from XML file"
        xml_str = open(self.way_xml_file).read()

        way = Way.from_xml(xml_str)
        self.assertIn('highway', way.tags)
        self.assertEqual(len(way.waynodes), 440)
        self.assertEqual(len(way.nodes), 0)
        self.assertFalse(way.closed)
        self.assertFalse(way.has_geometry)

        way.retrieve_geometry()
        self.assertTrue(way.has_geometry)
        self.assertEqual(len(way.waynodes), 440)
        self.assertEqual(len(way.nodes), 440)
        self.assertFalse(way.closed)

if __name__ == '__main__':
    unittest.main()
