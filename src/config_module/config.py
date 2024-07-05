import json

class Config:
    def __init__(self, json_file_path=None) -> None:
        if json_file_path is None:
            raise FileNotFoundError('JSON file path is not set')

        self.data = json.load(open(json_file_path, 'r'))
            