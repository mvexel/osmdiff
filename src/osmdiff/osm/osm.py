"""
# OSM Objects

This module provides classes for working with OpenStreetMap data in the application.

::: osmdiff.osm.Member

::: osmdiff.osm.OSMNode

::: osmdiff.osm.OSMWay

::: osmdiff.osm.OSMRelation

::: osmdiff.osm.OSMData

## Overview

This module contains base classes for OSM objects:
- OSMObject: Base class for all OSM elements
- Node: Represents OSM nodes with lat/lon coordinates
- Way: Represents OSM ways (sequences of nodes)
- Relation: Represents OSM relations (collections of objects)

## Example

```python
from osmdiff.osm import Node, Way, Relation
```

Each OSM object has:
- tags: Dictionary of key-value tag pairs
- attribs: Dictionary of XML attributes (id, version, etc.)
- bounds: Optional bounding box [minlon, minlat, maxlon, maxlat]

The objects can be created from XML elements using the from_xml() classmethod.

Example:
# Create a node
node = Node()
node.attribs = {
    "id": "123", 
    "version": "2",
    "lat": "37.7", 
    "lon": "-122.4"
}
node.tags = {
    "amenity": "cafe",
    "name": "Joe's Coffee"
}

# Create a way
way = Way() 
way.attribs = {
    "id": "456",
    "version": "1"
}
way.nodes = ["123", "124", "125"]  # List of node IDs
way.tags = {
    "highway": "residential",
    "name": "Oak Street"
}

# Create a relation
rel = Relation()
rel.attribs = {
    "id": "789",
    "version": "1"
}
rel.members = [
    {"type": "way", "ref": "456", "role": "outer"},
    {"type": "way", "ref": "457", "role": "inner"}
]
rel.tags = {
    "type": "multipolygon",
    "landuse": "park"
}
```

# Access __geo_interface__ for GeoJSON compatibility

See https://gist.github.com/sgillies/2217756 for more details.

```python
print(node.__geo_interface__) # {"type": "Point", "coordinates": [-0.1, 51.5]}
```
"""

from typing import Dict, Any, List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import json


class OSMObject:
    """
    Base class for OpenStreetMap objects.

    Parameters:
        tags (dict): OSM tags (key-value pairs)
        attribs (dict): XML attributes
        bounds (list): Bounding box [minlon, minlat, maxlon, maxlat]

    Attributes:
        tags (dict): OSM tags (key-value pairs)
        attribs (dict): XML attributes
        bounds (list): Bounding box [minlon, minlat, maxlon, maxlat]

    Methods:
        from_xml: Create object from XML element
        _parse_tags: Parse tags from XML
        _parse_bounds: Parse bounds from XML

    Raises:
        ValueError: If XML element is invalid
        TypeError: If element type is unknown

    Example:
    ```python
    node = Node()
    node.attribs = {"lon": "0.0", "lat": "51.5"}
    ```
    """

    def __init__(
        self,
        tags: Dict[str, str] = {},
        attribs: Dict[str, str] = {},
        bounds: List[float] = None,
    ) -> None:
        """Initialize an empty OSM object."""
        self.tags = tags or {}
        self.attribs = attribs or {}
        self.bounds = bounds or None

    def __repr__(self) -> str:
        """
        String representation of the OSM object.

        Returns:
            str: Object type and ID, with additional info for ways/relations
        """
        out = "{type} {id}".format(type=type(self).__name__, id=self.attribs.get("id"))
        if type(self) == Way:
            out += " ({ways} nodes)".format(ways=len(self.nodes))
        if type(self) == Relation:
            out += " ({mem} members)".format(mem=len(self.members))
        return out

    def _parse_tags(self, elem: Element) -> None:
        """
        Parse tags from XML element.

        Args:
            elem: XML element containing tag elements
        """
        for tagelem in elem.findall("tag"):
            self.tags[tagelem.attrib["k"]] = tagelem.attrib["v"]

    def _parse_bounds(self, elem: Element) -> None:
        """
        Parse bounds from XML element.

        Args:
            elem: XML element containing bounds element
        """
        be = elem.find("bounds")
        if be is not None:
            self.bounds = [
                be.attrib["minlon"],
                be.attrib["minlat"],
                be.attrib["maxlon"],
                be.attrib["maxlat"],
            ]

    @classmethod
    def from_xml(cls, elem: Element) -> "OSMObject":
        """
        Create OSM object from XML element.

        Args:
            elem: XML element representing an OSM object

        Returns:
            OSMObject: Appropriate subclass instance

        Raises:
            ValueError: If XML element is invalid
            TypeError: If element type is unknown
        """
        if elem is None:
            raise ValueError("XML element cannot be None")

        osmtype = ""
        if elem.tag == "member":
            osmtype = elem.attrib.get("type")
            if not osmtype:
                raise ValueError("Member element missing type attribute")
        else:
            osmtype = elem.tag

        if osmtype not in ("node", "nd", "way", "relation"):
            raise TypeError(f"Unknown OSM element type: {osmtype}")

        if osmtype in ("node", "nd"):
            o = Node()
        elif osmtype == "way":
            o = Way()
            o._parse_nodes(elem)
        elif osmtype == "relation":
            o = Relation()
            o._parse_members(elem)
        else:
            pass
        o.attribs = elem.attrib
        o._parse_tags(elem)
        o._parse_bounds(elem)
        return o

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert object to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "type": self.__class__.__name__,
            "id": self.attribs.get("id"),
            "tags": self.tags,
            "bounds": self.bounds,
        }

    def to_json(self) -> str:
        """
        Convert object to JSON string.

        Returns:
            str: JSON representation
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_file(cls, filename: str) -> "OSMObject":
        """
        Create object from XML file.

        Args:
            filename: Path to XML file

        Returns:
            OSMObject: Parsed object
        """
        with open(filename, "r") as f:
            tree = ElementTree.parse(f)
            return cls.from_xml(tree.getroot())


class Node(OSMObject):
    """
    Represents an OSM node (point feature).

    ## Attributes
        lon (float): Longitude
        lat (float): Latitude
        __geo_interface__ (dict): GeoJSON-compatible interface, see https://gist.github.com/sgillies/2217756 for more details.

    ## Example
    ```python
    node = Node()
    node.attribs = {"lon": "0.0", "lat": "51.5"}
    print(node.lon, node.lat)  # 0.0, 51.5
    ```
    """

    def __init__(
        self,
        tags: Dict[str, str] = {},
        attribs: Dict[str, str] = {},
        bounds: List[float] = None,
    ):
        super().__init__(tags, attribs, bounds)

    def _validate_coords(self) -> None:
        """Validate node coordinates."""
        lon = float(self.attribs.get("lon", 0))
        lat = float(self.attribs.get("lat", 0))
        if not -90 <= lat <= 90:
            raise ValueError(f"Invalid latitude: {lat}")
        if not -180 <= lon <= 180:
            raise ValueError(f"Invalid longitude: {lon}")

    @property
    def lon(self) -> float:
        """Get longitude value."""
        self._validate_coords()
        return float(self.attribs.get("lon", 0))

    @property
    def lat(self) -> float:
        """Get latitude value."""
        self._validate_coords()
        return float(self.attribs.get("lat", 0))

    def _geo_interface(self):
        """
        GeoJSON-compatible interface.

        Returns:
            dict: GeoJSON Point geometry
        """
        return {"type": "Point", "coordinates": [self.lon, self.lat]}

    __geo_interface__ = property(_geo_interface)

    def __eq__(self, other) -> bool:
        """
        Check if two nodes are equal.

        Args:
            other (OSMObject): Another OSMObject object

        Returns:
            bool: True if nodes have same coordinates
        """
        if not isinstance(other, Node):
            return False
        return self.lon == other.lon and self.lat == other.lat


class Way(OSMObject):
    """
    Represents an OSM way (linear feature).

    ## Attributes
        nodes (list): List of Node objects
        __geo_interface__ (dict): GeoJSON-compatible interface, see https://gist.github.com/sgillies/2217756 for more details.
    ## Example
    ```python
    way = Way()
    way.nodes = [Node(), Node()]  # Add nodes
    print(way.__geo_interface__["type"])  # "LineString" or "Polygon"
    ```
    """

    def __init__(
        self,
        tags: Dict[str, str] = {},
        attribs: Dict[str, str] = {},
        bounds: List[float] = None,
    ):
        super().__init__(tags, attribs, bounds)
        self.nodes = []

    def is_closed(self) -> bool:
        """
        Check if the way forms a closed loop.

        Returns:
            bool: True if first and last nodes are identical
        """
        return bool(self.nodes and self.nodes[0] == self.nodes[-1])

    def length(self) -> float:
        """
        Calculate approximate length in meters.

        Returns:
            float: Length of way in meters
        """
        # Implementation using haversine formula
        pass

    def _parse_nodes(self, elem: Element):
        """
        Parse nodes from XML element.

        Args:
            elem: XML element containing nd elements
        """
        for node in elem.findall("nd"):
            self.nodes.append(OSMObject.from_xml(node))

    def _geo_interface(self):
        """
        GeoJSON-compatible interface.

        Returns:
            dict: GeoJSON LineString or Polygon geometry
        """
        geom_type = "Polygon" if self.is_closed() else "LineString"
        coordinates = [[n.lon, n.lat] for n in self.nodes]

        # For Polygon, we need to wrap coordinates in an extra list
        if geom_type == "Polygon":
            coordinates = [coordinates]

        return {"type": geom_type, "coordinates": coordinates}

    __geo_interface__ = property(_geo_interface)


class Relation(OSMObject):
    """
    Represents an OSM relation (collection of features).

    ## Attributes
        members (list): List of member objects
        __geo_interface__ (dict): GeoJSON-compatible interface, see https://gist.github.com/sgillies/2217756 for more details.

    ## Example
    ```python
    relation = Relation()
    relation.members = [Way(), Node()]  # Add members
    print(relation.__geo_interface__["type"])  # "FeatureCollection"
    ```
    """

    def __init__(
        self,
        tags: Dict[str, str] = {},
        attribs: Dict[str, str] = {},
        bounds: List[float] = None,
    ):
        super().__init__(tags, attribs, bounds)
        self.members = []

    def _parse_members(self, elem: Element):
        """
        Parse members from XML element.

        Args:
            elem: XML element containing member elements
        """
        for member in elem.findall("member"):
            self.members.append(OSMObject.from_xml(member))

    def _geo_interface(self):
        """
        GeoJSON-compatible interface.

        Returns:
            dict: GeoJSON GeometryCollection
        """
        return {
            "type": "GeometryCollection",
            "geometries": [m.__geo_interface__ for m in self.members],
        }

    __geo_interface__ = property(_geo_interface)


class Member(OSMObject):
    """
    Represents an OSM member (a feature within a relation).
    """

    def __init__(self):
        """Initialize an empty member."""
        self.type = None
        self.ref = None
        self.role = None
        super().__init__()

    def _parse_attributes(self, elem: Element):
        """
        Parse member attributes from XML element.

        Args:
            elem: XML element containing member attributes
        """
        self.type = elem.get("type")
        self.ref = int(elem.get("ref"))
        self.role = elem.get("role")

    def _geo_interface(self):
        """
        GeoJSON-compatible interface.

        Returns:
            dict: GeoJSON Feature
        """
        return {
            "type": "Feature",
            "geometry": None,
            "properties": {"type": self.type, "ref": self.ref, "role": self.role},
        }

    __geo_interface__ = property(_geo_interface)
