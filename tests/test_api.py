import unittest

from osmdiff.osm import Node, Way


class OverpassAPITests(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_fetch_node(self):
        node = Node(8925356223)
        node.fetch()
        self.assertIsNotNone(node)
        self.assertIsNotNone(node.tags)
        self.assertEqual(node.tags.get("name"), "10600 S @ 60 E")
        self.assertTrue(node.is_on_earth)

    def test_fetch_way(self):
        way = Way(651830456)
        way.fetch()
        self.assertIsNotNone(way)
        self.assertIsNotNone(way.tags)
        self.assertEqual(way.tags.get("name"), "10600 South")
        self.assertTrue(way.is_on_earth)
