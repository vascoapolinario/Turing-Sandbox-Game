import json

class Level:
    def __init__(self, name, type, description, alphabet, objective, solution=None, correct_examples=None, wrong_examples=None):
        self.name = name
        self.type = type
        self.description = description
        self.alphabet = alphabet
        self.objective = objective
        self.solution = solution or {}
        self.correct_examples = correct_examples or []
        self.wrong_examples = wrong_examples or []

    def to_dict(self):
        return {
            "name": self.name,
            "level_type": self.type,
            "description": self.description,
            "alphabet": self.alphabet,
            "objective": self.objective,
            "solution": self.solution,
            "correct_examples": self.correct_examples,
            "wrong_examples": self.wrong_examples
        }

    @staticmethod
    def from_dict(data):
        return Level(
            name=data["name"],
            type=data["level_type"],
            description=data["description"],
            alphabet=data["alphabet"],
            objective=data["objective"],
            solution=data.get("solution"),
            correct_examples=data.get("correct_examples"),
            wrong_examples=data.get("wrong_examples")
        )

    def save_to_file(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load_from_file(path):
        with open(path, "r") as f:
            data = json.load(f)
        return Level.from_dict(data)
