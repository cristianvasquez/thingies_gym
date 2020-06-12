from typing import Any, List, Tuple

from gym.utils import seeding, colorize

ROLL_DICE = 0
BUY_PROPERTY = 1
BUILD = 2
END_TURN = 3

GO_INCOME = 200
INITIAL_POSITION = 0
STARTING_PLAYER = 1
PLAYERS_INITIAL_MONEY = 1500

# Types
Reward = int
Is_terminal = bool
Actions = List[int]

# The game state
Position = int
Money = int
Active = int
Players = List[Tuple[Position, Money, Active]]
Owner = int
Buildings_in_property = int
Properties = List[Tuple[Owner, Buildings_in_property]]
Current_player = int
Can_roll_dice = bool

State = Tuple[Players, Properties, Current_player, Can_roll_dice, int, int]


class MonopolicRules():

    def __init__(self, board, seed=None, max_turns=10000):

        self.np_random, seed = seeding.np_random(seed)

        # Players
        # (position, money, active_status)
        self.players = [(INITIAL_POSITION, PLAYERS_INITIAL_MONEY, True) for i in
                        list(range(0, board.number_of_players + 1))]

        self.max_turns = max_turns
        self.current_turn = 0

        # by default, the bank is a player 0
        self.players[0] = (None, 0, False)

        # Properties can have an owner, and the number of houses built.
        # (owner_id,houses_built)
        self.properties = [(0, 0) for i in list(range(0, board.number_of_locations))]

        # Current player
        self.current_player = STARTING_PLAYER
        self.player_can_roll_dice = True

        self.actions = [ROLL_DICE, BUY_PROPERTY, BUILD, END_TURN]
        self.board = board
        self.terminal_state = False

    def state(self) -> State:
        return self.players, self.properties, self.current_player, self.player_can_roll_dice, self.current_turn, self.max_turns

    def current_player_name(self):
        return self.board.player_name(self.current_player)

    def possible_actions(self) -> Actions:
        actions = []
        location, money, active = self.players[self.current_player]

        # No actions if the player is not active
        if not active:
            raise Exception("Non active player requested actions {}".format(self.state()))

        # Can roll the dice, or end the turn
        if self.player_can_roll_dice:
            actions.append(ROLL_DICE)
        else:
            actions.append(END_TURN)

        current_owner, number_of_houses = self.properties[location]
        spec = self.board.specs[location]

        # Only can buy in any of the 'properties'
        if spec['class'] in ['Street', 'Railroad', 'Utility']:
            # Can buy the property if the owner is the bank
            if current_owner == 0:
                # And has enough money
                if (int(spec['price']) <= money):
                    actions.append(BUY_PROPERTY)

        # Only can build in 'streets'
        if spec['class'] in ['Street']:
            # Can build if the player is the owner
            if current_owner == self.current_player:

                # And does not have an hotel
                if number_of_houses < 5:
                    # And has enough money
                    if int(spec['build_cost']) <= money:
                        actions.append(BUILD)

        return actions

    def roll_dice(self) -> int:
        return self.np_random.randint(1, 13)

    def number_of_active_players(self) -> int:
        active_players = 0
        for (_, _, active) in self.players:
            if active:
                active_players += 1
        return active_players

    def _set_next_active_player(self) -> None:
        if self.number_of_active_players() == 0:
            self.current_player =  None
            return None

        def next_player(current):
            current += 1
            if current > len(self.players) - 1:
                current = 1
            _, _, active = self.players[current]
            return current if active else next_player(current)

        self.current_turn += 1
        self.current_player = next_player(self.current_player)
        self.player_can_roll_dice = True

    def step(self, action) -> Tuple[State, Reward, Is_terminal, Any]:
        possible_actions = self.possible_actions()

        if action not in possible_actions:
            raise Exception('action {} not in: {}'.format(action, possible_actions))

        if action == END_TURN:
            return self._action_end_turn()
        elif action == BUILD:
            return self._action_build()
        elif action == BUY_PROPERTY:
            return self._action_buy_property()
        elif action == ROLL_DICE:
            return self._action_roll_dice()

    def _number_of_winners(self):
        number_of_winners = 0
        for _, _money, _ in self.players:
            if _money > 0:
                number_of_winners += 1
        return number_of_winners

    def _action_end_turn(self) -> Tuple[State, Reward, Is_terminal, Any]:
        messages = []

        location, money, active = self.players[self.current_player]
        if self.number_of_active_players() <= 1:
            # There is only one, and the reward is the money
            self.terminal_state = True
            messages.append('player {} finishes with (${})'.format(self.current_player_name(), money))
            messages.append(
                'The game ends in turn {} with {} winners'.format(self.current_turn, self._number_of_winners()))
            return self.state(), money, self.terminal_state, messages
        elif self.current_turn > self.max_turns:
            # Game ran out of turns, the player gets the reward and goes not active
            messages.append('player {} finishes with (${})'.format(self.current_player_name(), money))
            self.players[self.current_player] = (location, money, False)
            self._set_next_active_player()
            return self.state(), money, self.terminal_state, messages
        else:
            # Player finishes turn, and turn goes to next_active_player
            messages.append('{} ends the turn'.format(self.current_player_name()))
            self._set_next_active_player()
            return self.state(), 0, self.terminal_state, messages

    def _action_roll_dice(self) -> Tuple[State, Reward, Is_terminal, Any]:
        """Doc
         """
        messages = []
        location, money, active = self.players[self.current_player]

        dice = self.roll_dice()
        self.player_can_roll_dice = False
        location += dice

        # If player goes through GO, receives some money
        if location > 39:
            location -= 40
            money += GO_INCOME
            messages.append('{} pass through GO ({})'.format(self.current_player_name(), GO_INCOME))

        spec = self.board.specs[location]
        location_name = self.board.location_name(location)
        messages.append('{} rolls {} and lands in {}'.format(self.current_player_name(), dice, location_name))

        # Some properties have a default income that can be positive or negative
        default_income = int(spec['default_income'])
        if default_income != 0:
            money += default_income
            messages.append('{} pays/receives: (${}) '.format(self.current_player_name(), default_income))

        # Has to pay rent if the property is already owned
        current_owner, number_of_houses = self.properties[location]
        if (current_owner != self.current_player) & (current_owner != 0):
            location_name = self.board.location_name(location)
            rent = self.get_rent_amount(number_of_houses, spec)

            # Pay the rent
            money -= rent

            # Add the money to the owner
            _location, _money, _active = self.players[current_owner]
            self.players[current_owner] = (_location, _money + rent, _active)
            current_owner_name = self.board.player_name(current_owner)
            messages.append(
                '{} lands in {} and pays (${}) to {} '.format(self.current_player_name(), location_name, rent,
                                                              current_owner_name))
        # Simple rule:
        # If the player goes broke, returns all his properties to the bank
        if money < 0:
            for i, (owner, number_of_houses) in enumerate(self.properties):
                if owner == self.current_player:
                    messages.append(
                        '{} returns {} to the bank'.format(self.current_player_name(), self.board.location_name(i)))
                    self.properties[i] = (0, 0)
            messages.append('{} is out!'.format(self.current_player_name()))
            active = False
            self.players[self.current_player] = (location, money, active)
            self._set_next_active_player()  # The player auto-ends

            # In super rare occasions, all players go broke.
            if self.number_of_active_players() == 0:
                self.terminal_state = True
                messages.append('The game ends... and everyone is a loser')

            # If you go broke, the reward is negative
            return self.state(), money, self.terminal_state, messages
        else:
            self.players[self.current_player] = (location, money, active)
            return self.state(), 0, self.terminal_state, messages

    def _action_buy_property(self) -> Tuple[State, Reward, Is_terminal, Any]:
        """Doc
         """
        location, money, active = self.players[self.current_player]
        spec = self.board.specs[location]

        # Update the money
        self.players[self.current_player] = (location, money - int(spec['price']), active)

        # Update the property owner
        current_owner, number_of_houses = self.properties[location]
        self.properties[location] = (self.current_player, number_of_houses)

        messages = []
        messages.append('{} buys {}'.format(self.current_player_name(), self.board.location_name(location)))
        return self.state(), 0, self.terminal_state, messages

    def _action_build(self) -> Tuple[State, Reward, Is_terminal, Any]:
        """Doc
        """
        location, money, active = self.players[self.current_player]
        spec = self.board.specs[location]

        # Update the money
        self.players[self.current_player] = (location, money - int(spec['build_cost']), active)

        # Update the houses
        current_owner, number_of_houses = self.properties[location]
        self.properties[location] = (current_owner, number_of_houses + 1)

        messages = []
        messages.append('{} builds in {}'.format(self.current_player_name(), self.board.location_name(location)))
        return self.state(), 0, self.terminal_state, messages

    def get_rent_amount(self, number_of_houses, spec):
        if (number_of_houses == 0):
            rent = spec['rent']
        elif (number_of_houses == 1):
            rent = spec['rent_house_1']
        elif (number_of_houses == 2):
            rent = spec['rent_house_2']
        elif (number_of_houses == 3):
            rent = spec['rent_house_3']
        elif (number_of_houses == 4):
            rent = spec['rent_house_4']
        elif (number_of_houses == 5):
            rent = spec['rent_hotel']
        else:
            raise Exception('number_of_houses should not be ', number_of_houses)
        return rent

    def render(self):
        print(self.state())
