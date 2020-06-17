from rules import Winter_is_coming
from setup import MINI_SETUP

setup = MINI_SETUP


game = Winter_is_coming(setup=setup)

for i in range(100):
    print(game.random_state())