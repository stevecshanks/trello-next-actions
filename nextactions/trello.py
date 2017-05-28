from nextactions.board import Board
from nextactions.card import Card
import requests


class Trello:

    def __init__(self, config):
        self._config = config

    def get(self, url, data):
        response = self._makeGetRequest(url, self._addAuthToData(data))
        return self._getResponseJSONOrRaiseError(response)

    def _addAuthToData(self, data):
        auth = self._getAuth()
        return {**data, **auth}

    def _getAuth(self):
        return {
            'key': self._config.get('application_key'),
            'token': self._config.get('auth_token')
        }

    def _makeGetRequest(self, url, data):
        return requests.get(url, data)

    def _getResponseJSONOrRaiseError(self, response):
        if response.status_code != 200:
            raise APIError(
                "Request failed with status code " + str(response.status_code)
            )
        else:
            return response.json()

    def post(self, url, data):
        response = self._makePostRequest(url, self._addAuthToData(data))
        return self._getResponseJSONOrRaiseError(response)

    def _makePostRequest(url, data):
        return requests.post(url, data)

    def getBoardById(self, board_id):
        json = self.get('https://api.trello.com/1/boards/' + board_id)
        return Board(self, json)

    def getOwnedCards(self):
        json = self.get('https://api.trello.com/1/members/me/cards/')
        return [Card(j) for j in json]


class APIError(RuntimeError):
    pass
