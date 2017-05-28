import json
import unittest
import nextactions
import os
from nextactions.config import Config
from unittest.mock import MagicMock, patch, mock_open


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def testGetFromEmptyConfig(self):
        self.assertEqual(self.config.get("test"), None)

    def testGetAndSet(self):
        self.config.set("one", "1")
        self.config.set("two", "2")
        self.assertEqual(self.config.get("one"), "1")
        self.assertEqual(self.config.get("two"), "2")
        self.assertEqual(self.config.get("three"), None)

    def testLoadFromFile(self):
        m = mock_open(read_data='{"one": "1", "two": "2"}')
        with patch('nextactions.config.open', m):
                self.config.loadFromFile("test")
        m.assert_called_once_with("test", 'r')
        self.assertEqual(self.config.get('one'), "1")
        self.assertEqual(self.config.get('two'), "2")

    def testLoadFromNonExistentFile(self):
        m = mock_open()
        with patch('nextactions.config.open', m):
            m.side_effect = FileNotFoundError()
            with self.assertRaises(FileNotFoundError):
                self.config.loadFromFile("test")

    def testLoadFromInvalidFile(self):
        m = mock_open(read_data='{"one": "1", "}')
        with patch('nextactions.config.open', m):
            with self.assertRaises(nextactions.config.ParseError):
                self.config.loadFromFile("test")
