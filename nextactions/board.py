from nextactions.list import List


class Board:

    def __init__(self, trello, json):
        self._trello = trello
        self.id = json['id']
        self.name = json['name']
        self.nextActionList = []

    def getLists(self):
        json = self._trello.get(
            'https://api.trello.com/1/boards/' + self.id + '/lists?cards=none'
        )
        return [List(j) for j in json]

    def getListByName(self, name):
        matches = [l for l in self.getLists() if l.name == name]
        return matches[0] if len(matches) else None
