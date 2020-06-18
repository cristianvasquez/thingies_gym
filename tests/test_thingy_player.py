from rules import Winter_is_coming, Action
from setup import MINI_SETUP_TWO_PLAYERS


def test_playing_queue():
    setup = MINI_SETUP_TWO_PLAYERS
    setup['actions_per_turn'] = 1
    setup['number_of_players'] = 2
    game = Winter_is_coming(setup=MINI_SETUP_TWO_PLAYERS)
    assert len(game.playing_queue) == 2, "Should start with two players in the queue"
    game.do_action(Action.DO_NOTHING)
    assert len(game.playing_queue) == 1, "Should remove a player from the queue"
    game.do_action(Action.DO_NOTHING)
    assert len(game.playing_queue) == 2, "Should renew two players in the queue"

if __name__ == "__main__":
    test_playing_queue()
    print("Everything passed")
