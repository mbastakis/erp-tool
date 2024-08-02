import json
from config_module.config import Config

def test_create_config_throw_FileNotFoundException():
    try:
        Config()
        assert False
    except FileNotFoundError:
        assert True

def test_create_config_with_json():
    json_path = 'tests/config/test_data/test.json'
    config = Config(json_path)
    assert config is not None
    
    test_json = json.load(open(json_path, 'r'))
    assert config.data == test_json

def test_config_values():
    json_path = 'tests/config/test_data/test.json'
    config = Config(json_path)
    assert config is not None
    
    test_json = json.load(open(json_path, 'r'))
    assert config.data == test_json
    
    assert config.data['test-key'] == 'test-value'
    assert config.data['test-array'] == ['test-value-1', 'test-value-2']
    assert config.data['test-object']['test-key-1'] == 'test-value-1'
    assert config.data['test-object']['test-key-2'] == 'test-value-2'
    assert config.data['test-boolean'] is True
    assert config.data['test-number'] == 123