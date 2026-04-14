from config import Settings as C
from game_config import GameConfig
from gameplay.two_players import TwoPlayersGame
from logic import Game

if __name__ == "__main__":
    args = GameConfig.parse()

    GameConfig.apply(args)

    if C.NUM_PLAYERS == 1:
        Game().run()
    else:
        TwoPlayersGame().run()
