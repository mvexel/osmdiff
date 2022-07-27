#!/usr/bin/env python

from osmdiff import OSMChange, AugmentedDiff

debug = True

# r = OSMChange()
# r.get_state()
# r.retrieve()
# print(r)

with open("fixtures/test_osmchange.xml", "r") as fh:
    r = OSMChange.from_xml(fh.read())
    print(r)

a = AugmentedDiff(
    file="fixtures/test_adiff.xml",
    debug=debug)
print(a)

a = AugmentedDiff(
    # minlon=-160.0,
    # minlat=20.0,
    # maxlon=-80.0,
    # maxlat=60.0,
    debug=debug)
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
