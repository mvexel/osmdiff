from platform import node
import unittest
from osmdiff import OSMChange, Node, Way, Relation

class OSMChangeTests(unittest.TestCase):
    "tests for OSMChange object"

    def setUp(self):
        self.osmchange_file_path = '/home/mvexel/dev/osmdiff/tests/fixtures/test_osmchange.xml'

    def tearDown(self):
        pass

    def test_init_osmchange(self):
        "Test OSMChange init"
        osmchange = OSMChange()
        self.assertIsInstance(osmchange, OSMChange)
        self.assertIsInstance(osmchange.create, list)
        self.assertIsInstance(osmchange.modify, list)
        self.assertIsInstance(osmchange.delete, list)
        self.assertEqual(len(osmchange.create), 0)
        self.assertEqual(len(osmchange.modify), 0)
        self.assertEqual(len(osmchange.delete), 0)


    def test_set_sequencenumber(self):
        "Sequence number is not defined by default but can be set manually"
        osm_change = OSMChange()
        self.assertIsNone(osm_change.sequence_number)
        osm_change.sequence_number = 12345
        self.assertEqual(osm_change.sequence_number, 12345)
        osm_change.sequence_number = "12345"
        self.assertEqual(osm_change.sequence_number, 12345)

    def test_3_readfromfile(self):
        "Test initializing from file"
        xml_str = open(self.osmchange_file_path).read()
        osmchange = OSMChange.from_xml(xml_str)
        self.assertEqual(len(osmchange.create), 831)
        self.assertEqual(len(osmchange.modify), 368)
        self.assertEqual(len(osmchange.delete), 3552)
        nodes_created = [o for o in osmchange.create if isinstance(o, Node)]
        ways_created = [o for o in osmchange.create if isinstance(o, Way)]
        rels_created = [o for o in osmchange.create if isinstance(o, Relation)]
        self.assertEqual(len(nodes_created), 699)
        self.assertEqual(len(ways_created), 132)
        self.assertEqual(len(rels_created), 0)
        self.assertEqual(len(nodes_created + ways_created + rels_created), len(osmchange.create))

    def test_4_state(self):
        "Test getting state (requires internet)"
        osm_change = OSMChange()
        self.assertTrue(osm_change.get_state())
        self.assertIsInstance(osm_change._sequence_number, int)

if __name__ == '__main__':
    unittest.main()
