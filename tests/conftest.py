import pytest
import xml.etree.ElementTree as ET
from unittest.mock import Mock


@pytest.fixture
def mock_osm_api_response():
    return {
        "status": 200,
        "data": {
            # mock response data
        },
    }


@pytest.fixture
def mock_osm_api(monkeypatch):
    mock = Mock()
    mock.get.return_value.status_code = 200
    mock.get.return_value.json.return_value = {
        # mock response data
    }
    monkeypatch.setattr("requests.get", mock.get)
    return mock


# Define a fixture to load the XML file
@pytest.fixture
def osmchange_xml_obj():
    with open("tests/data/test_osmchange.xml", "r") as fh:
        return ET.parse(fh)


# Path to the changeset XML file
@pytest.fixture
def osmchange_file_path():
    return "tests/data/test_osmchange.xml"


# Path to the augmented diff XML file
@pytest.fixture
def adiff_file_path():
    return "tests/data/test_adiff.xml"


@pytest.fixture
def api_config():
    return {
        "base_url": "https://api.openstreetmap.org/api/0.6",
        "timeout": 30,
        "headers": {"Content-Type": "application/xml", "Accept": "application/xml"},
    }


@pytest.fixture
def create_test_changeset():
    def _create_changeset(id="12345", user="testuser"):
        return f"""
        <osmChange version="0.6">
            <create>
                <node id="{id}" user="{user}" ... />
            </create>
        </osmChange>
        """

    return _create_changeset
