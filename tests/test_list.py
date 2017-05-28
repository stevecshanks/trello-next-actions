import unittest
from nextactions.list import List
from nextactions.trello import Trello
from unittest.mock import MagicMock


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
        json = [{
            'id': "1",
            'name': "Card",
            'idBoard': "2",
            'desc': "Desc",
            'url': "fake"
        }]
        mock = MagicMock(return_value=json)
        self.trello.get = mock
        cards = self.list.getCards()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, "1")
        self.assertEqual(cards[0].name, "Card")
