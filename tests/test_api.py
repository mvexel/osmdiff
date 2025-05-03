import pytest
from osmdiff import AugmentedDiff, OSMChange
from typing_extensions import assert_type
from unittest.mock import patch, MagicMock
import requests


class TestApi:
    """Tests for OSM API integration."""

    @pytest.fixture
    def mock_osm_state_response(self):
        """Fixture providing a mock OSM state API response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.content = """<?xml version='1.0'?>
        <osm version='0.6'>
            <state>
                <sequenceNumber>12345</sequenceNumber>
                <timestamp>2024-01-01T00:00:00Z</timestamp>
            </state>
        </osm>""".encode()
        return mock_response

    @pytest.fixture
    def mock_osm_diff_response(self):
        """Fixture providing a mock OSM diff response."""
        import gzip
        import io
        xml_content = """<?xml version='1.0'?>
        <osmChange version='0.6'>
            <create>
                <node id='1' version='1' timestamp='2024-01-01T00:00:00Z'/>
            </create>
        </osmChange>"""
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
            f.write(xml_content.encode())
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {'Content-Encoding': 'gzip'}
        mock_response.content = buffer.getvalue()
        return mock_response

    @pytest.fixture
    def mock_adiff_response(self):
        """Fixture providing a mock Augmented Diff response."""
        import gzip
        import io
        xml_content = """<?xml version='1.0'?>
        <osm version='0.6'>
            <meta osm_base='2024-01-01T00:00:00Z'/>
            <action type='create'>
                <node id='1' version='1' timestamp='2024-01-01T00:00:00Z'/>
            </action>
        </osm>"""
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
            f.write(xml_content.encode())
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {'Content-Encoding': 'gzip'}
        mock_response.content = buffer.getvalue()
        return mock_response

    @pytest.mark.integration
    def test_osm_diff_api_state(self, mock_osm_state_response):
        """Test getting state from OSM API returns valid sequence number."""
        with patch('osmdiff.osmchange.requests.get', return_value=mock_osm_state_response):
            osm_change = OSMChange()
            osm_change.base_url = "http://example.com/api"
            state = osm_change.get_state()
            assert state is True
            assert osm_change.sequence_number == 12345
            assert isinstance(osm_change.sequence_number, int)

    @pytest.mark.integration
    def test_osm_diff_retrieve(self, mock_osm_diff_response):
        """Test retrieving OSM diff returns successful status."""
        with patch('requests.get', return_value=mock_osm_diff_response):
            osm_change = OSMChange(sequence_number=12345)
            status = osm_change.retrieve()
            assert status == 200
            assert hasattr(osm_change, 'actions')
            assert len(osm_change.actions) > 0

    @pytest.mark.integration
    def test_augmented_diff_api_state(self, mock_osm_state_response):
        """Test getting state from Augmented Diff API returns valid sequence number."""
        with patch('osmdiff.augmenteddiff.requests.get', return_value=mock_osm_state_response):
            augmented_diff = AugmentedDiff()
            augmented_diff.base_url = "http://example.com/api"
            state = augmented_diff.get_state()
            assert state is True
            assert augmented_diff.sequence_number == 12345
            assert isinstance(augmented_diff.sequence_number, int)

    @pytest.mark.integration
    def test_augmented_diff_retrieve(self, mock_adiff_response):
        """Test retrieving Augmented Diff returns successful status."""
        with patch('requests.get', return_value=mock_adiff_response):
            augmented_diff = AugmentedDiff(sequence_number=12345)
            status = augmented_diff.retrieve()
            assert status == 200
            assert hasattr(augmented_diff, 'remarks')
            assert len(augmented_diff.remarks) > 0

    @pytest.mark.integration
    def test_api_error_handling(self):
        """Test API error conditions are properly handled."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 500
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception):
                osm_change = OSMChange()
                osm_change.retrieve()
