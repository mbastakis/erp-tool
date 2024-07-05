from xml_module.xml_parser import XMLParser

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

def test_parse_xml_correct_parse():
    xml_parser = XMLParser('tests/xml/test_data/pakoworld.xml')
    try:
        xml = xml_parser.parse_xml()
        assert xml_parser.xml is not None
        assert xml is not None
        assert xml is xml_parser.xml
    except FileNotFoundError as e:
        assert False