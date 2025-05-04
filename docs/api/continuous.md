# ContinuousAugmentedDiff

Iterator for continuous monitoring of OpenStreetMap changes using augmented diffs.

Builds on [AugmentedDiff](augmenteddiff.md) to provide automatic polling with backoff.

## Features

- Continuous monitoring
- Automatic sequence number tracking
- Exponential backoff during errors
- Configurable polling intervals
- Bounding box filtering

## Basic Usage

```python
from osmdiff import ContinuousAugmentedDiff

# Monitor London area
monitor = ContinuousAugmentedDiff(
    minlon=-0.489,
    minlat=51.28,
    maxlon=0.236,
    maxlat=51.686
)

for changes in monitor:  # Runs indefinitely
    print(f"Changeset {changes.sequence_number}:")
    print(f"  New: {len(changes.create)}")
    print(f"  Modified: {len(changes.modify)}")
```

## Advanced Configuration

```python
monitor = ContinuousAugmentedDiff(
    minlon=-0.489,
    minlat=51.28,
    maxlon=0.236,
    maxlat=51.686,
    min_interval=60,  # Minimum 1 minute between checks
    max_interval=300  # Maximum 5 minutes during backoff
)
```

## API Reference

::: osmdiff.augmenteddiff.ContinuousAugmentedDiff
    options:
      heading_level: 2
      show_source: true
      members:
        - __init__
        - __iter__
        - __next__

## See Also

- [AugmentedDiff](augmenteddiff.md) - For single diff retrieval
- [OSMChange](osmchange.md) - For standard changesets
