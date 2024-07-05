import xml.etree.ElementTree as ET

class XMLParser:
    
    def __init__(self, xml_file_path=None) -> None:
        self.xml_file_path = xml_file_path
        self.xml = None
    
    def parse_xml(self) -> ET.ElementTree:
        if self.xml_file_path is None:
            raise FileNotFoundError('XML file path is not set')
        
        try:
            self.xml = ET.parse(self.xml_file_path)
            return self.xml
        except FileNotFoundError as e:
            raise e
        