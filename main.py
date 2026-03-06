from game_config import GameConfig
from config import Settings as C
from logic import Game
from gameplay.two_players import TwoPlayersGame


if __name__ == "__main__":
    args = GameConfig.parse()

    GameConfig.apply(args)

    if C.NUM_PLAYERS == 1:
        Game().run()
    else:
        base_game = Game()

        assets = {
            "screen": base_game.screen,
            "clock": base_game.clock,
            "font_big": base_game.font_big,
            "font_small": base_game.font_small,
            "road": base_game.road_img,
            "cars": base_game.car_images,
            "trucks": base_game.truck_images,
            "explosion": base_game.explosion_img,
        }

        TwoPlayersGame(assets).run()