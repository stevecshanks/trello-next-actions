import nextactions.cmdline as cmdline
import unittest
import os
from unittest.mock import MagicMock, patch, call


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
        return_code = None
        with patch('sys.stderr.write', m):
            return_code = cmdline.main(['unknown'])
        m.assert_called_once()
        self.assertEqual(return_code, 1)

    def testSyncAction(self, load_from_file):
        m = MagicMock(return_value=([], []))
        return_code = None
        with patch('nextactions.synctool.SyncTool.sync', m):
            return_code = cmdline.main(['sync'])
        m.assert_called_once()
        self.assertEqual(return_code, 0)

    def testResetAction(self, load_from_file):
        m = MagicMock(return_value=[])
        return_code = None
        with patch('nextactions.synctool.SyncTool.reset', m):
            return_code = cmdline.main(['reset'])
        m.assert_called_once()
        self.assertEqual(return_code, 0)

    def testPrintEmptyList(self, load_from_file):
        m = MagicMock()
        with patch('nextactions.cmdline.print', m):
            cmdline.print_card_list('Test', [])
        m.assert_not_called()

    @patch('nextactions.card.Card')
    def testPrintList(self, load_from_file, card):
        card.id = "123"
        card.name = "Test"
        m = MagicMock()
        with patch('nextactions.cmdline.print', m):
            cmdline.print_card_list('Test', [card])
        m.assert_has_calls([
            call('Test:'),
            call(),
            call(" - Test (123)"),
            call()
        ])
