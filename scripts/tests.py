import unittest
from unittest.mock import Mock, patch
from main import ProductUpdater


class TestProductUpdater(unittest.TestCase):

    @patch('main.dbc')
    @patch('main.xc')
    @patch('main.Logger')
    def setUp(self, MockLogger, MockXmlConnector, MockDatabaseConnector):
        self.mock_module = Mock()
        self.mock_module.XML_URL = "some_url"
        self.mock_module.SUP_NAME = "some_name"

        self.updater = ProductUpdater(self.mock_module)

        self.mock_db_connector = MockDatabaseConnector()
        self.updater.db = self.mock_db_connector

        self.mock_xml_connector = MockXmlConnector()
        self.updater.xml = self.mock_xml_connector

        self.mock_logger = MockLogger()
        self.updater.logger = self.mock_logger

    


if __name__ == '__main__':
    unittest.main()
