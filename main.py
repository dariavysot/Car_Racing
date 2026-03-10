from game_config import GameConfig
from config import Settings as C
from logic import Game
from gameplay.two_players import TwoPlayersGame


if __name__ == "__main__":
    GameConfig.parse()

    if C.NUM_PLAYERS == 1:
        Game().run()
    else:
        TwoPlayersGame().run()