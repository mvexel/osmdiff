from pathlib import Path
import unittest
from xml.etree import ElementTree
from osmdiff import Way
from osmdiff.osm import OSMObject

class WayTests(unittest.TestCase):
    "tests for Way object"

    def setUp(self) -> None:
        self.way_xml_file = Path(__file__).parent.joinpath('fixtures/way_clearcreek.xml')
        return super().setUp()

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

    def test_way_from_xml(self):
        "Test read way from XML file"
        root_elem = ElementTree.parse(self.way_xml_file).getroot()
        way = Way.from_xml(root_elem)
        self.assertIn('highway', way.tags)
        self.assertEqual(len(way.nodes), 440)
        self.assertFalse(way.closed)

if __name__ == '__main__':
    unittest.main()
