"""
osmdiff is a Python library for working with OpenStreetMap changesets and diffs.

It provides classes for working with OpenStreetMap changesets and diffs, and
includes a parser for the OpenStreetMap changeset API.
"""

from .augmenteddiff import AugmentedDiff, ContinuousAugmentedDiff
from .osm import Node, Relation, Way
from .osmchange import OSMChange

__version__ = "0.4.5"
