class List:

    def __init__(self, trello, json):
        self._trello = trello
        self.id = json['id']
        self.name = json['name']

    def createCard(self, name, description):
        data = {
            'name': name,
            'description': description,
            'idList': self.id
        }
        json = self._trello.post('https://api.trello.com/1/cards', data)
        return json['id']
