import unittest
from nextactions.board import Board
from nextactions.trello import Trello
from unittest.mock import MagicMock


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.trello = Trello(None)
        json = {'id': "123", 'name': "Test"}
        self.board = Board(self.trello, json)

    def testGetListsOnEmptyBoard(self):
        self.trello.get = MagicMock(return_value=[])
        self.assertEqual(self.board.getLists(), [])

    def testGetListsWithSingleResult(self):
        self._fakeSuccessResponse()
        lists = self.board.getLists()
        self.assertEqual(len(lists), 1)
        self.assertEqual(lists[0].id, "123")

    def _fakeSuccessResponse(self):
        fake_json = [{'id': "123", 'name': "Next Actions"}]
        self.trello.get = MagicMock(return_value=fake_json)

    def testGetNonExistentListByName(self):
        self.trello.get = MagicMock(return_value=[])
        self.assertEqual(self.board.getListByName('test'), None)

    def testGetListByName(self):
        self._fakeSuccessResponse()
        next_actions = self.board.getListByName('Next Actions')
        self.assertEqual(next_actions.name, 'Next Actions')
