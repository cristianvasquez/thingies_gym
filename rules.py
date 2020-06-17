from typing import Any, Tuple

from gym.utils import seeding
from enum import Enum, unique

from render import Winter_is_coming_renderer
from setup import DEFAULT_SETUP

MAX_APPLES_PER_TREE = 100
MAX_APPLES_PER_PLAYER = 10000


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
        self.setup = setup

        self._grid_size_x = setup['grid_size_x']
        self._grid_size_y = setup['grid_size_y']
        self._actions_per_turn = setup['actions_per_turn']
        self._turns_between_seasons = setup['turns_between_seasons']
        self._apple_gathering_capacity = setup['apple_gathering_capacity']
        self._summer_spec = tuple(setup['summer'].values())
        self._winter_spec = tuple(setup['winter'].values())

        self.players, self.houses, self.trees, self.current_season = self._build_state(current_season=Seasons.SUMMER)

        self._renderer = Winter_is_coming_renderer(len(self.players))
        self.current_turn = 0
        self.is_terminal = False
        self.playing_queue = self._draw_new_playing_queue()

    def random_state(self):
        return self._build_state(
            tree_apples_bounds=(0, MAX_APPLES_PER_TREE),
            player_apples_bound=(0, MAX_APPLES_PER_PLAYER)
        )

    def _build_state(self, tree_apples_bounds=None, player_apples_bound=None, current_season=None):
        if player_apples_bound is None:
            player_apples_bound = (self.setup['initial_player_apples'], self.setup['initial_player_apples'] + 1)
        if tree_apples_bounds is None:
            tree_apples_bounds = (self.setup['initial_apples_per_tree'], self.setup['initial_apples_per_tree'] + 1)
        if current_season is None:
            current_season = list(Seasons)[self.np_random.randint(len(list(Seasons)))]  # random season

        spots = [(x, y) for x in list(range(self._grid_size_x)) for y in list(range(self._grid_size_y))]

        # Allocate players
        player_positions = self.np_random.choice(len(spots), self.setup['number_of_players'], replace=False)

        # coordinates, apples, actions_left, active
        players = [(spots[i],
                    self.np_random.randint(player_apples_bound[0], player_apples_bound[1]),
                    self._actions_per_turn, True)
                   for i in player_positions]

        number_of_houses_and_trees = self.setup['number_of_houses'] + self.setup['number_of_trees']
        assert number_of_houses_and_trees < self._grid_size_x * self._grid_size_y, "Not enough space for so many houses  and trees"

        # Allocate houses and trees
        houses_and_trees_positions = self.np_random.choice(len(spots), number_of_houses_and_trees, replace=False)

        # houses: (coordinates, type, buy_price, rent_price)
        houses = [(spots[i], House_type.WILD) for i in houses_and_trees_positions[:self.setup['number_of_houses']]]
        # trees: (coordinates, number_of_initial_apples)
        trees = [(spots[i],
                  self.np_random.randint(tree_apples_bounds[0], tree_apples_bounds[1]))
                 for i in houses_and_trees_positions[self.setup['number_of_houses']:]]

        list(map(lambda x: x.value, list(Action)))

        #
        # self.houses = [
        #     (spots[i], None, self.np_random.randint(House_spec.BUY_PRICE_LB.value, House_spec.BUY_PRICE_UB.value + 1),
        #      self.np_random.randint(House_spec.RENT_PRICE_LB.value, House_spec.RENT_PRICE_UB.value + 1)) for i in
        #     houses_positions]

        return players, houses, trees, current_season

    @property
    def action_space(self):
        return list(map(lambda x: x.value, list(Action)))

    def state(self) -> types.State:
        return self.players, self.houses, self.trees, self.current_season

    def render(self):
        print(self._renderer.render(self._grid_size_x, self._grid_size_y, current_turn=self.current_turn,
                                    playing_queue=self.playing_queue, state=self.state(), is_terminal=self.is_terminal))

    def _season_specs(self):
        return self._summer_spec if self.current_season == Seasons.SUMMER else self._winter_spec

    def _next_season(self):
        return Seasons.WINTER if self.current_season == Seasons.SUMMER else Seasons.SUMMER

    def step(self, action: Action) -> types.Response:

        if self.is_terminal:
            raise RuntimeError("Terminal state reached")

        current_player_id = self.playing_queue[0]
        (x, y), apples, actions_left, active = self.players[current_player_id]
        move_cost, in_the_wild_cost, in_a_house_cost, _ = self._season_specs()

        if action == Action.MOVE_LEFT and x > 0:
            x = x - 1 if x > 0 else x
            apples -= move_cost
        elif action == Action.MOVE_RIGHT:
            x = x + 1 if x < self._grid_size_x - 1 else x
            apples -= move_cost
        elif action == Action.MOVE_UP:
            y = y - 1 if y > 0 else y
            apples -= move_cost
        elif action == Action.MOVE_DOWN:
            y = y + 1 if y < self._grid_size_y - 1 else y
            apples -= move_cost
        elif action == Action.COLLECT_APPLES:
            for i, ((_x, _y), _apples) in enumerate(self.trees):
                if x == _x and y == _y and _apples > 0:
                    # Player can only collect available apples in the tree
                    gathered_apples = min(self._apple_gathering_capacity, _apples)
                    apples += gathered_apples
                    self.trees[i] = ((_x, _y), _apples - gathered_apples)
                    break
        elif action == Action.DO_NOTHING:
            pass

        actions_left = actions_left - 1

        # apply seasonal costs each time the turn ends
        if actions_left == 0:
            player_in_a_house = False
            for (_x, _y), _ in self.houses:
                if x == _x and y == _y:
                    player_in_a_house = True
                    break
            apples -= in_a_house_cost if player_in_a_house else in_the_wild_cost

        # Keep apples in bounds
        apples = max(apples, 0)
        apples = min(apples, MAX_APPLES_PER_PLAYER)

        # if player has 0 apples, ... dies
        if apples == 0:
            active = False
            actions_left = 0

        # update the player
        updated_player = ((x, y), apples, actions_left, active)
        self.players[current_player_id] = updated_player

        reward = self.setup['reward_function'](updated_player)

        self.is_terminal = self._next_turn()
        return self.state(), reward, self.is_terminal, None

    @property
    def player_ids(self):
        return list(range(len(self.players)))

    def _players_with_actions_left(self, player_ids):
        available = []
        for i in player_ids:
            (_, _, actions_left, active) = self.players[i]
            if active and actions_left > 0:
                available.append(i)
        return available

    def _draw_new_playing_queue(self):
        alive_players_ids = []
        for i, (coord, apples, _, active) in enumerate(self.players):
            if active:
                self.players[i] = (coord, apples, self._actions_per_turn, active)  # Update actions per turn
                alive_players_ids.append(i)
        return self.np_random.choice(alive_players_ids, len(alive_players_ids), replace=False) if len(
            alive_players_ids) > 0 else None

    def _next_turn(self) -> types.Is_terminal:

        # filter players without actions left
        self.playing_queue = self._players_with_actions_left(self.playing_queue)

        if len(self.playing_queue) == 0:

            # Draw another player queue
            self.playing_queue = self._draw_new_playing_queue()

            # all players died, this is a terminal state
            if self.playing_queue is None:
                return True

            self.current_turn += 1

            # Season changes
            if self.current_turn % self._turns_between_seasons:
                self.current_season = self._next_season()
                # Apply tree growth
                _, _, _, (apples_growth_lb, apples_growth_up) = self._season_specs()
                for i, ((_x, _y), _apples) in enumerate(self.trees):
                    _apples = _apples + self.np_random.randint(apples_growth_lb, apples_growth_up)
                    # Keep apples in bounds
                    _apples = min(_apples, MAX_APPLES_PER_TREE)
                    # Update apples
                    self.trees[i] = ((_x, _y), _apples)
        return False
