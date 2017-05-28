import unittest
import nextactions
from nextactions.config import Config
from nextactions.trello import Trello
from unittest.mock import MagicMock


class TestTrello(unittest.TestCase):

    def setUp(self):
        self.trello = Trello(None)
        self.bad_status_codes = [400, 401, 404, 500]

    def _mockRequestToReturnCode(self, request_type, status_code):
        method_name = "_make" + request_type.capitalize() + "Request"
        fake_response = FakeResponse(status_code)
        mock = MagicMock(return_value=fake_response)
        setattr(self.trello, method_name, mock)

        return getattr(self.trello, request_type)

    def _testRequestOk(self, request_type):
        json = self._testRequestWithStatusCode(request_type, 200)
        self.assertEqual(json, {})

    def _testRequestWithStatusCode(self, request_type, status_code):
        method = self._mockRequestToReturnCode(request_type, status_code)
        return method("fake url", {})

    def _testBadResponseRaisesError(self, request_type):
        for code in self.bad_status_codes:
            with self.subTest(code=code):
                with self.assertRaises(nextactions.trello.APIError):
                    self._testRequestWithStatusCode(request_type, code)

    def testGetRequestOk(self):
        self._testRequestOk('get')

    def testGetequestErrors(self):
        self._testBadResponseRaisesError('get')

    def testPostRequestOk(self):
        self._testRequestOk('post')

    def testPostRequestErrors(self):
        self._testBadResponseRaisesError('post')

    @unittest.skip("Todo")
    def testRequestMadeWithDataAndAuth(self):
        pass

    def testGetBoard(self):
        self._mockGetResponse({'id': "123", 'name': "Test Name"})
        board = self.trello.getBoardById("123")
        self.assertEqual(board.id, "123")
        self.assertEqual(board.name, "Test Name")

    def _mockGetResponse(self, json):
        self.trello.get = MagicMock(return_value=json)

    def testGetZeroOwnedCards(self):
        self._mockGetResponse([])
        owned_cards = self.trello.getOwnedCards()
        self.assertEqual(owned_cards, [])

    def testGetOneOwnedCard(self):
        self._mockGetResponse([{
            'id': "123",
            'name': "Test Name",
            'idBoard': "456"
        }])
        owned_cards = self.trello.getOwnedCards()
        self.assertEqual(len(owned_cards), 1)
        self.assertEqual(owned_cards[0].id, "123")
        self.assertEqual(owned_cards[0].name, "Test Name")

    def testGetAuth(self):
        config = Config()
        config.set('application_key', "dummy key")
        config.set('auth_token', "dummy token")
        trello = Trello(config)
        auth = trello._getAuth()
        self.assertEqual(auth['key'], "dummy key")
        self.assertEqual(auth['token'], "dummy token")


class FakeResponse:

    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return {}
