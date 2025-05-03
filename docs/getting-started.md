# Getting Started with OSMDiff

OSMDiff helps you work with OpenStreetMap change data. OpenStreetMap (OSM) is a collaborative map that's constantly updated by volunteers. These updates come in different formats:

- **Augmented Diffs**: Detailed changes including metadata about who made changes and why
- **OSMChange**: Standard format for basic create/modify/delete operations

## Installation

```bash
pip install osmdiff
```

## Basic Usage

Track changes in a specific area (here using London as an example):

```python
from osmdiff import AugmentedDiff

# Create an AugmentedDiff instance for London
ad = AugmentedDiff(
    minlon=-0.489,  # West
    minlat=51.28,   # South 
    maxlon=0.236,   # East
    maxlat=51.686   # North
)

# Get current state and retrieve changes
ad.get_state()
status = ad.retrieve()

if status == 200:
    print(f"Changes retrieved:")
    print(f"  Created: {len(ad.create)}")
    print(f"  Modified: {len(ad.modify)}")
    print(f"  Deleted: {len(ad.delete)}")
```

## Continuous Monitoring

For real-time monitoring of changes:

```python
from osmdiff import ContinuousAugmentedDiff

# Create continuous fetcher for London area
fetcher = ContinuousAugmentedDiff(
    minlon=-0.489,
    minlat=51.28, 
    maxlon=0.236,
    maxlat=51.686,
    min_interval=30,  # Check at least every 30 seconds
    max_interval=120  # Back off up to 120 seconds if no changes
)

# Process changes as they come in
for diff in fetcher:
    print(f"\nNew changes in diff {diff.sequence_number}:")
    print(f"  Created: {len(diff.create)} objects")
    print(f"  Modified: {len(diff.modify)} objects")
    print(f"  Deleted: {len(diff.delete)} objects")
    
    # Example: Track new amenities
    for obj in diff.create:
        if "amenity" in obj.tags:
            print(f"New amenity: {obj.tags['amenity']}")
```

## Next Steps

- Learn about [AugmentedDiff API](/api/augmenteddiff)
- Explore [OSMChange format](/api/osmchange)
- See [OSM Objects](/api/osm) you can work with
