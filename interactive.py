from rules import Winter_is_coming, Action
from pynput.keyboard import Key, Listener, KeyCode

from setup import MINI_SETUP

game = Winter_is_coming(setup=MINI_SETUP)

key_map = {
    KeyCode(char='w'): Action.MOVE_UP,
    KeyCode(char='s'): Action.MOVE_DOWN,
    KeyCode(char='a'): Action.MOVE_LEFT,
    KeyCode(char='d'): Action.MOVE_RIGHT,
    KeyCode(char='e'): Action.COLLECT_APPLES,
    Key.space: Action.DO_NOTHING

}

print("The game starts, exit with ESC", key_map)
game.render()


# State, Reward, Is_terminal, Any

class Controller():
    def __init__(self):
        self.is_terminal = False

    def on_press(self,key):
        if (key in key_map):
            _, _, self.is_terminal, _ = game.step(key_map[key])

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
