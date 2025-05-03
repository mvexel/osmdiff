import pytest
from osmdiff import ContinuousAugmentedDiff, AugmentedDiff
from unittest.mock import patch, MagicMock

class TestContinuousAugmentedDiff:
    @pytest.fixture
    def mock_state_sequence(self):
        # Simulate state endpoint returning increasing sequence numbers
        return [12345, 12345, 12346, 12347]

    @pytest.fixture
    def mock_adiff_response(self):
        xml_content = """<?xml version='1.0'?>\n<osm version='0.6'>\n<meta osm_base='2024-01-01T00:00:00Z'/>\n<action type='create'>\n<node id='1' version='1' timestamp='2024-01-01T00:00:00Z'/>\n</action>\n</osm>""".strip()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = xml_content
        mock_response.content = xml_content.encode()
        mock_response.raw = MagicMock()
        return mock_response

    def test_iterator_yields_augmented_diff(self, mock_state_sequence, mock_adiff_response):
        # Patch get_state and retrieve, and patch time.sleep to avoid real delays
        with patch.object(AugmentedDiff, "get_state", side_effect=mock_state_sequence), \
             patch.object(AugmentedDiff, "retrieve", return_value=200), \
             patch("time.sleep", return_value=None):

            fetcher = ContinuousAugmentedDiff(min_interval=0, max_interval=0)
            gen = iter(fetcher)
            # The first two calls return the same sequence, so no diff should be yielded yet
            # On the third call, sequence increases, so a diff is yielded
            diff = next(gen)
            assert isinstance(diff, AugmentedDiff)
            assert diff.sequence_number == 12346

            # Next sequence increases again, another diff is yielded
            diff2 = next(gen)
            assert isinstance(diff2, AugmentedDiff)
            assert diff2.sequence_number == 12347

    def test_iterator_handles_backoff(self, mock_state_sequence, mock_adiff_response):
        # Simulate get_state returning None (API error) first, then a valid sequence
        with patch.object(AugmentedDiff, "get_state", side_effect=[None, 12345, 12346]), \
             patch.object(AugmentedDiff, "retrieve", return_value=200), \
             patch("time.sleep", return_value=None):

            fetcher = ContinuousAugmentedDiff(min_interval=0, max_interval=0)
            gen = iter(fetcher)
            # First call to get_state returns None, so it should backoff and retry
            diff = next(gen)
            assert isinstance(diff, AugmentedDiff)
            assert diff.sequence_number == 12346
