import pytest
from osmdiff.osm import Node


@pytest.fixture(scope="module")
def valid_area():
    return (
        Node((0.0, 0.0)),
        Node((1.0, 0.0)),
        Node((1.0, 1.0)),
        Node((0.0, 1.0)),
        Node((0.0, 0.0)),
    )


@pytest.fixture(scope="module")
def unclosed_way():
    return (Node((0.0, 0.0)), Node((1.0, 0.0)), Node((1.0, 1.0)), Node((0.0, 1.0)))


@pytest.fixture(scope="module")
def self_intersecting_linestring():
    return (Node((0.0, 0.0)), Node((1.0, 0.0)), Node((1.0, 1.0)), Node((0.0, 0.0)))
