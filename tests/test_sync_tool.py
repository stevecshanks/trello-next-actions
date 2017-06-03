import unittest
from nextactions.synctool import SyncTool
from nextactions.trello import Trello
from nextactions.board import Board
from nextactions.list import List
from nextactions.config import Config
from unittest.mock import MagicMock, call
from nextactions.card import Card


class TestSyncTool(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.config.set('gtd_board_id', "123")
        self.trello = Trello(self.config)
        self.board = Board(self.trello, {'id': "123", 'name': "GTD"})
        self.list = List(self.trello, {'id': "456", 'name': "Next Actions"})
        self.trello.getBoardById = MagicMock(return_value=self.board)
        self.board.getListByName = MagicMock(return_value=self.list)
        self.sync_tool = SyncTool(self.config, self.trello)

    def testGetNextActionCards(self):
        self.list.getCards = MagicMock(return_value=[])
        self.assertEqual(self.sync_tool.getNextActionCards(), [])
        self.trello.getBoardById.assert_called_once_with("123")
        self.board.getListByName.assert_called_once_with("Next Actions")
        self.list.getCards.assert_called_once()

    def testGetNextActionCardsReturnsOnlyAutoGeneratedCards(self):
        normal = Card(None, self._getCardJson())
        auto_json = self._getCardJson({'desc': Card.AUTO_GENERATED_TEXT})
        auto = Card(None, auto_json)
        self.list.getCards = MagicMock(return_value=[auto, normal])
        results = self.sync_tool.getNextActionCards()
        self.assertEqual(results, [auto])

    def _getCardJson(self, override={}):
        defaults = {
            'id': "123",
            'name': "Card",
            'idBoard': "456",
            'desc': "Test",
            'url': "fake"
        }
        return {**defaults, **override}

    def testReset(self):
        card = Card(None, self._getCardJson())
        self.sync_tool.getNextActionCards = MagicMock(return_value=[card])
        mock = MagicMock()
        self.trello.archiveCard = mock
        self.sync_tool.reset()
        mock.assert_called_once_with("123")

    def testGetProjectBoards(self):
        project_list = List(self.trello, {'id': "789", 'name': "Projects"})
        self.board.getListByName = MagicMock(return_value=project_list)
        card = Card(self.trello, self._getCardJson())
        project_board = Board(None, {'id': "678", 'name': "Dummy"})
        card.getProjectBoard = MagicMock(return_value=project_board)
        project_list.getCards = MagicMock(return_value=[card])
        project_boards = self.sync_tool.getProjectBoards()
        self.assertEqual(len(project_boards), 1)
        self.assertEqual(project_boards[0].id, "678")

    def testGetTopTodoCardsForNonExistentList(self):
        self.board.getListByName = MagicMock(return_value=None)
        self.sync_tool.getProjectBoards = MagicMock(return_value=[self.board])
        self.assertEqual(self.sync_tool.getTopTodoCards(), [])

    def testGetTopTodoCards(self):
        boards = [self.board, self.board]
        self.sync_tool.getProjectBoards = MagicMock(return_value=boards)
        card = Card(None, self._getCardJson())
        self.list.getCards = MagicMock(return_value=[card])
        todo_cards = self.sync_tool.getTopTodoCards()
        self.assertEqual(len(todo_cards), 2)
        self.assertEqual(todo_cards[0].id, "123")
        self.assertEqual(todo_cards[1].id, "123")

    def testSyncCard(self):
        card = Card(None, self._getCardJson())
        self.list.createCard = MagicMock()
        self.sync_tool.syncCard(card)
        self.list.createCard.assert_called_once_with(
            "GTD - Card",
            "fake\n\n" + Card.AUTO_GENERATED_TEXT
        )

    def testSyncArchivesOldNextActions(self):
        card = Card(None, self._getCardJson())
        self.sync_tool.getNextActionCards = MagicMock(return_value=[card])
        self.trello.getOwnedCards = MagicMock(return_value=[])
        self.sync_tool.getTopTodoCards = MagicMock(return_value=[])
        self.trello.archiveCard = MagicMock()

        created, archived = self.sync_tool.sync()
        self.trello.archiveCard.assert_called_once_with("123")
        self.assertEqual(created, [])
        self.assertEqual(archived, [card])

    def testSyncIgnoresExistingNextActions(self):
        url = "https://trello.com/c/12345678"
        card = Card(None, self._getCardJson({'id': "456", 'url': url}))
        next_action_card = Card(None, self._getCardJson({'desc': url}))
        self.sync_tool.getNextActionCards = MagicMock(
            return_value=[next_action_card]
        )
        self.trello.getOwnedCards = MagicMock(return_value=[])
        self.sync_tool.getTopTodoCards = MagicMock(return_value=[card])
        self.trello.archiveCard = MagicMock()
        self.sync_tool.syncCard = MagicMock()

        created, archived = self.sync_tool.sync()
        self.trello.archiveCard.assert_not_called()
        self.sync_tool.syncCard.assert_not_called()
        self.assertEqual(created, [])
        self.assertEqual(archived, [])

    def testSyncCreatesNextActionCards(self):
        card1 = Card(None, self._getCardJson())
        card2= Card(None, self._getCardJson({'id': "456"}))
        self.sync_tool.getNextActionCards = MagicMock(return_value=[])
        self.trello.getOwnedCards = MagicMock(return_value=[card1])
        self.sync_tool.getTopTodoCards = MagicMock(return_value=[card2])
        self.trello.archiveCard = MagicMock()
        self.sync_tool.syncCard = MagicMock()

        created, archived = self.sync_tool.sync()
        self.trello.archiveCard.assert_not_called()
        self.sync_tool.syncCard.assert_has_calls([call(card1), call(card2)])
        self.assertEqual(created, [card1, card2])
        self.assertEqual(archived, [])
