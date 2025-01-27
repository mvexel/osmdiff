# OpenStreetMap (OSM) Module

This module provides classes for working with OpenStreetMap data in the application.

## Classes

### OSMNode

Represents a node in OpenStreetMap data structure.

#### Properties
- `id` (int): Unique identifier for the node
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate
- `tags` (dict): Dictionary of key-value pairs containing node metadata

### OSMWay

Represents a way (path, road, or area boundary) in OpenStreetMap data structure.

#### Properties
- `id` (int): Unique identifier for the way
- `nodes` (list): List of node IDs that make up the way
- `tags` (dict): Dictionary of key-value pairs containing way metadata

### OSMRelation

Represents a relation in OpenStreetMap data structure, which defines logical or geographic relationships between other elements.

#### Properties
- `id` (int): Unique identifier for the relation
- `members` (list): List of member elements (nodes, ways, or other relations)
- `tags` (dict): Dictionary of key-value pairs containing relation metadata

### OSMData

Main class for handling OpenStreetMap data.

#### Methods

##### `__init__(self)`
Initializes an empty OSM data container.

##### `add_node(self, node)`
Adds a node to the OSM data.

Parameters:
- `node` (OSMNode): Node object to add

##### `add_way(self, way)`
Adds a way to the OSM data.

Parameters:
- `way` (OSMWay): Way object to add

##### `add_relation(self, relation)`
Adds a relation to the OSM data.

Parameters:
- `relation` (OSMRelation): Relation object to add

##### `get_node(self, node_id)`
Retrieves a node by its ID.

Parameters:
- `node_id` (int): ID of the node to retrieve

Returns:
- OSMNode or None: The requested node if found, None otherwise

##### `get_way(self, way_id)`
Retrieves a way by its ID.

Parameters:
- `way_id` (int): ID of the way to retrieve

Returns:
- OSMWay or None: The requested way if found, None otherwise

##### `get_relation(self, relation_id)`
Retrieves a relation by its ID.

Parameters:
- `relation_id` (int): ID of the relation to retrieve

Returns:
- OSMRelation or None: The requested relation if found, None otherwise
