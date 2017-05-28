import unittest
from nextactions.list import List
from nextactions.trello import Trello
from unittest.mock import MagicMock


class TestList(unittest.TestCase):

    def testCreateCard(self):
        trello = Trello(None)
        trello.post = MagicMock(return_value={'id': "456"})
        json = {'id': "123", 'name': "Test"}
        list_ = List(trello, json)
        card_id = list_.createCard("Name", "Description")
        self.assertEqual(card_id, "456")
