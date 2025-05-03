from osmdiff import Node, AugmentedDiff, Relation, Way
from typing_extensions import assert_type
from unittest.mock import patch, Mock
from io import StringIO, BytesIO


class TestAugmentedDiff:
    "tests for AugmentedDiff class"

    def test_init_augmenteddiff(self):
        "Test AugmentedDiff init"
        augmenteddiff = AugmentedDiff()
        assert_type(augmenteddiff, AugmentedDiff)
        assert_type(augmenteddiff.create, list)
        assert_type(augmenteddiff.modify, list)
        assert_type(augmenteddiff.delete, list)
        assert len(augmenteddiff.create) == 0
        assert len(augmenteddiff.modify) == 0
        assert len(augmenteddiff.delete) == 0

    def test_set_sequencenumber(self):
        "Sequence number is not defined by default but can be set manually"
        augmented_diff = AugmentedDiff()
        assert not augmented_diff.sequence_number
        augmented_diff.sequence_number = 12345
        assert augmented_diff.sequence_number == 12345
        augmented_diff.sequence_number = "12345"
        assert augmented_diff.sequence_number == 12345

    @patch('osmdiff.augmenteddiff.requests.get')
    def test_read_changeset_from_xml_file(self, mock_get, adiff_file_path, mock_adiff_response):
        """Test initializing from an XML object with mocked response"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.raw = BytesIO(mock_adiff_response)
        mock_get.return_value.raw.decode_content = True
        
        adiff = AugmentedDiff(file=adiff_file_path)
        
        # Verify API call was made if file is remote
        if adiff_file_path.startswith('http'):
            mock_get.assert_called_once()
        
        # Test that objects were parsed correctly
        assert len(adiff.create) > 0
        assert len(adiff.modify) >= 0  # Some diffs may only have creates
        assert len(adiff.delete) >= 0  # Some diffs may only have creates

        # Test created object structure
        if adiff.create:
            created_obj = adiff.create[0]
            assert isinstance(created_obj, (Node, Way, Relation))
            assert hasattr(created_obj, 'attribs')
            assert hasattr(created_obj, 'tags')

        # Test modified object structure
        if adiff.modify:
            modified = adiff.modify[0]
            assert set(modified.keys()) == {'old', 'new'}
            assert isinstance(modified['old'], (Node, Way, Relation))
            assert isinstance(modified['new'], (Node, Way, Relation))

        # Test deleted object structure
        if adiff.delete:
            deleted_obj = adiff.delete[0]
            assert 'old' in deleted_obj
            assert isinstance(deleted_obj['old'], (Node, Way, Relation))
            assert 'meta' in deleted_obj  # Verify metadata exists

        # Test metadata was parsed
        assert adiff.timestamp is not None
        assert isinstance(adiff.remarks, list)

    def test_auto_increment(self):
        "Test auto-increment behavior in retrieve()"
        augmented_diff = AugmentedDiff()
        augmented_diff.sequence_number = 100
        
        # Create a minimal valid XML response
        xml_content = '''<?xml version='1.0' encoding='UTF-8'?>
<osm version="0.6" generator="Overpass API">
    <note>The data included in this document is from www.openstreetmap.org</note>
    <meta osm_base="2023-01-01T00:00:00Z"/>
    <action type="create">
        <node id="123" lat="51.5" lon="-0.1" version="1" timestamp="2023-01-01T00:00:00Z"/>
    </action>
    <action type="modify">
        <old>
            <node id="456" lat="51.5" lon="-0.1" version="1"/>
        </old>
        <new>
            <node id="456" lat="51.6" lon="-0.2" version="2"/>
        </new>
    </action>
</osm>'''
        
        # Mock the requests.get call
        with patch('requests.get') as mock_get:
            def get_mock_response():
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raw = StringIO(xml_content)
                mock_response.raw.decode_content = True
                return mock_response
            
            mock_get.return_value = get_mock_response()
            
            # Test auto-increment (default behavior)
            augmented_diff.retrieve()
            assert augmented_diff.sequence_number == 101
            
            # Create fresh mock for second call
            mock_get.return_value = get_mock_response()
            
            # Test without auto-increment
            augmented_diff.retrieve(auto_increment=False)
            assert augmented_diff.sequence_number == 101
            
            # Create fresh mock for third call
            mock_get.return_value = get_mock_response()
            
            # Test with auto-increment again
            augmented_diff.retrieve()
            assert augmented_diff.sequence_number == 102
