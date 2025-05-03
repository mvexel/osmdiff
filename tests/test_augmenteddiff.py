import pytest
from osmdiff import AugmentedDiff
from unittest.mock import patch, MagicMock
import requests
from io import BytesIO


class TestAugmentedDiff:
    """Tests for AugmentedDiff class."""

    def test_get_state_errors(self):
        """Test AugmentedDiff.get_state error handling and edge cases."""
        from osmdiff import AugmentedDiff
        import requests
        from unittest.mock import patch, MagicMock

        # Non-200 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch('requests.get', return_value=mock_response):
            assert AugmentedDiff.get_state(base_url='http://fake') is None

        # Malformed XML
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<invalid>'
        with patch('requests.get', return_value=mock_response):
            assert AugmentedDiff.get_state(base_url='http://fake') is None

        # Missing <state>
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<osm></osm>'
        with patch('requests.get', return_value=mock_response):
            assert AugmentedDiff.get_state(base_url='http://fake') is None

        # Exception in requests.get
        with patch('requests.get', side_effect=requests.exceptions.RequestException):
            assert AugmentedDiff.get_state(base_url='http://fake') is None

    def test_retrieve_exceptions_and_clear_cache(self):
        """Test retrieve() for missing sequence_number, clear_cache, and non-200 status."""
        from osmdiff import AugmentedDiff
        import requests
        from unittest.mock import patch, MagicMock

        # Missing sequence_number
        adiff = AugmentedDiff()
        with patch('requests.get'):
            try:
                adiff.retrieve()
            except Exception as e:
                assert "invalid sequence number" in str(e)
            else:
                assert False, "Exception not raised for missing sequence_number"

        # clear_cache should clear lists
        adiff = AugmentedDiff(sequence_number=1)
        adiff.create = [1]
        adiff.modify = [2]
        adiff.delete = [3]
        import io
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raw = io.BytesIO(b'<osm></osm>')
        mock_response.raw.decode_content = True
        mock_response.content = b'<osm></osm>'
        with patch('requests.get', return_value=mock_response):
            adiff.retrieve(clear_cache=True)
        assert adiff.create == []
        assert adiff.modify == []
        assert adiff.delete == []

        # Non-200 HTTP status
        adiff = AugmentedDiff(sequence_number=1)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raw = MagicMock()
        mock_response.raw.decode_content = True
        with patch('requests.get', return_value=mock_response):
            status = adiff.retrieve()
        assert status == 404

    def test_parse_stream_meta_tag(self):
        """Test that meta tag in XML sets timestamp attribute."""
        from osmdiff import AugmentedDiff
        import io
        xml = '''<osm><meta osm_base="2024-01-01T12:34:56Z"/></osm>'''
        adiff = AugmentedDiff()
        adiff._parse_stream(io.StringIO(xml))
        assert hasattr(adiff, 'timestamp')

    def test_sequence_number_setter_and_repr(self):
        """Test sequence_number setter error and __repr__ output."""
        from osmdiff import AugmentedDiff
        adiff = AugmentedDiff(sequence_number=1)
        # Valid int
        adiff.sequence_number = 42
        assert adiff.sequence_number == 42
        # Valid string
        adiff.sequence_number = "43"
        assert adiff.sequence_number == 43
        # Invalid value
        try:
            adiff.sequence_number = "notanumber"
        except ValueError as e:
            assert "sequence_number must be an integer" in str(e)
        else:
            assert False, "ValueError not raised for invalid sequence_number"
        # __repr__
        r = repr(adiff)
        assert "AugmentedDiff" in r and "created" in r and "modified" in r and "deleted" in r

    def test_context_manager_clears_lists(self):
        """Test that __enter__ returns self and __exit__ clears lists."""
        from osmdiff import AugmentedDiff
        adiff = AugmentedDiff(sequence_number=1)
        adiff.create = [1]
        adiff.modify = [2]
        adiff.delete = [3]
        with adiff as a:
            assert a is adiff
            assert adiff.create == [1]
        # After context exit, lists should be cleared
        assert adiff.create == []
        assert adiff.modify == []
        assert adiff.delete == []

    def test_build_adiff_url_bbox(self):
        """Test that bbox is included in the URL if provided."""
        from osmdiff import AugmentedDiff
        # Without bbox
        adiff = AugmentedDiff(sequence_number=123, base_url="http://example.com")
        url = adiff._build_adiff_url()
        assert url.startswith("http://example.com/augmented_diff?id=123")
        assert "bbox" not in url

        # With bbox
        adiff = AugmentedDiff(minlon=1, minlat=2, maxlon=3, maxlat=4, sequence_number=123, base_url="http://example.com")
        url = adiff._build_adiff_url()
        assert url.startswith("http://example.com/augmented_diff?id=123")
        assert "bbox=1,2,3,4" in url

    def test_bbox_validation(self):
        """Test that invalid bounding boxes raise an Exception."""
        from osmdiff import AugmentedDiff
        # Valid bbox should NOT raise
        AugmentedDiff(minlon=5, minlat=10, maxlon=10, maxlat=20)
        # Invalid bbox: maxlon <= minlon (all nonzero)
        with pytest.raises(Exception, match="invalid bbox"):
            AugmentedDiff(minlon=10, minlat=10, maxlon=5, maxlat=20)
        # Invalid bbox: maxlat <= minlat (all nonzero)
        with pytest.raises(Exception, match="invalid bbox"):
            AugmentedDiff(minlon=5, minlat=20, maxlon=10, maxlat=10)


    @pytest.fixture
    def mock_adiff_response(self):
        """Fixture providing a mock Augmented Diff response."""
        xml_content = """<?xml version='1.0'?>
<osm version='0.6'>
<meta osm_base='2024-01-01T00:00:00Z'/>
<action type='create'>
<node id='1' version='1' timestamp='2024-01-01T00:00:00Z'/>
</action>
</osm>""".strip()
        
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = xml_content
        mock_response.content = xml_content.encode()
        mock_response.raw = BytesIO(xml_content.encode())
        return mock_response

    @pytest.fixture
    def mock_timeout_response(self):
        """Fixture providing a mock timeout response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.side_effect = requests.exceptions.ReadTimeout("Timeout")
        
        # Add raw attribute that will raise timeout when read
        mock_raw = MagicMock()
        mock_raw.read.side_effect = requests.exceptions.ReadTimeout("Timeout")
        mock_raw.decode_content = True
        mock_response.raw = mock_raw
        
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

    def test_consecutive_sequence_numbers(self, augmented_diff):
        """Test auto-increment of sequence numbers."""
        def new_mock_response():
            xml_content = """<?xml version='1.0'?>\n<osm version='0.6'>\n<meta osm_base='2024-01-01T00:00:00Z'/>\n<action type='create'>\n<node id='1' version='1' timestamp='2024-01-01T00:00:00Z'/>\n</action>\n</osm>""".strip()
            mock_response = MagicMock(spec=requests.Response)
            mock_response.status_code = 200
            mock_response.text = xml_content
            mock_response.content = xml_content.encode()
            mock_response.raw = BytesIO(xml_content.encode())
            return mock_response

        with patch('requests.get', side_effect=[new_mock_response(), new_mock_response()]) as mock_get:
            # Retrieve first diff
            status1 = augmented_diff.retrieve(auto_increment=True)
            assert status1 == 200
            assert augmented_diff.sequence_number == 12346
            initial_create_count = len(augmented_diff.create)

            # Retrieve next diff
            status2 = augmented_diff.retrieve(auto_increment=True)
            assert status2 == 200
            assert augmented_diff.sequence_number == 12347
            assert len(augmented_diff.create) == initial_create_count * 2
            assert mock_get.call_count == 2
