import nextactions.cmdline as cmdline
import unittest
import os
import argparse
from unittest.mock import MagicMock, patch


@patch('nextactions.config.Config.loadFromFile')
class TestCmdLine(unittest.TestCase):

    def testNoOptionsLoadsDefaultConfig(self, load_from_file):
        cmdline.main(['sync'])
        expected_file = os.path.join(
            os.path.expanduser('~'), '.trellonextactions.json'
        )
        load_from_file.assert_called_once_with(expected_file)

    def testLoadDifferentConfig(self, load_from_file):
        expected_file = "test.txt"
        cmdline.main(['--config=' + expected_file, 'sync'])
        load_from_file.assert_called_once_with(expected_file)

    def testActionIsRequired(self, load_from_file):
        with self.assertRaises(SystemExit):
            cmdline.main([])

    def testUnknownAction(self, load_from_file):
        m = MagicMock()
        return_code = 0
        with patch('sys.stderr.write', m):
            return_code = cmdline.main(['unknown'])
        m.assert_called_once()
        self.assertEqual(return_code, 1)
