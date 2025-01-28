from shapely.geometry import shape
from osmdiff.osm import Node, Way, Relation

# Create a node with coordinates
node = Node()
node.attribs = {"lon": "-122.4", "lat": "37.7"}

# Convert to Shapely Point using geo_interface
point = shape(node.__geo_interface__)
print(f"Node as Point: {point}")  # POINT (-122.4 37.7)

# Create a way with nodes
way = Way()
way.nodes = [
    Node(attribs={"lon": "-122.4", "lat": "37.7"}),
    Node(attribs={"lon": "-122.4", "lat": "37.8"}),
    Node(attribs={"lon": "-122.5", "lat": "37.8"}),
    Node(attribs={"lon": "-122.4", "lat": "37.7"}),  # Closing the loop
]

# Convert to Shapely Polygon using geo_interface
polygon = shape(way.__geo_interface__)
print(
    f"Way as Polygon: {polygon}"
)  # POLYGON ((-122.4 37.7, -122.4 37.8, -122.5 37.8, -122.4 37.7))

# Create a relation with members
relation = Relation()
relation.members = [way, node]

# Convert to Shapely GeometryCollection using geo_interface
collection = shape(relation.__geo_interface__)
print(
    f"Relation as Collection: {collection}"
)  # GEOMETRYCOLLECTION (POLYGON ((-122.4 37.7, -122.4 37.8, -122.5 37.8, -122.4 37.7)), POINT (-122.4 37.7))
