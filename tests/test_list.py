import unittest
from nextactions.list import List
from nextactions.trello import Trello
from unittest.mock import MagicMock
from nextactions.card import Card


class TestList(unittest.TestCase):

    def setUp(self):
        self.trello = Trello(None)
        self.list = List(self.trello, {'id': "123", 'name': "Test"})

    def testCreateCard(self):
        mock = MagicMock(return_value={'id': "456"})
        self.trello.post = mock
        card_id = self.list.createCard("Name", "Description")
        self.assertEqual(card_id, "456")
        mock.assert_called_once_with(
            'https://api.trello.com/1/cards',
            {'name': "Name", 'description': "Description", 'idList': "123"}
        )

    def testGetCardsForEmptyList(self):
        mock = MagicMock(return_value=[])
        self.trello.get = mock
        cards = self.list.getCards()
        self.assertEqual(cards, [])
        mock.assert_called_once_with(
            'https://api.trello.com/1/lists/123/cards',
            {}
        )

    def testGetCards(self):
        mock = MagicMock(return_value=[self._getCardJson()])
        self.trello.get = mock
        cards = self.list.getCards()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, "123")
        self.assertEqual(cards[0].name, "Card")

    def _getCardJson(self, override={}):
        defaults = {
            'id': "123",
            'name': "Card",
            'idBoard': "456",
            'desc': "Test",
            'url': "fake"
        }
        return {**defaults, **override}

    def testGetTopCardForEmptyListIsNone(self):
        self.list.getCards = MagicMock(return_value=[])
        self.assertIsNone(self.list.getTopCard())

    def testGetTopCard(self):
        card1 = Card(None, self._getCardJson())
        card2 = Card(None, self._getCardJson({'id': "234"}))
        self.list.getCards = MagicMock(return_value=[card1, card2])
        top_card = self.list.getTopCard()
        self.assertEqual(top_card.id, card1.id)
