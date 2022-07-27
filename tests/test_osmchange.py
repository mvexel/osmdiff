import unittest
from pathlib import Path

from osmdiff import OSMChange


class AugmentedDiffTests(unittest.TestCase):

    def setUp(self) -> None:
        self.way_xml_file = Path(__file__).parent.joinpath(
            "fixtures/test_osmchange.xml"
        )
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_init_osmchange_from_file(self) -> None:
        with open(self.way_xml_file, "r") as fh:
            o = OSMChange.from_xml(fh.read())
            self.assertEqual(len(o.create), 831)
            self.assertEqual(len(o.modify), 368)
            self.assertEqual(len(o.delete), 3552)

    def test_osmchange_from_overpass_api(self) -> None:
        o = OSMChange()
        self.assertEqual(len(o.create), 0)
        self.assertEqual(len(o.modify), 0)
        self.assertEqual(len(o.delete), 0)
        o.get_state()
        self.assertGreater(o.sequence_number, 0)
        o.retrieve()
        self.assertGreaterEqual(len(o.create), 1)
        self.assertGreaterEqual(len(o.modify), 1)
