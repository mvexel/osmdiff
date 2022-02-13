from sys import unraisablehook
from urllib.parse import urljoin
import requests

class API:

    OSM_API_BASE_URL = "https://osm.org/api/0.6/"

    def __init__(self) -> None:
        pass

    def fetch(self, osm_type, id):
        url = urljoin(self.OSM_API_BASE_URL, '{}/{}'.format(osm_type, id))
        res = requests.get(url)
        return res.text
