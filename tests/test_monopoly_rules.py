import random

from monopoly.board import Board
from monopoly.rules import ClassicMonopolyRules
from monopoly.rules import ROLL_DICE, BUY_PROPERTY, BUILD, END_TURN


def test_never_buy_build_at_the_same_time(possible_actions_history):
    for actions in possible_actions_history:
        assert not (BUY_PROPERTY in actions and BUILD in actions), "Should not happen"


def test_never_roll_end_turn_at_the_same_time(possible_actions_history):
    for actions in possible_actions_history:
        assert not (ROLL_DICE in actions and END_TURN in actions), "Should not happen"


def test_all_actions_are_proposed(possible_actions_history):
    all_triggered = set()
    for actions in possible_actions_history:
        all_triggered = all_triggered.union(actions)

    assert ROLL_DICE in all_triggered, "Should be in"
    assert BUY_PROPERTY in all_triggered, "Should be in"
    assert BUILD in all_triggered, "Should be in"
    assert END_TURN in all_triggered, "Should be in"


def test_all_positions_visited():
    board = Board(number_of_players=6, board_file='monopoly/default.csv')
    game = ClassicMonopolyRules(board=board)
    terminal_state = False
    locations_visited = set()
    for i in range(1, 500000):
        if terminal_state:
            break
        possible_actions = game.possible_actions()
        action = random.choice(possible_actions)
        state, reward, terminal_state, messages = game.step(action)
        for player_position, _, _ in state[0]:
            locations_visited = locations_visited.union([player_position])
    print(locations_visited,board.number_of_locations)
    assert len(locations_visited) == board.number_of_locations # Counts None, from the bank

if __name__ == "__main__":

    board = Board(number_of_players=6, board_file='monopoly/default.csv')
    game = ClassicMonopolyRules(board=board)

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
    test_all_positions_visited()

    print("Everything passed")
