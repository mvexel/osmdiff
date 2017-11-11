"osmdiff test classes"
import unittest
from osmdiff import OSMChange


class OSMChangeTestCase(unittest.TestCase):
    "tests for OSMChange object"

    def test_1_initialization(self):
        "Test successful initiaization"
        osm_change = OSMChange()
        self.assertIsInstance(osm_change, OSMChange)

    def test_2_sequencenumber(self):
        "Sequence number is not defined by default but can be set manually"
        osm_change = OSMChange()
        self.assertIsNone(osm_change.sequence_number)
        osm_change.sequence_number = 12345
        self.assertEqual(osm_change.sequence_number, 12345)
        # osm_change.sequence_number = "12345"
        # self.assertEqual(osm_change.sequence_number, 12345)

    def test_3_readfromfile(self):
        "Test initializing from file"
        pass

    def test_4_state(self):
        "Test getting state (requires internet)"
        osm_change = OSMChange()
        self.assertTrue(osm_change.get_state())
        self.assertIsInstance(osm_change.sequence_number, int)

if __name__ == '__main__':
    unittest.main()
