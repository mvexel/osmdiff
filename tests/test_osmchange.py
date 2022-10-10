from pathlib import Path

from osmdiff import Node, OSMChange, Relation, Way
from typing_extensions import assert_type


class TestOSMChange:
    "tests for OSMChange object"

    osmchange_file_path = (
        Path(__file__).parent / "fixtures/test_osmchange.xml"
    ).resolve()

    def test_init_osmchange(self):
        "Test OSMChange init"
        osmchange = OSMChange()
        assert_type(osmchange, OSMChange)
        assert_type(osmchange.create, list)
        assert_type(osmchange.modify, list)
        assert_type(osmchange.delete, list)
        assert len(osmchange.create) == 0
        assert len(osmchange.modify) == 0
        assert len(osmchange.delete) == 0

    def test_set_sequencenumber(self):
        "Sequence number is not defined by default but can be set manually"
        osm_change = OSMChange()
        assert not osm_change.sequence_number
        osm_change.sequence_number = 12345
        assert osm_change.sequence_number == 12345
        osm_change.sequence_number = "12345"
        assert osm_change.sequence_number == 12345

    def test_3_readfromfile(self):
        "Test initializing from file"
        osmchange = OSMChange.from_xml(self.osmchange_file_path)
        assert len(osmchange.create) == 831
        assert len(osmchange.modify) == 368
        assert len(osmchange.delete) == 3552
        nodes_created = [o for o in osmchange.create if isinstance(o, Node)]
        ways_created = [o for o in osmchange.create if isinstance(o, Way)]
        rels_created = [o for o in osmchange.create if isinstance(o, Relation)]
        assert len(nodes_created) == 699
        assert len(ways_created) == 132
        assert len(rels_created) == 0
        assert len(nodes_created + ways_created + rels_created) == len(osmchange.create)
