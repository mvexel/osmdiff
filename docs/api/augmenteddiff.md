# AugmentedDiff

Core class for retrieving and parsing OpenStreetMap augmented diffs.

For continuous monitoring of changes, see [ContinuousAugmentedDiff](continuous.md).

## Features

- Single diff retrieval
- Bounding box filtering
- Automatic sequence number handling
- Context manager support

## Basic Usage

```python
from osmdiff import AugmentedDiff

# Create with bounding box for London
adiff = AugmentedDiff(
    minlon=-0.489,
    minlat=51.28,
    maxlon=0.236,
    maxlat=51.686
)

# Retrieve and process changes
status = adiff.retrieve()
if status == 200:
    print(f"Created: {len(adiff.create)} features")
    print(f"Modified: {len(adiff.modify)} features")
    print(f"Deleted: {len(adiff.delete)} features")
```

## API Reference

::: osmdiff.augmenteddiff.AugmentedDiff
    options:
      heading_level: 2
      show_source: true
      members:
        - __init__
        - get_state
        - retrieve
        - sequence_number
        - timestamp
        - remarks
        - actions
        - __repr__
        - __enter__
        - __exit__

## See Also

- [ContinuousAugmentedDiff](continuous.md) - For continuous monitoring
- [OSMChange](osmchange.md) - For standard OSM changesets
