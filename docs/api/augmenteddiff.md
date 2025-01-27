# AugmentedDiff

This class is used to represent an OSM Augmented Diff. For more information about OSM Augmented Diffs, see the [Augmented Diff](https://wiki.openstreetmap.org/wiki/Overpass_API/Augmented_Diffs) page on the OpenStreetMap Wiki.

Basic usage:

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
