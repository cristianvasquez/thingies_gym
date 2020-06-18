from rules import Winter_is_coming, Action
from pynput.keyboard import Key, Listener, KeyCode

from setup import MINI_SETUP_TWO_PLAYERS, MINI_SETUP_SINGLE_PLAYER

setup = MINI_SETUP_SINGLE_PLAYER
# setup['actions_per_turn'] = 1
# setup['number_of_players'] = 2

game = Winter_is_coming(setup=setup)

key_map = {
    KeyCode(char='w'): Action.MOVE_UP.value,
    KeyCode(char='s'): Action.MOVE_DOWN.value,
    KeyCode(char='a'): Action.MOVE_LEFT.value,
    KeyCode(char='d'): Action.MOVE_RIGHT.value,
    KeyCode(char='e'): Action.COLLECT_APPLES.value,
    Key.space: Action.DO_NOTHING.value
}

print("The game starts, exit with ESC", key_map)
game.render()

# State, Reward, Is_terminal, Any

class Controller():
    def __init__(self):
        self.is_terminal = False

    def on_press(self,key):
        if (key in key_map):
            _, reward, self.is_terminal, _ = game.do_action(key_map[key])
            print(f'Reward: {reward}, is_terminal:{self.is_terminal}')

    def on_release(self,key):
        if self.is_terminal:
            game.render()
            return False
        if key == Key.esc:
            return False
        if (key in key_map):
            game.render()

controller = Controller()

with Listener(
        on_press=controller.on_press,
        on_release=controller.on_release) as listener:
    listener.join()
