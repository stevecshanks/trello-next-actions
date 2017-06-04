import unittest
import nextactions
import requests
from nextactions.config import Config
from nextactions.trello import Trello
from unittest.mock import MagicMock, patch


class TestTrello(unittest.TestCase):

    def setUp(self):
        config = Config()
        config.set('application_key', "456")
        config.set('auth_token', "789")
        self.trello = Trello(config)

    def testGetRequestOk(self):
        self._testRequestOk('get')

    def testGetRequestErrors(self):
        self._testBadResponseRaisesError('get')

    def testPostRequestOk(self):
        self._testRequestOk('post')

    def testPostRequestErrors(self):
        self._testBadResponseRaisesError('post')

    def testPutRequestOk(self):
        self._testRequestOk('put')

    def testPutRequestErrors(self):
        self._testBadResponseRaisesError('put')

    def _testRequestOk(self, request_type):
        json = self._makeRequestWithStatusCode(request_type, 200)
        self.assertEqual(json, {})

    def _testBadResponseRaisesError(self, request_type):
        for code in [400, 401, 404, 500]:
            with self.subTest(code=code):
                with self.assertRaises(nextactions.trello.APIError):
                    self._makeRequestWithStatusCode(request_type, code)

    def _makeRequestWithStatusCode(self, request_type, status_code):
        mock = self._getRequestsMock(request_type, status_code)
        method = self._getTrelloMethodForRequest(request_type)
        with patch(self._getRequestsMethodName(request_type), mock):
            return method("fake url", {})

    def _getRequestsMock(self, request_type, status_code):
        fake_response = FakeResponse(status_code)
        mock = MagicMock(return_value=fake_response)
        return mock

    def _getTrelloMethodForRequest(self, request_type):
        return getattr(self.trello, request_type)

    def _getRequestsMethodName(self, request_type):
        return 'requests.' + request_type

    def testGetRequestMadeWithDataAndAuth(self):
        self._testRequestMadeWithDataAndAuth('get')

    def testPostRequestMadeWithDataAndAuth(self):
        self._testRequestMadeWithDataAndAuth('post')

    def testPutRequestMadeWithDataAndAuth(self):
        self._testRequestMadeWithDataAndAuth('put')

    def _testRequestMadeWithDataAndAuth(self, request_type):
        data = {'test': "123"}
        mock = self._getRequestsMock(request_type, 200)
        method = self._getTrelloMethodForRequest(request_type)
        with patch(self._getRequestsMethodName(request_type), mock):
            method("fake url", data)
        expected = {'test': "123", 'key': "456", 'token': "789"}
        mock.assert_called_once_with("fake url", expected)

    def testGetBoard(self):
        mock = self._mockGetResponse({'id': "123", 'name': "Test Name"})
        board = self.trello.getBoardById("123")
        mock.assert_called_once_with(
            'https://api.trello.com/1/boards/123',
            {}
        )
        self.assertEqual(board.id, "123")
        self.assertEqual(board.name, "Test Name")

    def _mockGetResponse(self, json):
        mock = MagicMock(return_value=json)
        self.trello.get = mock
        return mock

    def testGetZeroOwnedCards(self):
        mock = self._mockGetResponse([])
        owned_cards = self.trello.getOwnedCards()
        self.assertEqual(owned_cards, [])
        mock.assert_called_once_with(
            'https://api.trello.com/1/members/me/cards',
            {}
        )

    def testGetOneOwnedCard(self):
        self._mockGetResponse([{
            'id': "123",
            'name': "Test Name",
            'idBoard': "456",
            'desc': "Test",
            'url': "fake"
        }])
        owned_cards = self.trello.getOwnedCards()
        self.assertEqual(len(owned_cards), 1)
        self.assertEqual(owned_cards[0].id, "123")
        self.assertEqual(owned_cards[0].name, "Test Name")


class FakeResponse:

    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return {}
