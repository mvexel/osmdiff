import io
import gzip
import pytest
from osmdiff import Node, OSMChange, Relation, Way
from typing_extensions import assert_type
from unittest.mock import patch, MagicMock


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

    @patch('osmdiff.osmchange.requests.get')
    def test_get_state_success(self, mock_get):
        # Simulate a valid state response with sequenceNumber
        xml = b'''<osm><state><sequenceNumber>123</sequenceNumber></state></osm>'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = xml
        oc = OSMChange()
        assert oc.get_state() is True
        assert oc.sequence_number == 123

    @patch('osmdiff.osmchange.requests.get')
    def test_get_state_missing_seq(self, mock_get):
        # Simulate state response without sequenceNumber
        xml = b'''<osm><state></state></osm>'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = xml
        oc = OSMChange()
        assert oc.get_state() is False

    @patch('osmdiff.osmchange.requests.get')
    def test_get_state_fail(self, mock_get):
        mock_get.return_value.status_code = 404
        oc = OSMChange()
        assert oc.get_state() is False

    @patch('osmdiff.osmchange.requests.get')
    def test_retrieve_non_200(self, mock_get):
        oc = OSMChange(sequence_number=1)
        mock_get.return_value.status_code = 404
        mock_get.return_value.content = b''
        status = oc.retrieve()
        assert status == 404

    @patch('osmdiff.osmchange.requests.get')
    def test_retrieve_gzip(self, mock_get):
        # Simulate a gzip-compressed XML response
        xml = b'<osmChange></osmChange>'
        gzipped = gzip.compress(xml)
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = gzipped
        mock_get.return_value.raw = io.BytesIO(gzipped)
        oc = OSMChange(sequence_number=1)
        status = oc.retrieve()
        assert status == 200

    @patch('osmdiff.osmchange.requests.get', side_effect=ConnectionError)
    def test_retrieve_connection_error(self, mock_get):
        oc = OSMChange(sequence_number=1)
        status = oc.retrieve()
        assert status == 0

    @patch('osmdiff.osmchange.requests.get')
    def test_retrieve_clear_cache(self, mock_get):
        oc = OSMChange(sequence_number=1)
        oc.create = [1]
        oc.modify = [2]
        oc.delete = [3]
        mock_get.return_value.status_code = 404
        mock_get.return_value.content = b''
        oc.retrieve(clear_cache=True)
        assert oc.create == [] and oc.modify == [] and oc.delete == []

    def test_sequence_number_setter_and_errors(self):
        oc = OSMChange()
        oc.sequence_number = 42
        assert oc.sequence_number == 42
        oc.sequence_number = None
        assert oc.sequence_number is None
        with pytest.raises(ValueError):
            oc.sequence_number = 'notanumber'

    def test_frequency_setter_and_errors(self):
        oc = OSMChange()
        oc.frequency = 'hour'
        assert oc.frequency == 'hour'
        with pytest.raises(ValueError):
            oc.frequency = 'invalid'

    def test_actions_property(self):
        oc = OSMChange()
        oc.create = [1]
        oc.modify = [2]
        oc.delete = [3]
        acts = oc.actions
        assert acts['create'] == [1]
        assert acts['modify'] == [2]
        assert acts['delete'] == [3]

    def test_repr(self):
        oc = OSMChange()
        oc.create = [1,2]
        oc.modify = [3]
        oc.delete = []
        r = repr(oc)
        assert '2 created' in r and '1 modified' in r

    def test_context_manager_exit_clears(self):
        oc = OSMChange()
        oc.create = [1]
        oc.modify = [2]
        oc.delete = [3]
        with oc:
            pass
        assert oc.create == [] and oc.modify == [] and oc.delete == []

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_init_else_branch(self, mock_open):
        # Should set _frequency and _sequence_number if file is not provided
        oc = OSMChange(frequency='hour', sequence_number=42)
        assert oc._frequency == 'hour'
        assert oc._sequence_number == 42
        # Also cover the case where both are left default
        oc2 = OSMChange()
        assert hasattr(oc2, '_frequency')
        assert hasattr(oc2, '_sequence_number')
        assert oc2._frequency == 'minute'
        assert oc2._sequence_number is None
        # And the case where only frequency is set
        oc3 = OSMChange(frequency='day')
        assert oc3._frequency == 'day'
        assert oc3._sequence_number is None
        # And only sequence_number is set
        oc4 = OSMChange(sequence_number=99)
        assert oc4._frequency == 'minute'
        assert oc4._sequence_number == 99

    def test_retrieve_raises_on_missing_sequence_number(self):
        oc = OSMChange()
        with pytest.raises(Exception) as exc:
            oc.retrieve()
        assert "invalid sequence number" in str(exc.value)

    @patch('osmdiff.osmchange.requests.get')
    def test_retrieve_non_gzip_xml(self, mock_get):
        xml = b'<osmChange></osmChange>'
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = xml
        mock_get.return_value.raw = io.BytesIO(xml)
        oc = OSMChange(sequence_number=1)
        status = oc.retrieve()
        assert status == 200
