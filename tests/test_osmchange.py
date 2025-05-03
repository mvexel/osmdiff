from osmdiff import Node, OSMChange, Relation, Way
from typing_extensions import assert_type
from unittest.mock import patch


class TestOSMChange:
    "tests for OSMChange object"

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

    @patch('osmdiff.osmchange.requests.get')
    def test_read_changeset_from_xml_file(self, mock_get, osmchange_file_path):
        """Test initializing from an XML object with mocked response"""
        # Mock the response if testing remote file
        if osmchange_file_path.startswith('http'):
            mock_get.return_value.status_code = 200
            with open("tests/data/test_osmchange.xml", "rb") as f:
                mock_get.return_value.content = f.read()
        
        osmchange = OSMChange.from_xml_file(osmchange_file_path)
        
        # Verify API call was made if file is remote
        if osmchange_file_path.startswith('http'):
            mock_get.assert_called_once()

        # Test counts
        assert len(osmchange.create) > 0
        assert len(osmchange.modify) >= 0
        assert len(osmchange.delete) >= 0

        # Test object types
        nodes_created = [o for o in osmchange.create if isinstance(o, Node)]
        ways_created = [o for o in osmchange.create if isinstance(o, Way)]
        rels_created = [o for o in osmchange.create if isinstance(o, Relation)]
        
        # Verify all created objects are accounted for
        assert len(nodes_created + ways_created + rels_created) == len(osmchange.create)
        
        # Test object attributes
        if nodes_created:
            node = nodes_created[0]
            assert hasattr(node, 'lat')
            assert hasattr(node, 'lon')
