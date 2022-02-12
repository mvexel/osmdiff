import unittest
from osmdiff import Node
from osmdiff.osm import OSMObject

class NodeTests(unittest.TestCase):
    "tests for Node object"

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


if __name__ == '__main__':
    unittest.main()
