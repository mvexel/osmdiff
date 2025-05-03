import pytest
from osmdiff import AugmentedDiff
from unittest.mock import patch, MagicMock
import requests
from io import BytesIO


class TestAugmentedDiff:
    """Tests for AugmentedDiff class."""

    @pytest.fixture
    def mock_adiff_response(self):
        """Fixture providing a mock Augmented Diff response."""
        xml_content = """<?xml version='1.0'?>
        <osm version='0.6'>
            <meta osm_base='2024-01-01T00:00:00Z'/>
            <action type='create'>
                <node id='1' version='1' timestamp='2024-01-01T00:00:00Z'/>
            </action>
        </osm>"""
        
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = xml_content
        mock_response.content = xml_content.encode()
        
        # Create a raw attribute with a read method
        mock_raw = BytesIO(xml_content.encode())
        mock_raw.decode_content = True
        mock_response.raw = mock_raw
        
        return mock_response

    @pytest.fixture
    def mock_timeout_response(self):
        """Fixture providing a mock timeout response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.side_effect = requests.exceptions.ReadTimeout("Timeout")
        return mock_response

    @pytest.fixture
    def augmented_diff(self):
        """Fixture providing a basic AugmentedDiff instance."""
        return AugmentedDiff(sequence_number=12345)

    def test_delete_metadata(self, augmented_diff):
        """Test that metadata is captured for deleted objects."""
        with open("tests/data/test_delete_metadata.xml", "r") as f:
            adiff = AugmentedDiff(file=f.name)
            
        assert len(adiff.delete) == 1
        deletion = adiff.delete[0]
        
        # Check the metadata is present
        assert "meta" in deletion
        assert deletion["meta"]["user"] == "TestUser"
        assert deletion["meta"]["uid"] == "12345"
        assert deletion["meta"]["changeset"] == "67890"
        assert deletion["meta"]["timestamp"] == "2024-01-28T12:00:00Z"
        
        # Check the old object is present
        assert "old" in deletion
        assert deletion["old"].attribs["id"] == "123"
        assert deletion["old"].attribs["lat"] == "51.5"
        assert deletion["old"].attribs["lon"] == "-0.1"
        assert deletion["old"].tags["amenity"] == "cafe"

    def test_timeout_retry_success(self, augmented_diff, mock_adiff_response, mock_timeout_response):
        """Test successful retry after timeout."""
        with patch('requests.get', side_effect=[mock_timeout_response, mock_adiff_response]) as mock_get:
            status = augmented_diff.retrieve()
            assert status == 200
            assert mock_get.call_count == 2  # Verify it retried once

    def test_multiple_timeouts(self, augmented_diff, mock_timeout_response):
        """Test max retries on consecutive timeouts."""
        with patch('requests.get', return_value=mock_timeout_response) as mock_get:
            with pytest.raises(requests.exceptions.ReadTimeout):
                augmented_diff.retrieve()
            assert mock_get.call_count == 3  # Verify it tried 3 times

    def test_consecutive_sequence_numbers(self, augmented_diff, mock_adiff_response):
        """Test auto-increment of sequence numbers."""
        with patch('requests.get', return_value=mock_adiff_response) as mock_get:
            # Retrieve first diff
            status1 = augmented_diff.retrieve(auto_increment=True)
            assert status1 == 200
            assert augmented_diff.sequence_number == 12346
            initial_create_count = len(augmented_diff.create)

            # Retrieve next diff
            status2 = augmented_diff.retrieve(auto_increment=True)
            assert status2 == 200
            assert augmented_diff.sequence_number == 12347
            
            # Verify changes were merged
            assert len(augmented_diff.create) > initial_create_count
