import random
from unittest import TestCase

from board import Board
from monopoly_rules import MonopolicRules
from monopoly_rules import ROLL_DICE,BUY_PROPERTY,BUILD,END_TURN


def test_never_buy_build_at_the_same_time(possible_actions_history):
    for actions in possible_actions_history:
        assert not (BUY_PROPERTY in  actions and BUILD in actions), "Should not happen"


def test_never_roll_end_turn_at_the_same_time(possible_actions_history):
    for actions in possible_actions_history:
        assert not (ROLL_DICE in  actions and END_TURN in actions), "Should not happen"

def test_all_actions_are_proposed(possible_actions_history):
    all_triggered = set()
    for actions in possible_actions_history:
        all_triggered = all_triggered.union(actions)

    assert ROLL_DICE in all_triggered, "Should be in"
    assert BUY_PROPERTY in all_triggered, "Should be in"
    assert BUILD in all_triggered, "Should be in"
    assert END_TURN in all_triggered, "Should be in"

if __name__ == "__main__":

    board = Board(number_of_players=6, board_file='board.csv')
    game = MonopolicRules(board=board)

    terminal_state = False
    possible_actions_history = []
    for i in range(1, 500000):
        if terminal_state:
            break
        possible_actions = game.possible_actions()
        possible_actions_history.append(possible_actions)
        action = random.choice(possible_actions)
        state, reward, terminal_state, messages = game.step(action)
    print('number of turns: {}'.format(i))

    test_never_buy_build_at_the_same_time(possible_actions_history)
    test_never_roll_end_turn_at_the_same_time(possible_actions_history)
    test_all_actions_are_proposed(possible_actions_history)
    print("Everything passed")



