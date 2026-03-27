import pytest
import os
from storage.highscore import HighScore  # перевірте шлях до класу


@pytest.fixture
def temp_highscore_file(tmp_path):
    """Створює тимчасовий шлях для файлу рекорду."""
    d = tmp_path / "storage"
    d.mkdir()
    return str(d / "highscore_test.txt")


@pytest.mark.smoke
def test_highscore_initialization(temp_highscore_file):
    """Перевірка: чи створюється файл з 0, якщо його не існує."""
    hs = HighScore(filepath=temp_highscore_file)
    assert hs.value == 0
    assert os.path.exists(temp_highscore_file)
    with open(temp_highscore_file, "r") as f:
        assert f.read() == "0"


@pytest.mark.smoke
def test_highscore_save_better_score(temp_highscore_file):
    """Перевірка: чи оновлюється рекорд на більший."""
    hs = HighScore(filepath=temp_highscore_file)

    result = hs.save_if_better(100)

    assert result is True
    assert hs.value == 100
    with open(temp_highscore_file, "r") as f:
        assert f.read() == "100"


@pytest.mark.smoke
def test_highscore_ignore_lower_score(temp_highscore_file):
    """Перевірка: чи ігнорується менший рахунок."""
    hs = HighScore(filepath=temp_highscore_file)
    hs.save_if_better(100)  # встановлюємо початковий рекорд

    result = hs.save_if_better(50)

    assert result is False
    assert hs.value == 100
    with open(temp_highscore_file, "r") as f:
        assert f.read() == "100"
