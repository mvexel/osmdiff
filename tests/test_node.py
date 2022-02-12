from pathlib import Path
import unittest
from xml.etree import ElementTree
from osmdiff import Node
from osmdiff.osm import OSMObject

class NodeTests(unittest.TestCase):
    "tests for Node object"

    def setUp(self) -> None:
        self.node_xml_file = Path(__file__).parent.joinpath('fixtures/node_fremont.xml')
        return super().setUp()

    def test_init_node(self):
        "Test Node init"
        node = Node()
        self.assertIsInstance(node, Node)
        self.assertIsInstance(node, OSMObject)
        self.assertIsInstance(node.attribs, dict)
        self.assertIsInstance(node.tags, dict)
        self.assertEqual(len(node.attribs), 0)
        self.assertEqual(len(node.tags), 0)
        self.assertEqual(node.lat, 0.0)
        self.assertEqual(node.lon, 0.0)

    def test_node_from_xml(self):
        "Test read node from XML file"
        root_elem = ElementTree.parse(self.node_xml_file).getroot()
        node = Node.from_xml(root_elem)
        self.assertIn('name', node.tags)
        self.assertIn('tourism', node.tags)
        self.assertEqual(node.tags['name'], 'Fremont Indian Museum')
        self.assertEqual(node.tags['tourism'], 'museum')


if __name__ == '__main__':
    unittest.main()
