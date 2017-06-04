import json


class Config:

    def __init__(self):
        self._values = {}

    def get(self, key):
        if key in self._values:
            return self._values[key]
        else:
            return None

    def set(self, key, value):
        self._values[key] = value

    def loadFromFile(self, file_name):
        try:
            self._setValuesFromFile(file_name)
        except json.decoder.JSONDecodeError:
            raise ParseError("'" + file_name + "' is not valid JSON")

    def _setValuesFromFile(self, file_name):
        with open(file_name, 'r') as f:
            self._values = json.load(f)


class ParseError(ValueError):

    def __init__(self, msg):
        self.msg = msg
