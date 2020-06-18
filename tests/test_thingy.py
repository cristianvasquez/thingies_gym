from distribution import dist
from rules import Winter_is_coming, Action
from setup import MINI_SETUP_TWO_PLAYERS
from variants import Summer, Winter


def test_playing_queue():
    setup = MINI_SETUP_TWO_PLAYERS
    setup['actions_per_turn'] = 1
    setup['number_of_players'] = 2
    game = Winter_is_coming(setup=setup)
    assert len(game.playing_queue) == 2, "Should start with two players in the queue"
    game.do_action(Action.DO_NOTHING)
    assert len(game.playing_queue) == 1, "Should remove a player from the queue"
    game.do_action(Action.DO_NOTHING)
    assert len(game.playing_queue) == 2, "Should renew two players in the queue"


def test_distance():
    assert dist((5, 5), (0, 10)) == (-5, 5)
    assert dist((5, 5), (10, 10)) == (5, 5)
    assert dist((5, 5), (10, 0)) == (5, -5)
    assert dist((5, 5), (0, 0)) == (-5, -5)


def test_variants():
    turns_between_seasons = 2
    summer = Summer(turns_between_seasons)
    winter = Winter(turns_between_seasons)

    assert summer.applies(0)
    assert summer.applies(1)
    assert winter.applies(2)
    assert winter.applies(3)
    assert summer.applies(4)

    for i in range(10):
        assert summer.applies(i) is not winter.applies(i)

    assert summer.turns_until_season_changes(0) == 2
    assert summer.turns_until_season_changes(1) == 1
    assert winter.turns_until_season_changes(2) == 2
    assert winter.turns_until_season_changes(3) == 1
    assert summer.turns_until_season_changes(4) == 2


assert dist((5, 5), (5, 5)) == (0, 0)

if __name__ == "__main__":
    test_variants()

    test_playing_queue()
    test_distance()
    print("Everything passed")
