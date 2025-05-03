# ContinuousAugmentedDiff

An iterator that continuously monitors and yields new AugmentedDiffs as they become available.

::: osmdiff.augmenteddiff.ContinuousAugmentedDiff
    options:
      heading_level: 2
      show_source: true
      members:
        - __init__
        - __iter__
        - __next__

## Features

- Automatic sequence number tracking
- Exponential backoff during errors
- Configurable polling intervals
- Bounding box filtering

## Example Usage

```python
from osmdiff import ContinuousAugmentedDiff

# Monitor Paris area changes
monitor = ContinuousAugmentedDiff(
    minlon=2.224,
    minlat=48.815,
    maxlon=2.469,
    maxlat=48.902,
    min_interval=60  # Check every minute
)

for changes in monitor:
    print(f"New changeset {changes.sequence_number}:")
    print(f"  Creates: {len(changes.create)} features")
    print(f"  Modifies: {len(changes.modify)} features")
    print(f"  Deletes: {len(changes.delete)} features")
```

## Error Handling

The iterator automatically:
- Retries failed requests (up to 3 times)
- Increases polling interval during errors
- Resets to normal polling after success
