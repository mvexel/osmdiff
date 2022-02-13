import unittest
from osmdiff.osm import API, Node, Way, Relation

class ApiTests(unittest.TestCase):

    def setUp(self) -> None:
        self.api = API()
        return super().setUp()

    def tearDown(self) -> None:
        del self.api
        return super().tearDown()

    def test_fetch_node(self):
        n_xml = self.api.fetch('node', 1000)
        node = Node.from_xml(n_xml)
        self.assertTrue(node.id == 1000)

    def test_fetch_way(self):
        w_xml = self.api.fetch('way', 1000)
        way = Way.from_xml(w_xml)
        self.assertTrue(way.id == 1000)

    def test_fetch_relation(self):
        r_xml = self.api.fetch('relation', 10000)
        relation = Relation.from_xml(r_xml)
        self.assertTrue(relation.id == 10000)