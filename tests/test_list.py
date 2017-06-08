import unittest
from nextactions.list import List
from nextactions.trello import Trello
from unittest.mock import MagicMock, patch
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
            {'name': "Name", 'desc': "Description", 'idList': "123"}
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
        card_json = {
            'id': "123",
            'name': "Card",
            'idBoard': "456",
            'desc': "Test",
            'url': "fake"
        }
        self.trello.get = MagicMock(return_value=[card_json])
        cards = self.list.getCards()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, "123")

    def testGetTopCardForEmptyListIsNone(self):
        self.list.getCards = MagicMock(return_value=[])
        self.assertIsNone(self.list.getTopCard())

    @patch('nextactions.card.Card')
    @patch('nextactions.card.Card')
    def testGetTopCard(self, card1, card2):
        self.list.getCards = MagicMock(return_value=[card1, card2])
        self.assertEqual(self.list.getTopCard(), card1)
