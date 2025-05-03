# osmdiff

[![build and test](https://github.com/mvexel/osmdiff/actions/workflows/build_and_test.yml/badge.svg)](https://github.com/mvexel/osmdiff/actions/workflows/build_and_test.yml)

A read-only interface to OpenStreetMap change APIs and files. See also [pyosm](https://github.com/iandees/pyosm) which can do similar things. 

## Documentation

📚 Comprehensive documentation is available at [mvexel.github.io/osmdiff](https://mvexel.github.io/osmdiff/)

## Python Version Support

This module has been tested with Python 3.8 - 3.12. Use at your own risk with other versions.

## Installing

`pip install osmdiff`

## Usage

See the [documentation](https://mvexel.github.io/osmdiff/) for more details.

### Reading

Retrieve the latest replication diff from the OSM API:

```python
>>> from osmdiff import OSMChange
>>> o = OSMChange(frequency="minute")  # minute is the default frequency
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

### Iterating

To continuously iterate over AugmentedDiff objects, use `ContinuousAugmentedDiff`:

```python
>>> for a in ContinuousAugmentedDiff():
...     print(a)
```

This will iterate indefinitely, printing each AugmentedDiff as it is retrieved.

You can also use it in a loop:

```python
for a in ContinuousAugmentedDiff():
    if a.sequence_number > 123456:
        break
    print(a)
```

## Configuration

The osmdiff package uses a centralized configuration system in `src/osmdiff/config.py`. This includes:

### API Configuration
Default settings for API endpoints and timeouts:

```python
API_CONFIG = {
    "overpass": {"base_url": "...", "timeout": 30},
    "osm": {"base_url": "...", "timeout": 30},
    "nominatim": {"base_url": "...", "timeout": 30}
}
```

### Request Headers
Standard headers used in all API requests:
```python
DEFAULT_HEADERS = {
    "User-Agent": "osmdiff/1.0",
    "Accept": "application/json, text/xml"
}
```

### Customizing Configuration
You can override any configuration value at runtime by passing parameters to the respective class constructors:

```python
from osmdiff import OSMChange

# Override default URL and timeout
change = OSMChange(
    url="https://custom-api.example.com",
    timeout=60
)
```

## Community

Join the conversation and get help:

- [GitHub Discussions](https://github.com/mvexel/osmdiff/discussions) - For questions, ideas, and general discussion
- [OpenStreetMap Community Forum](https://community.openstreetmap.org/) - For broader OSM-related discussions
- [OSM Slack](https://osmus.slack.com/) - Join the #dev channel

Please be respectful and follow the [OpenStreetMap Code of Conduct](https://wiki.openstreetmap.org/wiki/Code_of_conduct) in all community interactions.

## Contributing

I welcome your contributions in code, documentation and suggestions for enhancements.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

If you find `osmdiff` useful, or you use it in commercial software, please consider sponsoring this project.
