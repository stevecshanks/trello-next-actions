import unittest
from nextactions.board import Board
from nextactions.trello import Trello
from unittest.mock import MagicMock


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.trello = Trello(None)
        json = {'id': "123", 'name': "Test"}
        self.board = Board(self.trello, json)

    def testGetListsCallsAPICorrectly(self):
        mock = self._mockGetResponse()
        self.board.getLists()
        mock.assert_called_once_with(
            'https://api.trello.com/1/boards/123/lists',
            {'cards': "none"}
        )

    def _mockGetResponse(self):
        fake_json = [{'id': "123", 'name': "Next Actions"}]
        mock = MagicMock(return_value=fake_json)
        self.trello.get = mock
        return mock

    def testGetListsOnEmptyBoard(self):
        self.trello.get = MagicMock(return_value=[])
        self.assertEqual(self.board.getLists(), [])

    def testGetListsWithSingleResult(self):
        self._mockGetResponse()
        lists = self.board.getLists()
        self.assertEqual(len(lists), 1)
        self.assertEqual(lists[0].id, "123")

    def testGetNonExistentListByName(self):
        self.trello.get = MagicMock(return_value=[])
        self.assertEqual(self.board.getListByName('test'), None)

    def testGetListByName(self):
        self._mockGetResponse()
        next_actions = self.board.getListByName('Next Actions')
        self.assertEqual(next_actions.name, 'Next Actions')
