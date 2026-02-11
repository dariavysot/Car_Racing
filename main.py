from game_config import GameConfig
from logic import Game

if __name__ == "__main__":
    GameConfig.parse()
    Game().run()