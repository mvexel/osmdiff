class OSMAPI:

    @staticmethod
    def fetch(osm_type, id):
        import requests
        url = 'https://osm.org/api/0.6/{}/{}'.format(osm_type, id)
        res = requests.get(url)
        return res.text


class OverpassAPI():

    @staticmethod
    def geometry_for_way(wayref):
        import requests
        import xml.etree.ElementTree as ET
        url = 'https://overpass-api.de/api/interpreter?data=way%28{}%29%3B%28._%3B%3E%3B%29%3Bout%3B'.format(
            wayref.id)
        res = requests.get(url)
        root = ET.ElementTree(ET.fromstring(res.text)).getroot()
        for noderef in root.findall('node'):
            wayref.nodes.append(Node(
                lon=noderef.attrib['lon'],
                lat=noderef.attrib['lat'],
                id=noderef.attrib['id']))

    @staticmethod
    def fetch_relation(rel_id):
        import requests
        import xml.etree.ElementTree as ET
        from osmdiff.osm.relation import Relation
        url = 'https://overpass-api.de/api/interpreter?data=rel%28{}%29%3B%28._%3B%3E%3B%29%3Bout%3B'.format(rel_id)
        res = requests.get(url)
        root = ET.ElementTree(ET.fromstring(res.text)).getroot()
        rel_elem = [r for r in root.findall('relation') if int(r.attrib['id']) == rel_id][0]
        the_rel = Relation(id=rel_id)
        members = rel_elem.findall('member')
        the_rel.elements.append(OverpassAPI._parse_members(members))
        return the_rel

    @staticmethod
    def _parse_members(members):
        from osmdiff.osm.node import Node
        from osmdiff.osm.way import Way
        from osmdiff.osm.relation import Relation
        from osmdiff.osm.member import ElementReference
        relation_members = []
        relation_elements = []
        for member in members:
            ref = int(member.attrib['ref'])
            role = member.attrib['role']
            osmtype = member.attrib['type']
            # add member to members list
            relation_members.append(ElementReference(id=ref, osmtype=osmtype, role=role))
            # fetch element
            element = None
            if osmtype == 'node':
                element = Node(id=ref)
            elif osmtype == 'way':
                element = Way(id=ref)
                # find nodes
                way_elem = [w for w in root.findall('way') if int(w.attrib['id']) == ref][0]
                for nd in way_elem.findall('nd'):
                    nd_ref = int(nd.attrib['ref'])
                    nd_elem = [n for n in root.findall('node') if int(n.attrib['id']) == nd_ref][0]
                    element.nodes.append(Node(
                        id=nd_ref,
                        lon=nd_elem.attrib['lon'],
                        lat=nd_elem.attrib['lat']))
            elif osmtype == 'relation' and ref is not rel_id:
                element = Relation(id=ref)
            else:
                continue
            relation_elements.append(element)