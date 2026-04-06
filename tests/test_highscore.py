import pytest
import os
from storage.highscore import HighScore


@pytest.mark.smoke
class TestHighScoreSystem:
    """Tests for the high-score persistence and validation system."""

    @pytest.fixture
    def temp_highscore_file(self, tmp_path):
        """Creates an isolated temporary file path for disk I/O testing."""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()
        return str(storage_dir / "highscore_test.txt")

    def test_highscore_initialization(self, temp_highscore_file):
        """Verification of automatic file creation with a zero value."""
        hs = HighScore(filepath=temp_highscore_file)

        assert hs.value == 0
        assert os.path.exists(temp_highscore_file)
        with open(temp_highscore_file, "r") as f:
            assert f.read() == "0"

    def test_highscore_save_better_score(self, temp_highscore_file):
        """Verification that a higher score successfully updates the record."""
        hs = HighScore(filepath=temp_highscore_file)

        result = hs.save_if_better(100)

        assert result is True
        assert hs.value == 100
        with open(temp_highscore_file, "r") as f:
            assert f.read() == "100"

    def test_highscore_ignore_lower_score(self, temp_highscore_file):
        """Verification that lower scores are ignored to preserve the record"""
        hs = HighScore(filepath=temp_highscore_file)
        hs.save_if_better(100)  # Establish baseline

        result = hs.save_if_better(50)

        assert result is False
        assert hs.value == 100
        with open(temp_highscore_file, "r") as f:
            assert f.read() == "100"
