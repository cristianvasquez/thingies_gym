from enum import Enum, unique

MAX_APPLES_PER_USER = 100
MAX_APPLES_PER_SPOT = MAX_APPLES_PER_USER
MAX_TURNS = 150


@unique
class Action(Enum):
    MOVE_LEFT = 0
    MOVE_RIGHT = 1
    COLLECT_APPLES = 2
    DO_NOTHING = 3
    MOVE_UP = 4
    MOVE_DOWN = 5


@unique
class Location_type(Enum):
    EMPTY_WILDERNESS = 0
    TREE = 1
    UNCLAIMED_HOUSE = 2
    OWNED_HOUSE = 3
    FRACTIONAL_OWNERSHIP_HOUSE = 4


def DEFAULT_REWARD_FUNCTION(player, grid, variant_state_info):
    (_x, _y), apples, actions_left, active = player

    happiness_multiplier = 1  # Happiness starts at 1

    # If it's winter and the player is not in a house, the player is less happy
    for season, _ in variant_state_info:
        if season == 1:  # Winter
            [current_location_type, _] = grid[_x, _y]
            if int(current_location_type) in [Location_type.EMPTY_WILDERNESS.value, Location_type.TREE.value]:
                happiness_multiplier = -1

    return 1. * happiness_multiplier if active else -1000.  # Reward the player if still alive, and punish him when he dies (again)


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
    'move_cost': 1,
    'summer': {
        'in_the_wild_cost': 2,
        'in_a_house_cost': 0,
        'apples_growth': (3, 10)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'winter': {
        'in_the_wild_cost': 10,
        'in_a_house_cost': 0,
        'apples_growth': (1, 4)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'reward_function': DEFAULT_REWARD_FUNCTION
}

MINI_SETUP_TWO_PLAYERS = {
    'grid_size_x': 5,
    'grid_size_y': 5,
    'number_of_players': 2,
    'number_of_houses': 3,
    'number_of_trees': 3,
    'initial_player_apples': 20,
    'apple_gathering_capacity': 5,
    'initial_apples_per_tree': 10,
    'actions_per_turn': 1,
    'turns_between_seasons': 3,
    'move_cost': 1,
    'summer': {
        'in_the_wild_cost': 1,
        'in_a_house_cost': 1,
        'apples_growth': (3, 10)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'winter': {
        'in_the_wild_cost': 10,
        'in_a_house_cost': 1,
        'apples_growth': (1, 4)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'reward_function': DEFAULT_REWARD_FUNCTION
}

'''
Mini setup with very simmilar values for summer and winter
'''
MINI_SETUP_SINGLE_PLAYER = {
    'grid_size_x': 4,
    'grid_size_y': 4,
    'number_of_players': 1,
    'number_of_houses': 3,
    'number_of_trees': 3,
    'initial_player_apples': 20,
    'apple_gathering_capacity': 5,
    'initial_apples_per_tree': 10,
    'actions_per_turn': 1,
    'turns_between_seasons': 2,
    'move_cost': 1,
    'death_zone': False,
    'summer': {
        'in_the_wild_cost': 1,
        'in_a_house_cost': 1,
        'apples_growth': (3, 10)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'winter': {
        'in_the_wild_cost': 1,
        'in_a_house_cost': 1,
        'apples_growth': (3, 10)  # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'reward_function': DEFAULT_REWARD_FUNCTION
}
