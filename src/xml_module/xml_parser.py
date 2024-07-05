import xml.etree.ElementTree as ET

class XMLParser:
    
    def __init__(self, xml_file_path : str = None) -> None:
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
    
    def extract_data(self, config : dict ) -> dict:
        if self.xml is None:
            raise FileNotFoundError('XML file is not parsed')
        
        root_element = config.get('ROOT_ELEMENT', None)
        if root_element is None:
            raise ValueError('ROOT_ELEMENT is not set in config')
        
        product_element = config.get('PRODUCT_ROOT_ELEMENT', None)
        if product_element is None:
            raise ValueError('PRODUCT_ROOT_ELEMENT is not set in config')
        
        data = {}
        
        root = self.xml.getroot()
        products_root = root.find(root_element)
        
        for product in products_root.findall(product_element):
            data[product.get('id')] = "test"
        
        return data
            
        
        
    