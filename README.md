# osmdiff

A read-only interface to OpenStreetMap change APIs and files. See also [pyosm](https://github.com/iandees/pyosm) which can do similar things. 

Python 3.7+

## Installing

`pip install osmdiff`

## Usage

### Reading

Retrieve the latest replication diff from the OSM API:

```python
>>> from osmdiff import OSMChange
>>> o = OSMChange()
>>> o.frequency = "minute"  # the default
>>> o.get_state()  # retrieve current sequence ID
>>> o.sequence_number
2704451
>>> o.retrieve()  # retrieve from API
>>> o
OSMChange (677 created, 204 modified, 14 deleted)
```

Read a replication diff from a file:

```python
>>> from osmdiff import OSMChange
>>> o = OSMChange(file="test_osmchange.xml")
>>> o
OSMChange (831 created, 368 modified, 3552 deleted)
```

Retrieve the latest Augmented Diff from Overpass:

```python
>>> from osmdiff import AugmentedDiff
>>> a = AugmentedDiff()
>>> a.get_state()
>>> a.sequence_number
2715051
>>> a.retrieve()
>>> a
AugmentedDiff (747 created, 374 modified, 55 deleted)
```

Read an augmented diff file:

```python
>>> from osmdiff import AugmentedDiff
>>> a = AugmentedDiff(file="test_adiff.xml")
>>> a
AugmentedDiff (2329 created, 677 modified, 39 deleted)
```

### Inspect contents

Get all the things that `chris66` has created:

```
>>> [n for n in a.create if n.attribs["user"] == "chris66"]
[Node 5221564287, Node 5221564288, Node 5221564289, Node 5221564290, Node 5221564291, Node 5221564292, Node 5221564293, Node 5221564294, Node 5221564295, Node 5221564296, Node 5221564297, Node 5221564298, Node 5221564299, Node 5221564301, Node 5221564302, Node 5221564303, Node 5221564304, Way 539648222 (5 nodes), Way 539648223 (5 nodes), Way 539648323 (5 nodes)]
```

Get all `residential` ways that were modified:

```python
>>> [n["new"] for n in a.modify if type(n["new"]) == Way and n["new"].tags.get("highway") == "residential"]
[Way 34561958 (3 nodes), Way 53744484 (6 nodes), Way 53744485 (6 nodes), Way 122650942 (3 nodes), Way 283221266 (4 nodes), Way 344272652 (5 nodes), Way 358243999 (13 nodes), Way 410489319 (5 nodes), Way 452218081 (10 nodes)]
```

Get all ways that were changed to `residential` from something else:

```python
>>> [n["new"] for n in a.modify if type(n["new"]) == Way and n["new"].tags.get("highway") == "residential" and n["old"].tags["highway"] != "residential"]
[Way 410489319 (5 nodes), Way 452218081 (10 nodes)]
```

Inspect details:

```python
>>> w = [n["new"] for n in a.modify if n["new"].attribs["id"] == "452218081"]
>>> w
[Way 452218081 (10 nodes)]
>>> w[0]
Way 452218081 (10 nodes)
>>> w[0].tags
{'highway': 'residential'}
>>> w[0].attribs
{'id': '452218081', 'version': '2', 'timestamp': '2017-11-10T13:52:01Z', 'changeset': '53667190', 'uid': '2352517', 'user': 'carths81'}
>>> w[0].attribs
{'id': '452218081', 'version': '2', 'timestamp': '2017-11-10T13:52:01Z', 'changeset': '53667190', 'uid': '2352517', 'user': 'carths81'}
>>> w[0].bounds
['12.8932677', '43.3575917', '12.8948117', '43.3585947']
```