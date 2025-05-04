#!/usr/bin/env python

from osmdiff import AugmentedDiff, OSMChange
from osmdiff.osm import Node, Relation, Way
from pathlib import Path

osm_change_file = Path("tests", "data", "test_osmchange.xml")
print(osm_change_file)

# absolute path
osm_change_file = osm_change_file.resolve()
print(osm_change_file)


r = OSMChange()
r.get_state()
r.retrieve()
print(r)

r = OSMChange(file=osm_change_file)
print(r)

a = AugmentedDiff(file=osm_change_file)
print(a)

a = AugmentedDiff(
    # minlon=-160.0,
    # minlat=20.0,
    # maxlon=-80.0,
    # maxlat=60.0,
)
a._get_current_id()
a.retrieve()
print(a)

# n = Node()
# w = Way()
# r = Relation()

# r = replication.OSMChange(frequency="hour")

# print(r.sequence_number)
# r.get(r.sequence_number)

# r = replication.OSMChange(frequency="day")

# print(r.sequence_number)
# r.get(r.sequence_number)
