from nextactions.board import Board
from nextactions.card import Card
import requests


class Trello:

    def __init__(self, config):
        self._config = config

    def get(self, url, data):
        return self._makeRequest('get', url, data)

    def post(self, url, data):
        return self._makeRequest('post', url, data)

    def put(self, url, data):
        return self._makeRequest('put', url, data)

    def _makeRequest(self, request_type, url, data):
        method = getattr(requests, request_type)
        response = method(url, self._addAuthToData(data))
        return self._getResponseJSONOrRaiseError(response)

    def _addAuthToData(self, data):
        auth = self._getAuth()
        return {**data, **auth}

    def _getAuth(self):
        return {
            'key': self._config.get('application_key'),
            'token': self._config.get('auth_token')
        }

    def _getResponseJSONOrRaiseError(self, response):
        if response.status_code != 200:
            raise APIError(
                "Request failed with status code " + str(response.status_code)
            )
        else:
            return response.json()

    def getBoardById(self, board_id):
        json = self.get('https://api.trello.com/1/boards/' + board_id, {})
        return Board(self, json)

    def getOwnedCards(self):
        json = self.get('https://api.trello.com/1/members/me/cards', {})
        return [Card(self, j) for j in json]

    # Putting this in Trello rather than Card as we want to be able to archive
    # lots of cards just by their ID, without loading them all first
    def archiveCard(self, card_id):
        self.put(
            'https://api.trello.com/1/cards/' + card_id + '/closed',
            {'value': "true"}
        )


class APIError(RuntimeError):
    pass
