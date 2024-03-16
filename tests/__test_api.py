from osmdiff import AugmentedDiff, OSMChange
from typing_extensions import assert_type


class TestApi:
    "tests for API calls"

    state = None

    def test_osm_diff_api(self):
        "Test getting state from OSM API"
        osm_change = OSMChange()
        assert osm_change.get_state()
        self.state = osm_change.sequence_number
        assert_type(self.state, int)
        status = osm_change.retrieve()
        assert status == 200

    def test_augmented_diff_api(self):
        "Test getting augmented diff from Overpass API"
        augmented_diff = AugmentedDiff()
        assert augmented_diff.get_state()
        self.state = augmented_diff.sequence_number
        assert_type(self.state, int)
        status = augmented_diff.retrieve()
        assert status == 200
