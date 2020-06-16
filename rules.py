from typing import Any, Tuple

from gym.utils import seeding
from enum import Enum, unique

from render import Winter_is_coming_renderer
from setup import DEFAULT_SETUP


@unique
class Action(Enum):
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    COLLECT_APPLES = 4
    DO_NOTHING = 5


@unique
class Seasons(Enum):
    SUMMER = 0
    WINTER = 1


@unique
class House_type(Enum):
    WILD = 0
    OWNED = 1
    FRACTIONAL = 2


class types():
    State = Any
    Reward = float
    Is_terminal = bool
    Response = Tuple[State, Reward, Is_terminal, Any]


class Winter_is_coming():
    '''
    ## Base rules

        * Thingies can move in the grid in four directions.
        * Thingies spend apples to move around.
        * From time to time, trees with apples appear in the grid
        * Thingies can collect apples from the trees
        * A thingy that doesn't have any apple left dies
        * Thingies can perform a fixed number of actions each turn.
        * The order in which thingies play is randomly chosen.
        * No more than one house or tree is allowed in the same spot.
    '''

    def __init__(self, setup=None, seed=None):
        if setup is None:
            setup = DEFAULT_SETUP
        self.np_random, seed = seeding.np_random(seed)

        self.reward_function = setup['reward_function']
        self.grid_size_x = setup['grid_size_x']
        self.grid_size_y = setup['grid_size_y']
        self.actions_per_turn = setup['actions_per_turn']
        self.turns_between_seasons = setup['turns_between_seasons']
        self.apple_gathering_capacity = setup['apple_gathering_capacity']
        self.summer_spec = tuple(setup['summer'].values())
        self.winter_spec = tuple(setup['winter'].values())
        self.current_season = Seasons.SUMMER

        spots = [(x, y) for x in list(range(self.grid_size_x)) for y in list(range(self.grid_size_y))]

        # Allocate players
        player_positions = self.np_random.choice(len(spots), setup['number_of_players'], replace=False)
        # coordinates, apples, actions_left, active
        self.players = [(spots[i], setup['initial_player_apples'], self.actions_per_turn, True) for i in
                        player_positions]

        number_of_houses_and_trees = setup['number_of_houses'] + setup['number_of_trees']
        assert number_of_houses_and_trees < self.grid_size_x * self.grid_size_y, "Not enough space for so many houses  and trees"

        # Allocate houses and trees
        houses_and_trees_positions = self.np_random.choice(len(spots), number_of_houses_and_trees, replace=False)

        # houses: (coordinates, type, buy_price, rent_price)
        self.houses = [(spots[i], House_type.WILD) for i in houses_and_trees_positions[:setup['number_of_houses']]]
        # trees: (coordinates, number_of_initial_apples)
        self.trees = [(spots[i], setup['initial_apples_per_tree']) for i in
                      houses_and_trees_positions[setup['number_of_houses']:]]

        #
        # self.houses = [
        #     (spots[i], None, self.np_random.randint(House_spec.BUY_PRICE_LB.value, House_spec.BUY_PRICE_UB.value + 1),
        #      self.np_random.randint(House_spec.RENT_PRICE_LB.value, House_spec.RENT_PRICE_UB.value + 1)) for i in
        #     houses_positions]

        self.renderer = Winter_is_coming_renderer(len(self.players))
        self.current_turn = 0
        self.is_terminal = False
        self.playing_queue = self._draw_playing_queue()

    def _draw_playing_queue(self):
        available = []
        for i, (_, _, actions_left, active) in enumerate(self.players):
            if active and actions_left > 0:
                available.append(i)
        return self.np_random.choice(available, len(available), replace=False) if len(available) > 0 else None

    def action_space(self):
        return list(map(lambda x: x.value, list(Action)))

    def state(self) -> types.State:
        return self.players, self.houses, self.trees, self.current_season

    def render(self):
        print(self.renderer.render(self.grid_size_x, self.grid_size_y, current_turn=self.current_turn,
                                   playing_queue=self.playing_queue, state=self.state(), is_terminal=self.is_terminal))

    def season_specs(self):
        return self.summer_spec if self.current_season == Seasons.SUMMER else self.winter_spec

    def next_season(self):
        return Seasons.WINTER if self.current_season == Seasons.SUMMER else Seasons.SUMMER

    def step(self, action: Action) -> types.Response:

        if self.is_terminal:
            raise RuntimeError("Terminal state reached")

        current_player_id = self.playing_queue[0]
        (x, y), apples, actions_left, active = self.players[current_player_id]
        move_cost, in_the_wild_cost, in_a_house_cost, _ = self.season_specs()

        if action == Action.MOVE_LEFT and x > 0:
            x = x - 1 if x > 0 else x
            apples -= move_cost
        elif action == Action.MOVE_RIGHT:
            x = x + 1 if x < self.grid_size_x - 1 else x
            apples -= move_cost
        elif action == Action.MOVE_UP:
            y = y - 1 if y > 0 else y
            apples -= move_cost
        elif action == Action.MOVE_DOWN:
            y = y + 1 if y < self.grid_size_y - 1 else y
            apples -= move_cost
        elif action == Action.COLLECT_APPLES:
            for i, ((_x, _y), _apples) in enumerate(self.trees):
                if x == _x and y == _y and _apples > 0:
                    # Player can only collect available apples in the tree
                    gathered_apples = min(self.apple_gathering_capacity, _apples)
                    apples += gathered_apples
                    self.trees[i] = ((_x, _y), _apples - gathered_apples)
                    break
        elif action == Action.DO_NOTHING:
            pass

        actions_left = actions_left - 1

        # The player's turn ended
        if actions_left == 0:

            # remove it from the playing queue
            self.playing_queue = self.playing_queue[1:]

            # apply seasonal costs
            player_in_a_house = False
            for (_x, _y), _ in self.houses:
                if x == _x and y == _y:
                    player_in_a_house = True
                    break
            apples -= in_a_house_cost if player_in_a_house else in_the_wild_cost

            # if the player still alive, renew his available actions
            if apples >= 0:
                actions_left = self.actions_per_turn
            # Else mark him as inactive
            else:
                active = False

        # update the player
        updated_player = ((x, y), apples, actions_left, active)
        self.players[current_player_id] = updated_player

        reward = self.reward_function(updated_player)
        self.is_terminal = self.next_turn()

        return self.state(), reward, self.is_terminal, None

    def next_turn(self) -> types.Is_terminal:
        if len(self.playing_queue) == 0:
            # Draw another player queue
            self.playing_queue = self._draw_playing_queue()

            # all players died, this is a terminal state
            if self.playing_queue is None:
                return True

            self.current_turn += 1

            # Season changes
            if self.current_turn % self.turns_between_seasons:
                self.current_season = self.next_season()
                # Apply tree growth
                _, _, _, (apples_growth_lb, apples_growth_up) = self.season_specs()
                for i, ((_x, _y), _apples) in enumerate(self.trees):
                    self.trees[i] = ((_x, _y), _apples + self.np_random.randint(apples_growth_lb, apples_growth_up))

        return False
