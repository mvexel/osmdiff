"""
osmdiff is a Python library for working with OpenStreetMap changesets and diffs.

It provides classes for working with OpenStreetMap changesets and diffs, and
includes a parser for the OpenStreetMap changeset API.
"""

__version__ = [0, 4, 0]

from .augmenteddiff import AugmentedDiff
from .osm import Node, Relation, Way
from .osmchange import OSMChange
