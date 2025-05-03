# Augmented Diffs

This module provides classes for working with OSM Augmented Diffs. For more information about OSM Augmented Diffs, see the [Augmented Diff](https://wiki.openstreetmap.org/wiki/Overpass_API/Augmented_Diffs) page on the OpenStreetMap Wiki.

## AugmentedDiff

Basic usage of the AugmentedDiff class:

```python
>>> from osmdiff import AugmentedDiff
>>> ad = AugmentedDiff()
>>> ad.get_state()
True
>>> ad.sequence_number
6509700
>>> ad.retrieve()
200
>>> ad.sequence_number
6509701
>>> ad
AugmentedDiff (2776 created, 927 modified, 6999 deleted)
>>> ad.retrieve()
200
>>> ad.sequence_number
6509702
>>> ad
AugmentedDiff (3191 created, 1724 modified, 7077 deleted)  # the results of the two calls to retrieve() are merged
```

::: osmdiff.augmenteddiff.AugmentedDiff
    options:
      show_root_heading: true
      show_source: false

## ContinuousAugmentedDiff

The ContinuousAugmentedDiff class provides an iterator interface for continuously fetching augmented diffs as they become available. It handles timing, backoff, and error recovery automatically.

Basic usage:

```python
>>> from osmdiff import ContinuousAugmentedDiff
>>> # Create fetcher for London area
>>> fetcher = ContinuousAugmentedDiff(
...     minlon=-0.489,
...     minlat=51.28,
...     maxlon=0.236,
...     maxlat=51.686
... )
>>> # Iterate over diffs as they become available
>>> for diff in fetcher:
...     print(f"Got diff {diff.sequence_number} with {len(diff.create)} creates")
Got diff 6509701 with 2776 creates
Got diff 6509702 with 3191 creates
# ... continues until interrupted
```

::: osmdiff.augmenteddiff.ContinuousAugmentedDiff
    options:
      show_root_heading: true
      show_source: false
