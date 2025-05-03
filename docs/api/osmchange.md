# OSMChange

Handles OpenStreetMap changesets in OSMChange format.

::: osmdiff.osmchange.OSMChange
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2
      members: true
      show_signature_annotations: true
      show_signature: true
      show_bases: false

## Usage Example

```python
from osmdiff import OSMChange

# Create from sequence number
osm_change = OSMChange(sequence_number=12345)

# Or from local file
osm_change = OSMChange(file="changeset.xml")

# Retrieve changes
osm_change.retrieve()

# Access changes
creations = osm_change.actions["create"]
modifications = osm_change.actions["modify"]
deletions = osm_change.actions["delete"]
```

## Key Features

- Retrieves changesets from OSM replication servers
- Parses OSMChange XML format
- Handles create/modify/delete actions
- Supports both remote and local file sources
- Context manager support for resource cleanup
- Sequence number management

## Configuration

The following configuration options are available via constructor arguments:

- `url`: Base URL of OSM replication server
- `frequency`: Replication frequency ('minute', 'hour', or 'day')
- `file`: Path to local OSMChange XML file  
- `sequence_number`: Sequence number of the diff
- `timeout`: Request timeout in seconds

