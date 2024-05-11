import json
import os

class Database:
    # Constructor for Database class
    def __init__(self, path="database/data.json"):
        self.path = path
        self.data = {}
        self._load()

    # Private method to load data from file
    def _load(self):
        try:
            with open(self.path, 'r') as file:
                self.data = json.load(file)

        except IOError as error:
            print(f"Error loading data from {self.path}: {error}")
            self.data = {}

    # Private method to save data to file
    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True) # "exist_ok" to not raise an error if the directory already exists

            with open(self.path, 'w') as file:
                json.dump(self.data, file, indent=4) # "indent" to make the file more readable
                
        except IOError as error:
            print(f"Error saving data to {self.path}: {error}")

    # Public method to get the high score from the database
    def getHighScore(self):
        return self.data.get("high_score", 0) # If high_score doesn't exist, default to 0

    # Public method to set the high score in the database
    def setHighScore(self, score):
        self.data["high_score"] = score
        self._save()