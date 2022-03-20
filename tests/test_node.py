from pathlib import Path
import unittest
from osmdiff import Node
from osmdiff.osm.osmobject import OSMElement

class NodeTests(unittest.TestCase):
    "tests for Node object"

    def setUp(self) -> None:
        self.node_xml_file = Path(__file__).parent.joinpath('fixtures/node_fremont.xml')
        return super().setUp()

    def test_init_node(self):
        "Test Node init"
        node = Node()
        self.assertIsInstance(node, Node)
        self.assertIsInstance(node, OSMElement)
        self.assertIsInstance(node._attrib, dict)
        self.assertIsInstance(node.tags, dict)
        self.assertEqual(len(node._attrib), 0)
        self.assertEqual(len(node.tags), 0)
        self.assertIsNone(node.lat)
        self.assertIsNone(node.lon)
        self.assertFalse(node.is_on_earth)

    def test_node_from_xml(self):
        "Test read node from XML file"
        xml_str = open(self.node_xml_file).read()
        node = Node.from_xml(xml_str)
        self.assertIn('name', node.tags)
        self.assertIn('tourism', node.tags)
        self.assertEqual(node.tags['name'], 'Fremont Indian Museum')
        self.assertEqual(node.tags['tourism'], 'museum')

    def test_node_geointerface(self):
        from shapely.geometry import shape
        node = Node(lon=0.0, lat=0.0, id=1)
        shp = shape(node)
        self.assertTrue(shp.geom_type == 'Point')
        self.assertTrue(list(shp.coords) == [(node.lon, node.lat)])

if __name__ == '__main__':
    unittest.main()
