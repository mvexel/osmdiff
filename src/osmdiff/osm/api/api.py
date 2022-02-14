from platform import node
from urllib.parse import urljoin
import requests
import xml.etree.ElementTree as ET
from osmdiff.osm.node import Node

class OSMAPI:

    @staticmethod
    def fetch(osm_type, id):
        OSM_API_BASE_URL = "https://osm.org/api/0.6/"
        url = urljoin(OSM_API_BASE_URL, '{}/{}'.format(osm_type, id))
        res = requests.get(url)
        return res.text


class OverpassAPI():

    @staticmethod
    def geometry_for_way(wayref):
        OVERPASS_API_BASE_URL = "https://overpass-api.de/"
        url = urljoin(
            OVERPASS_API_BASE_URL,
            'api/interpreter?data=way%28{}%29%3B%28._%3B%3E%3B%29%3Bout%3B'.format(wayref.id))
        res = requests.get(url)
        root = ET.ElementTree(ET.fromstring(res.text)).getroot()
        for noderef in root.findall('node'):
            wayref.nodes.append(Node(
                lon=noderef.attrib['lon'],
                lat=noderef.attrib['lat'],
                id=noderef.attrib['id']))

    def geometry_for_relation(relref):
        OVERPASS_API_BASE_URL = "https://overpass-api.de/"
        url = urljoin(
            OVERPASS_API_BASE_URL,
            'api/interpreter?data=rel%28{}%29%3B%28._%3B%3E%3B%29%3Bout%3B'.format(relref.id))
        res = requests.get(url)
        root = ET.ElementTree(ET.fromstring(res.text)).getroot()
        for r in root.findall('relation'):
            relref.nodes.append(Node(
                lon=noderef.attrib['lon'],
                lat=noderef.attrib['lat'],
                id=noderef.attrib['id']))
