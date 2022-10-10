#!/usr/bin/env python

from osmdiff import AugmentedDiff, OSMChange
from osmdiff.osm import Node, Relation, Way

debug = True

r = OSMChange(debug=debug)
r.get_state()
r.retrieve()
print(r)

r = OSMChange(file="test_osmchange.xml", debug=debug)
print(r)

a = AugmentedDiff(file="test_adiff.xml", debug=debug)
print(a)

a = AugmentedDiff(
    # minlon=-160.0,
    # minlat=20.0,
    # maxlon=-80.0,
    # maxlat=60.0,
    debug=debug
)
a.get_state()
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
