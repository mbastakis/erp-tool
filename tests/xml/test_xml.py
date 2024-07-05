import pytest
from xml_module.xml_parser import XMLParser

@pytest.fixture
def expected_config():
    return {
        "ROOT_ELEMENT": "products",
        "PRODUCT_ROOT_ELEMENT": "product",
    }

def test_create_xml_parser():
    xml_parser = XMLParser()
    assert xml_parser is not None

def test_create_xml_parser_with_xml():
    xml_parser = XMLParser('tests/xml/test_data/pakoworld.xml')
    assert xml_parser is not None
    assert xml_parser.xml_file_path == 'tests/xml/test_data/pakoworld.xml'
    assert xml_parser.xml is None
    
def test_parse_xml_throw_FileNotFoundException():
    xml_parser = XMLParser('not_exists.xml')
    try:
        xml_parser.parse_xml()
        assert False
    except FileNotFoundError as e:
        assert xml_parser.xml is None
        assert True

def test_xml_parser_parse_xml():
    xml_parser = XMLParser('tests/xml/test_data/pakoworld.xml')
    try:
        xml = xml_parser.parse_xml()
        assert xml_parser.xml is not None
        assert xml is not None
        assert xml is xml_parser.xml
    except FileNotFoundError as e:
        assert False
    
def test_xml_parser_extract_data_easy( expected_config ):
    xml_parser = XMLParser('tests/xml/test_data/easy_test.xml')
    xml_parser.parse_xml()
    
    data = xml_parser.extract_data(expected_config)
    
    assert data is not None
    assert len(data.keys()) == 1
    
def test_xml_parser_extract_data_pakoworld( expected_config ):
    xml_parser = XMLParser('tests/xml/test_data/pakoworld.xml')
    xml_parser.parse_xml()
    
    data = xml_parser.extract_data(expected_config)
    
    assert data is not None
    assert len(data.keys()) == 42
    

def test_xml_parser_extract_data_with_empty_xml( expected_config ):
    xml_parser = XMLParser('tests/xml/test_data/empty.xml')
    xml_parser.parse_xml()
    
    data = xml_parser.extract_data(expected_config)     
    
    assert data is not None
    assert len(data.keys()) == 0