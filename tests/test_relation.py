import unittest
from pathlib import Path

from osmdiff.osm import OSMElement, Relation, OSMAPI


class RelationTests(unittest.TestCase):
    "tests for Relation object"

    def setUp(self) -> None:
        self.rel_xml_file = Path(__file__).parent.joinpath('fixtures/rel_fishlake.xml')
        return super().setUp()

    def tearDown(self) -> None:
        pass

    def test_init_relation(self):
        """Test Relation init"""
        relation = Relation(1)
        self.assertIsInstance(relation, Relation)
        self.assertIsInstance(relation, OSMElement)
        self.assertIsInstance(relation.attributes, dict)
        self.assertIsInstance(relation.tags, dict)
        self.assertEqual(len(relation.tags), 0)
        self.assertEqual(len(relation.attributes), 0)
        self.assertIsInstance(relation.members, list)
        self.assertEqual(len(relation.members), 0)

    def test_relation_from_xml(self):
        "Test read relation from XML file"
        with open(self.rel_xml_file, "r") as fh:
            xml_str = fh.read()
            relation = OSMAPI.from_xml(xml_str)
            self.assertIn('name', relation.tags)
            self.assertIn('leisure', relation.tags)
            self.assertEqual(relation.tags['name'], 'Fishlake National Forest')
            self.assertEqual(relation.tags['leisure'], 'nature_reserve')
            self.assertTrue(relation.has_geometry)
            self.assertTrue(relation.is_on_earth)

    # def test_node_geointerface(self):
    #     from shapely.geometry import shape
    #     node = Node(lon=0.0, lat=0.0, id=1)
    #     self.assertTrue(node.has_geometry)
    #     self.assertTrue(node.is_on_earth)
    #     shp = shape(node)
    #     self.assertTrue(shp.geom_type == 'Point')
    #     self.assertTrue(list(shp.coords) == [(node.lon, node.lat)])


if __name__ == '__main__':
    unittest.main()
