from gym.utils import seeding

from setup import Location_type, MAX_APPLES_PER_SPOT

class Variant():
    def __init__(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

    def state_info(self, current_turn):
        return self.__class__, None


class Season(Variant):
    def __init__(self, values=None, seed=None):
        self.values = values
        super().__init__(seed)

    def applies(self, turn) -> bool:
        return False

    # Invoked each time the player has no actions left
    # Perhaps I should take this out.
    def location_cost(self, grid, x, y):
        player_in_a_house = grid[x, y, 0] in [Location_type.UNCLAIMED_HOUSE.value,
                                              Location_type.OWNED_HOUSE.value,
                                              Location_type.FRACTIONAL_OWNERSHIP_HOUSE.value]
        return self.values['in_a_house_cost'] if player_in_a_house else self.values['in_the_wild_cost']

    # Invoked each time the turn ends
    def update_spots(self, spots):
        # Apples grow in trees
        l_bound, h_bound = self.values['apples_growth']
        is_tree = spots[:, :, 0] == Location_type.TREE.value
        spots[is_tree] += [0, self.np_random.randint(l_bound, h_bound)]
        return spots


class Summer(Season):
    def __init__(self, turns_between_seasons, values=None, seed=None):
        if values is None:
            values = {
                'in_the_wild_cost': 2,
                'in_a_house_cost': 0,
                'apples_growth': (3, 10)
                # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
            }
        self.turns_between_seasons = turns_between_seasons
        super().__init__(values=values, seed=seed)

    def turns_until_season_changes(self, turn) -> int:
        return self.turns_between_seasons - turn % (2 * self.turns_between_seasons)

    def applies(self, turn) -> bool:
        current = turn % (2 * self.turns_between_seasons)  # Two seasons only
        return True if current < self.turns_between_seasons else False

    def state_info(self, current_turn):
        return 0, self.turns_until_season_changes(current_turn)


class Winter(Season):
    def __init__(self, turns_between_seasons, values=None, seed=None):
        if values is None:
            values = {
                'in_the_wild_cost': 10,
                'in_a_house_cost': 0,
                'apples_growth': (1, 4)
                # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
            }
        self.turns_between_seasons = turns_between_seasons
        super().__init__(values=values, seed=seed)

    def turns_until_season_changes(self, turn) -> int:
        return (2 * self.turns_between_seasons) - turn % (2 * self.turns_between_seasons)

    def applies(self, turn) -> bool:
        current = turn % (2 * self.turns_between_seasons)  # Two seasons only
        return True if current >= self.turns_between_seasons else False

    def state_info(self, current_turn):
        return 1, self.turns_until_season_changes(current_turn)
