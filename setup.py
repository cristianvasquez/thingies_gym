def DEFAULT_REWARD_FUNCTION(player):
    (_x, _y), apples, actions_left, active = player
    return 1 if active else -1000  # Reward the player if still alive, and punish him when he dies (again)


DEFAULT_SETUP = {
    'grid_size_x': 10,
    'grid_size_y': 10,
    'number_of_players': 6,
    'number_of_houses': 10,
    'number_of_trees': 5,
    'initial_player_apples': 1000,
    'initial_apples_per_tree': 10,
    'apple_gathering_capacity': 5,
    'actions_per_turn': 5,
    'turns_between_seasons': 5,
    'summer': {
        'move_cost': 1,
        'in_the_wild_cost': 2,
        'in_a_house_cost': 0,
        'apples_growth': (3, 10)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'winter': {
        'move_cost': 2,
        'in_the_wild_cost': 10,
        'in_a_house_cost': 0,
        'apples_growth': (1, 4)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'reward_function': DEFAULT_REWARD_FUNCTION
}

MINI_SETUP = {
    'grid_size_x': 5,
    'grid_size_y': 5,
    'number_of_players': 2,
    'number_of_houses': 3,
    'number_of_trees': 3,
    'initial_player_apples': 20,
    'apple_gathering_capacity': 5,
    'initial_apples_per_tree': 10,
    'actions_per_turn': 5,
    'turns_between_seasons': 2,
    'summer': {
        'move_cost': 1,
        'in_the_wild_cost': 1,
        'in_a_house_cost': 1,
        'apples_growth': (3, 10)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'winter': {
        'move_cost': 2,
        'in_the_wild_cost': 10,
        'in_a_house_cost': 1,
        'apples_growth': (1, 4)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'reward_function': DEFAULT_REWARD_FUNCTION
}
