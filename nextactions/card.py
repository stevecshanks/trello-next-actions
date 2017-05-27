class Card:

    def __init__(self, json):
        self.id = json['id']
        self.name = json['name']
        self.board_id = json['idBoard']
