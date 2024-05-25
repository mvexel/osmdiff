from osmdiff import Node, AugmentedDiff, Relation, Way
from typing_extensions import assert_type


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

    def test_read_changeset_from_xml_file(self, adiff_file_path):
        "Test initializing from an XML object"
        # not implemented yet
        pass
