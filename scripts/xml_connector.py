import requests


class XmlConnector:
    def __init__(self, url):
        self.url = url

    def download_xml(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.xml_string = response.content
            return True
        else:
            return False

    def get_xml(self):
        return self.xml_string
