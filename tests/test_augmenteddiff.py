import unittest
from unittest.mock import patch
import requests
from osmdiff import AugmentedDiff
from io import BytesIO

class MockStream:
    def __init__(self, content):
        self.content = content
        self.position = 0
        self.decode_content = None

    def read(self, size=None):
        if self.position >= len(self.content):
            return b''
        if size is None:
            data = self.content[self.position:]
            self.position = len(self.content)
        else:
            data = self.content[self.position:self.position + size]
            self.position += size
        return data

class TestAugmentedDiffRetries(unittest.TestCase):
    def setUp(self):
        self.adiff = AugmentedDiff(sequence_number=12345)

    @patch('requests.get')
    def test_timeout_retry_success(self, mock_get):
        # First call raises timeout, second succeeds
        xml_content = b'''<?xml version='1.0' encoding='UTF-8'?>
        <osm version="0.6">
            <meta osm_base="2024-01-01T00:00:00Z"/>
        </osm>'''
        
        mock_get.side_effect = [
            requests.exceptions.ReadTimeout("Timeout"),
            type('Response', (), {
                'status_code': 200,
                'raw': MockStream(xml_content)
            })
        ]

        status = self.adiff.retrieve()
        self.assertEqual(status, 200)
        self.assertEqual(mock_get.call_count, 2)  # Verify it retried once

    @patch('requests.get')
    def test_multiple_timeouts(self, mock_get):
        # All calls timeout
        mock_get.side_effect = requests.exceptions.ReadTimeout("Timeout")

        with self.assertRaises(requests.exceptions.ReadTimeout):
            self.adiff.retrieve()
        
        self.assertEqual(mock_get.call_count, 3)  # Verify it tried 3 times

    def test_delete_metadata(self):
        """Test that metadata is captured for deleted objects"""
        with open("tests/data/test_delete_metadata.xml", "r") as f:
            adiff = AugmentedDiff(file=f.name)
            
        self.assertEqual(len(adiff.delete), 1)
        deletion = adiff.delete[0]
        
        # Check the metadata is present
        self.assertIn("meta", deletion)
        self.assertEqual(deletion["meta"]["user"], "TestUser")
        self.assertEqual(deletion["meta"]["uid"], "12345")
        self.assertEqual(deletion["meta"]["changeset"], "67890")
        self.assertEqual(deletion["meta"]["timestamp"], "2024-01-28T12:00:00Z")
        
        # Check the old object is present
        self.assertIn("old", deletion)
        self.assertEqual(deletion["old"].attribs["id"], "123")
        self.assertEqual(deletion["old"].attribs["lat"], "51.5")
        self.assertEqual(deletion["old"].attribs["lon"], "-0.1")
        self.assertEqual(deletion["old"].tags["amenity"], "cafe")

    @patch('requests.get')
    def test_consecutive_sequence_numbers(self, mock_get):
        # Test retrieving consecutive diffs (12345 -> 12346)
        xml_content = b'''<?xml version='1.0' encoding='UTF-8'?>
        <osm version="0.6">
            <meta osm_base="2024-01-01T00:00:00Z"/>
            <action type="create">
                <node id="1" version="1" timestamp="2024-01-01T00:00:00Z" uid="1" user="test" changeset="1" lat="0" lon="0"/>
            </action>
        </osm>'''
        
        def mock_responses(*args, **kwargs):
            return type('Response', (), {
                'status_code': 200,
                'raw': MockStream(xml_content)
            })

        mock_get.side_effect = mock_responses

        # Retrieve first diff
        status1 = self.adiff.retrieve(auto_increment=True)
        self.assertEqual(status1, 200)
        self.assertEqual(self.adiff.sequence_number, 12346)
        initial_create_count = len(self.adiff.create)

        # Retrieve next diff
        status2 = self.adiff.retrieve(auto_increment=True)
        self.assertEqual(status2, 200)
        self.assertEqual(self.adiff.sequence_number, 12347)
        
        # Verify changes were merged
        self.assertGreater(len(self.adiff.create), initial_create_count)
