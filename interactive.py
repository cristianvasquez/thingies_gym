from dm_env import StepType

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
print(game.render())


# State, Reward, Is_terminal, Any

class Controller():
    def __init__(self):
        self.step_type = StepType.FIRST

    def on_press(self, key):
        if (key in key_map):
            timestep = game.step(key_map[key])
            self.step_type = timestep.step_type
            print(f'Reward: {timestep.reward}, step_type:{timestep.step_type}')

    def on_release(self, key):
        if self.step_type == StepType.LAST:
            print(game.render())
            return False
        if key == Key.esc:
            return False
        if (key in key_map):
            print(game.render())


controller = Controller()

with Listener(
        on_press=controller.on_press,
        on_release=controller.on_release) as listener:
    listener.join()
