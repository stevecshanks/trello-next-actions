from nextactions.board import Board
from nextactions.card import Card
import requests


class Trello:

    def __init__(self, config):
        self._config = config

    def get(self, url):
        response = self._makeGetRequest(url)
        return self._getResponseJSONOrRaiseError(response)

    def _makeGetRequest(self, url):
        return requests.get(url, self._getAuth())

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

    def getBoardById(self, id):
        json = self.get('https://api.trello.com/1/boards/' + id)
        return Board(self, json)

    def getOwnedCards(self):
        json = self.get('https://api.trello.com/1/members/me/cards/')
        return [Card(j) for j in json]


class APIError(RuntimeError):
    pass
