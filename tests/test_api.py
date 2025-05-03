import pytest
from osmdiff import AugmentedDiff, OSMChange
from typing_extensions import assert_type
from unittest.mock import patch, MagicMock
import requests


class TestApi:
    """Tests for OSM API integration."""

    @pytest.fixture
    def mock_api_response(self):
        """Fixture providing a mock API response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = "<osm></osm>"
        return mock_response

    @pytest.mark.integration
    def test_osm_diff_api_state(self, mock_api_response):
        """Test getting state from OSM API returns valid sequence number."""
        with patch('requests.get', return_value=mock_api_response):
            osm_change = OSMChange()
            assert osm_change.get_state() is True
            assert_type(osm_change.sequence_number, int)
            assert osm_change.sequence_number >= 0

    @pytest.mark.integration
    def test_osm_diff_retrieve(self, mock_api_response):
        """Test retrieving OSM diff returns successful status."""
        with patch('requests.get', return_value=mock_api_response):
            osm_change = OSMChange()
            status = osm_change.retrieve()
            assert status == 200
            assert hasattr(osm_change, 'actions')

    @pytest.mark.integration
    def test_augmented_diff_api_state(self, mock_api_response):
        """Test getting state from Augmented Diff API returns valid sequence number."""
        with patch('requests.get', return_value=mock_api_response):
            augmented_diff = AugmentedDiff()
            assert augmented_diff.get_state() is True
            assert_type(augmented_diff.sequence_number, int)
            assert augmented_diff.sequence_number >= 0

    @pytest.mark.integration
    def test_augmented_diff_retrieve(self, mock_api_response):
        """Test retrieving Augmented Diff returns successful status."""
        with patch('requests.get', return_value=mock_api_response):
            augmented_diff = AugmentedDiff()
            status = augmented_diff.retrieve()
            assert status == 200
            assert hasattr(augmented_diff, 'remarks')

    @pytest.mark.integration
    def test_api_error_handling(self):
        """Test API error conditions are properly handled."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 500
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception):
                osm_change = OSMChange()
                osm_change.retrieve()
