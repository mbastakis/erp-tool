import requests

class XmlConnector:
    def __init__(self, url):
        self.url = url
        self.xml_string = None

    def download_xml(self):
        try:
            print(f"Attempting to download XML from: {self.url}")  # Add this line to print the URL
            response = requests.get(self.url)
            response.raise_for_status()
            if response.status_code == 200:
                self.xml_string = response.content
                return True
            else:
                print(f"Failed to download XML: HTTP {response.status_code}")
                return False
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error occurred: {e}")
            return False
        except requests.exceptions.Timeout as e:
            print(f"Timeout error occurred: {e}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return False

    def get_xml(self):
        if self.xml_string:
            return self.xml_string
        else:
            print("No XML data available.")
            return None
