import unittest
from pathlib import Path

from osmdiff.osm import Way, OSMElement, OSMAPI


class WayTests(unittest.TestCase):
    "tests for Way object"

    def setUp(self) -> None:
        self.way_xml_file = Path(__file__).parent.joinpath(
            "fixtures/way_clearcreek.xml"
        )
        return super().setUp()

    def tearDown(self) -> None:
        pass

    def test_init_way(self):
        """Test Way init"""
        way = Way(1)
        self.assertIsInstance(way, Way)
        self.assertIsInstance(way, OSMElement)
        self.assertIsInstance(way.attributes, dict)
        self.assertIsInstance(way.tags, dict)
        self.assertEqual(len(way.tags), 0)
        self.assertEqual(len(way.attributes), 0)
        self.assertIsInstance(way.nodes, list)
        self.assertEqual(len(way.nodes), 0)

    def test_way_from_xml(self):
        """Test read way from XML file"""
        with open(self.way_xml_file, "r") as fh:
            xml_str = fh.read()
            way = OSMAPI.from_xml(xml_str)
            self.assertIn("highway", way.tags)
            self.assertEqual(len(way.nodes), 440)
            self.assertFalse(way.is_closed)
            self.assertFalse(way.has_geometry)
            self.assertEqual(len(way.nodes), 440)
            self.assertFalse(way.is_closed)


if __name__ == "__main__":
    unittest.main()
