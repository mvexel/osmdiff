import unittest
from osmdiff.osm.api import OSMAPI, OverpassAPI
from osmdiff.osm import Node, Way, Relation

class OSMAPITests(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_fetch_node(self):
        n_xml = OSMAPI.fetch('node', 1000)
        node = Node.from_xml(n_xml)
        self.assertTrue(node.id == 1000)

    def test_fetch_way(self):
        w_xml = OSMAPI.fetch('way', 1000)
        way = Way.from_xml(w_xml)
        self.assertTrue(way.id == 1000)

    def test_fetch_relation(self):
        r_xml = OSMAPI.fetch('relation', 10000)
        relation = Relation.from_xml(r_xml)
        self.assertTrue(relation.id == 10000)

        relation.fetch_elements()
        self.assertEqual(len(relation.elements), len(relation.members))


class OverpassAPITests(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

