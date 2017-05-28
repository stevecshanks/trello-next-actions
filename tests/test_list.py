import unittest
from nextactions.list import List
from nextactions.trello import Trello
from unittest.mock import MagicMock


class TestList(unittest.TestCase):

    def testCreateCard(self):
        trello = Trello(None)
        mock = MagicMock(return_value={'id': "456"})
        trello.post = mock
        json = {'id': "123", 'name': "Test"}
        list_ = List(trello, json)
        card_id = list_.createCard("Name", "Description")
        self.assertEqual(card_id, "456")
        mock.assert_called_once_with(
            'https://api.trello.com/1/cards',
            {'name': "Name", 'description': "Description", 'idList': "123"}
        )
