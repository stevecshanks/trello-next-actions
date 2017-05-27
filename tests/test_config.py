import json
import unittest
import nextactions
from nextactions.config import Config
from unittest.mock import MagicMock


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.config._doesFileExist = MagicMock(return_value=True)

    def testGetFromEmptyConfig(self):
        self.assertEqual(self.config.get("test"), None)

    def testGetAndSet(self):
        self.config.set("one", "1")
        self.config.set("two", "2")
        self.assertEqual(self.config.get("one"), "1")
        self.assertEqual(self.config.get("two"), "2")
        self.assertEqual(self.config.get("three"), None)

    def testLoadFromFile(self):
        file_values = {'one': "1", 'two': "2"}
        file_name = "myFile.cfg"
        self.config._getValuesFromFile = MagicMock(return_value=file_values)

        self.config.loadFromFile(file_name)

        self.config._getValuesFromFile.assert_called_once_with(file_name)
        for key, value in file_values.items():
            self.assertEqual(self.config.get(key), value)

    def testLoadFromNonExistentFile(self):
        self.config._doesFileExist = MagicMock(return_value=False)
        with self.assertRaises(FileNotFoundError):
            self.config.loadFromFile("test")

    def testLoadFromInvalidFile(self):
        json_error = json.decoder.JSONDecodeError("", "", 0)
        self.config._getValuesFromFile = MagicMock(side_effect=json_error)

        with self.assertRaises(nextactions.config.ParseError):
            self.config.loadFromFile("test")
