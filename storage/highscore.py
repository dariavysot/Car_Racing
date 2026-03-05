"""
Persistent data management for game records.

This module handles the `HighScore` class, responsible for saving and
loading player records to and from the local file system, ensuring
that achievements are preserved across game restarts.
"""

import os

class HighScore:
    """
    Manage persistent storage of the player's highest score.

    This class handles reading from and writing to a local text file
    to ensure the high score is preserved between game sessions.

    Parameters
    ----------
    filepath : str, optional
        The path to the file where the high score is stored
        (default is "storage/highscore.txt").

    Attributes
    ----------
    filepath : str
        Location of the persistent data file.
    value : int
        The current highest score loaded into memory.
    """
    def __init__(self, filepath="storage/highscore.txt"):
        """
        Initialize the HighScore manager.
        """
        self.filepath = filepath
        self.value = self.load()

    def load(self):
        """
        Load the high score from the storage file.

        If the file does not exist, it will be created with an
        initial value of 0.

        Returns
        -------
        int
            The high score retrieved from the file.

        Notes
        -----
        Expects the file to contain a single integer string.
        """
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                f.write("0")
            return 0

        with open(self.filepath, "r") as f:
            return int(f.read())

    def save_if_better(self, score):
        """
        Update the high score if the new score exceeds the current record.

        Parameters
        ----------
        score : int
            The score achieved in the current game session.

        Returns
        -------
        bool
            True if a new record was set and saved, False otherwise.
        """
        if score > self.value:
            self.value = score
            with open(self.filepath, "w") as f:
                f.write(str(score))
            return True
        return False