class Board:

    def __init__(self, json):
        self.id = json['id']
        self.name = json['name']
        self.nextActionList = []
