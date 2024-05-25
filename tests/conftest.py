import pytest
import xml.etree.ElementTree as ET


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
