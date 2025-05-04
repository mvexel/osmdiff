from osmdiff import ContinuousAugmentedDiff

# Create continuous fetcher for London area
fetcher = ContinuousAugmentedDiff(
    minlon=-0.489,
    minlat=51.28,
    maxlon=0.236,
    maxlat=51.686,
    min_interval=30,  # Check at least every 30 seconds
    max_interval=120,  # Back off up to 120 seconds if no changes
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
