import os

class HighScore:
    def __init__(self, filepath="storage/highscore.txt"):
        self.filepath = filepath
        self.value = self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                f.write("0")
            return 0

        with open(self.filepath, "r") as f:
            return int(f.read())

    def save_if_better(self, score):
        if score > self.value:
            self.value = score
            with open(self.filepath, "w") as f:
                f.write(str(score))
            return True
        return False