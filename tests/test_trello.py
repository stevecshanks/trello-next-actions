import unittest
import nextactions
from nextactions.config import Config
from nextactions.trello import Trello
from unittest.mock import MagicMock


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
        json = self._testRequestWithStatusCode(request_type, 200)
        self.assertEqual(json, {})

    def _testBadResponseRaisesError(self, request_type):
        for code in [400, 401, 404, 500]:
            with self.subTest(code=code):
                with self.assertRaises(nextactions.trello.APIError):
                    self._testRequestWithStatusCode(request_type, code)

    def _testRequestWithStatusCode(self, request_type, status_code):
        method = self._mockRequestToReturnCode(request_type, status_code)
        return method("fake url", {})

    def _mockRequestToReturnCode(self, request_type, status_code):
        self._mockMakeRequestToReturnCode(request_type, status_code)
        return self._getMethodForRequest(request_type)

    def _mockMakeRequestToReturnCode(self, request_type, status_code):
        fake_response = FakeResponse(status_code)
        mock = MagicMock(return_value=fake_response)
        method_to_mock = self._getMakeRequestMethodName(request_type)
        setattr(self.trello, method_to_mock, mock)
        return mock

    def _getMakeRequestMethodName(self, request_type):
        return "_make" + request_type.capitalize() + "Request"

    def _getMethodForRequest(self, request_type):
        return getattr(self.trello, request_type)

    def testGetRequestMadeWithDataAndAuth(self):
        self._testRequestMadeWithDataAndAuth('get')

    def testPostRequestMadeWithDataAndAuth(self):
        self._testRequestMadeWithDataAndAuth('post')

    def testPutRequestMadeWithDataAndAuth(self):
        self._testRequestMadeWithDataAndAuth('put')

    def _testRequestMadeWithDataAndAuth(self, request_type):
        data = {'test': "123"}
        mock = self._mockMakeRequestToReturnCode(request_type, 200)
        method = self._getMethodForRequest(request_type)
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

    def testArchiveCard(self):
        mock = MagicMock()
        self.trello.put = mock
        self.trello.archiveCard("123")
        mock.assert_called_once_with(
            'https://api.trello.com/1/cards/123/closed',
            {'value': "true"}
        )


class FakeResponse:

    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return {}
