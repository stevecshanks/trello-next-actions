import json
import os


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
        if self._doesFileExist(file_name):
            try:
                self._values = self._getValuesFromFile(file_name)
            except json.decoder.JSONDecodeError:
                raise ParseError("'" + file_name + "' is not valid JSON")
        else:
            raise FileNotFoundError("File " + file_name + " not found")

    def _getValuesFromFile(self, file_name):
        json_data = {}
        with open(file_name, 'r') as f:
            json_data = json.load(f)
        return json_data

    def _doesFileExist(self, file_name):
        return os.path.exists(file_name)


class ParseError(ValueError):

    def __init__(self, msg):
        self.msg = msg
