from nextactions.board import Board


class Trello:

    def __init__(self, config):
        self._config = config

    def _get(self, url):
        response = self._makeGetRequest(url)
        return self._getResponseJSONOrRaiseError(response)

    def _makeGetRequest(self, url):
        pass

    def _getResponseJSONOrRaiseError(self, response):
        if response.status_code == 401:
            raise UnauthorisedError()
        elif response.status_code == 404:
            raise NotFoundError()
        elif response.status_code != 200:
            raise ServerError()
        else:
            return response.json()

    def getBoardById(self, id):
        json = self._get('https://api.trello.com/1/boards/' + id)
        return Board(json['id'], json['name'])


class UnauthorisedError(ValueError):
    pass


class NotFoundError(ValueError):
    pass


class ServerError(ValueError):
    pass
