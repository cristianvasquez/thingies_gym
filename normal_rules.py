from gym.utils import seeding, colorize

ROLL_DICE = 0
BUY_PROPERTY = 1
BUILD = 2
END_TURN = 3

GO_INCOME = 200


# The normal rules
class NormalGame():

    def __init__(self, board, seed=None):

        self.np_random, seed = seeding.np_random(seed)

        initial_position = 0
        players_initial_money = 1500
        bank_initial_money = 1000000
        starting_player = 1

        # Players have a position, their money, and their active status.
        self.players = [(initial_position, players_initial_money, True) for i in list(range(0, board.number_of_players + 1))]

        # by default, the bank is a player 0
        # And has a lot of money
        self.players[0] = (None, bank_initial_money, None)

        # Properties can have an owner, and the number of houses built.
        self.properties = [(0, 0) for i in list(range(0, board.number_of_locations))]

        # Current player
        self.current_player = starting_player
        self.player_can_roll_dice = True

        self.actions = [ROLL_DICE, BUY_PROPERTY, BUILD, END_TURN]
        self.board = board
        self.terminal_state = False

    def toggle_verbose(self):
        self.verbose = not self.verbose

    def state(self):
        return self.players, self.properties, self.current_player, self.player_can_roll_dice

    def possible_actions(self, player):
        actions = []
        location, money, active = self.players[player]

        # No possible actions if the game ended
        if self.terminal_state:
            return actions

        # No actions if is not your turn
        if self.current_player != player:
            return actions

        # No actions if the player is not active
        if not active:
            actions.append(END_TURN)
            return actions

        # Can roll the dice, or end the turn
        if self.player_can_roll_dice:
            actions.append(ROLL_DICE)
        else:
            actions.append(END_TURN)

        current_owner, number_of_houses = self.properties[location]
        spec = self.board.location(location)

        # Only can buy 'properties'
        if spec['class'] in ['Street', 'Railroad', 'Utility']:
            # Can buy the property if the owner is the bank
            if current_owner == 0:
                # And has enough money
                if (int(spec['price']) <= money):
                    actions.append(BUY_PROPERTY)

        # Only can build in 'streets'
        if spec['class'] in ['Street']:
            # Can build if the player is the owner
            if current_owner == player:

                # And does not have an hotel
                if number_of_houses < 5:
                    # And has enough money
                    if int(spec['build_cost']) <= money:
                        actions.append(BUILD)

        return actions

    def roll_dice(self):
        return self.np_random.randint(1, 13)

    def is_terminal_state(self):
        # If only one is active, the game is in a terminal state
        active_players = 0
        for (_, _, active) in self.players:
            if active:
                active_players += 1
        return True if active_players <= 1 else False

    def do_action(self, player, action):
        possible_actions = self.possible_actions(player)

        if action not in possible_actions:
            raise Exception('action {} not in: {}'.format(action, possible_actions))

        player_name = self.board.player_name(player)
        location, money, active = self.players[player]
        messages = []

        def next_player(current):
            current += 1
            if current > len(self.players) - 1:
                current = 1
            _, _, active = self.players[current]
            return current if active else next_player(current)

        if action == END_TURN:
            messages.append('{} ends the turn'.format(player_name))
            self.current_player = next_player(self.current_player)
            self.player_can_roll_dice = True

            if self.is_terminal_state():
                self.terminal_state = True
                messages.append('the game ended')
            return self.state(), 0, self.terminal_state, messages

        elif action == BUILD:
            current_owner, number_of_houses = self.properties[location]
            spec = self.board.location(location)
            self.players[player] = (location, money - int(spec['build_cost']), active)
            self.properties[location] = (player, number_of_houses + 1)
            location_name = self.board.location_name(location)
            messages.append('{} builds in {}'.format(player_name, location_name))
            return self.state(), 0, self.terminal_state, messages

        elif action == BUY_PROPERTY:
            current_owner, number_of_houses = self.properties[location]
            spec = self.board.location(location)
            self.players[player] = (location, money - int(spec['price']), active)
            self.properties[location] = (player, number_of_houses)
            location_name = self.board.location_name(location)
            messages.append('{} buys {}'.format(player_name, location_name))
            return self.state(), 0, self.terminal_state, messages

        elif action == ROLL_DICE:
            dice = self.roll_dice()
            self.player_can_roll_dice = False

            messages.append('{} rolls {} '.format(player_name, dice))
            location += dice
            if location > 39:
                location -= 40
                money += GO_INCOME
                messages.append('{} pass through GO ({})'.format(player_name, GO_INCOME))

            current_owner, number_of_houses = self.properties[location]
            spec = self.board.location(location)

            # Some properties have a default income that can be positive or negative
            default_income = int(spec['default_income'])
            if default_income != 0:
                money += default_income
                location_name = self.board.location_name(location)
                messages.append('{} lands in {} ({}) '.format(player_name, location_name, default_income))

            # Has to pay rent if the property is already owned
            if (current_owner != player) & (current_owner != 0):
                location_name = self.board.location_name(location)
                rent = self.get_rent_amount(number_of_houses, spec)

                # Pay the rent
                money = money - rent

                # Add the money to the owner
                _location, _money, _active = self.players[current_owner]
                self.players[current_owner] = (_location, _money + rent, _active)
                current_owner_name = self.board.player_name(current_owner)
                messages.append('{} lands in {} and pays {} to {} '.format(player_name, location_name, rent, current_owner_name))

            # Simple rule:
            # If the player goes broke, returns all his properties to the bank
            if money < 0:
                for i,(owner,number_of_houses) in enumerate(self.properties):
                    if owner == player:
                        messages.append('{} returns {} to the bank'.format(player_name, self.board.location_name(i)))
                        self.properties[i] = (0,0)
                messages.append('{} is out!'.format(player_name))
                active = False

            self.players[player] = (location, money, active)
            # If you go broke, the reward is negative
            return self.state(), 0 if active else -1000, self.terminal_state, messages

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
