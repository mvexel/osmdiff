from xml.etree import ElementTree


class OSMAPI:
    @staticmethod
    def fetch(osm_type, osm_id):
        import requests

        url = "https://osm.org/api/0.6/{}/{}".format(osm_type, osm_id)
        res = requests.get(url)
        return res.text

    @staticmethod
    def from_xml(xml):
        from osmdiff.osm import Node, Way, Relation
        if isinstance(xml, ElementTree.Element):
            root = xml
        else:
            root = ElementTree.ElementTree(ElementTree.fromstring(xml)).getroot()
        if root.tag == "osm":
            elem = root[0]
        else:
            elem = root
        if elem.tag == "node":
            o = Node(
                lon=float(elem.attrib["lon"]),
                lat=float(elem.attrib["lat"]),
                osm_id=int(elem.attrib["id"]),
            )
        elif elem.tag == "nd":
            o = Node(osm_id=int(elem.attrib["ref"]))
        elif elem.tag == "way":
            o = Way(osm_id=int(elem.attrib["id"]))
            for nd in elem.findall("nd"):
                o.nodes.append(Node(osm_id=nd.attrib.get("id")))
        elif elem.tag == "relation":
            o = Relation(osm_id=int(elem.attrib["id"]))
            # parse members
            for member in elem.findall("member"):
                role = member.attrib.get("role")
                osm_type = member.attrib.get("type")
                osm_id = member.attrib.get("ref")
                if osm_type == "node":
                    o.members.append(Node(osm_id=osm_id, role=role))
                elif osm_type == "way":
                    o.members.append(Way(osm_id=osm_id, role=role))
                elif osm_type == "relation":
                    o.members.append(Relation(osm_id=osm_id, role=role))
        for tag_element in elem.findall("tag"):
            o.tags[tag_element.attrib["k"]] = tag_element.attrib["v"]
        o.attributes = elem.attrib

        return o
