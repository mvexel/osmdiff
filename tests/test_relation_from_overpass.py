import unittest
import osmdiff

class Relation_From_Overpass(unittest.TestCase):

    def setUp(self) -> None:
        self.relation_id = 1744366
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_fetch_relation(self):

        relation = osmdiff.osm.OverpassAPI.fetch_relation(self.relation_id)