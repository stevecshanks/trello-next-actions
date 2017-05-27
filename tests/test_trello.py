import unittest
import nextactions
from nextactions.trello import Trello
from unittest.mock import MagicMock


class TestTrello(unittest.TestCase):

    def setUp(self):
        self.trello = Trello(None)

    def testGetRaisesUnauthorisedOn401(self):
        with self.assertRaises(nextactions.trello.UnauthorisedError):
            self._testGetWithStatusCode(401)

    def _testGetWithStatusCode(self, status_code):
        fake_response = FakeResponse(status_code)
        self.trello._makeGetRequest = MagicMock(return_value=fake_response)
        return self.trello._get("fake url")

    def testGetRaisesNotFoundOn404(self):
        with self.assertRaises(nextactions.trello.NotFoundError):
            self._testGetWithStatusCode(404)

    def testGetRaisesErrorOn500(self):
        with self.assertRaises(nextactions.trello.ServerError):
            self._testGetWithStatusCode(500)

    def testGetWith200(self):
        json = self._testGetWithStatusCode(200)
        self.assertEqual(json, {})

    def testGetBoard(self):
        json = {'id': "123", 'name': "Test Name"}
        self.trello._get = MagicMock(return_value=json)
        board = self.trello.getBoardById("123")
        self.assertEqual(board.id, "123")
        self.assertEqual(board.name, "Test Name")


class FakeResponse:

    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return {}
