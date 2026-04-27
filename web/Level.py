import json

class Level:
    def __init__(self, name, type, description, detailedDescription, alphabet, objective, mode, solution=None, transform_tests=None, correct_examples=None, wrong_examples=None, double_tape=False):
        self.name = name
        self.type = type
        self.description = description
        self.detailedDescription = detailedDescription
        self.alphabet = alphabet
        self.objective = objective
        self.mode = mode
        self.solution = solution or {}
        self.transform_tests = transform_tests or []
        self.correct_examples = correct_examples or []
        self.wrong_examples = wrong_examples or []
        self.double_tape = double_tape

    def to_dict(self):
        return {
            "name": self.name,
            "level_type": self.type,
            "description": self.description,
            "detailedDescription": self.detailedDescription,
            "alphabet": self.alphabet,
            "objective": self.objective,
            "mode": self.mode,
            "solution": self.solution,
            "transform_tests": self.transform_tests,
            "correct_examples": self.correct_examples,
            "wrong_examples": self.wrong_examples,
            "double_tape": self.double_tape
        }

    @staticmethod
    def from_dict(data):
        return Level(
            name=data["name"],
            type=data["level_type"],
            description=data["description"],
            detailedDescription=data["detailedDescription"],
            alphabet=data["alphabet"],
            objective=data["objective"],
            mode=data["mode"],
            solution=data.get("solution"),
            transform_tests=data["transform_tests"],
            correct_examples=data.get("correct_examples"),
            wrong_examples=data.get("wrong_examples"),
            double_tape=data.get("double_tape", False)
        )

    def save_to_file(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load_from_file(path):
        with open(path, "r") as f:
            data = json.load(f)
        return Level.from_dict(data)
