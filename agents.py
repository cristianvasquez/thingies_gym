import random

from monopoly_rules import State, Actions, BUY_PROPERTY, ROLL_DICE, END_TURN, BUILD

class Agent():
    def select_action(self,state:State,actions:Actions):
        raise NotImplementedError("Implement me!")

class Random_agent(Agent):
    def select_action(self, state: State, actions: Actions):
        players, properties, current_player, player_can_roll_dice, current_turn, max_turns = state
        return random.choice(actions)

class Compulsive_buyer_agent(Agent):
    def select_action(self, state: State, actions: Actions):
        if BUY_PROPERTY in actions:
            return BUY_PROPERTY

        return random.choice(actions)

class Compulsive_builder_agent(Agent):
    def select_action(self, state: State, actions: Actions):
        if BUILD in actions:
            return BUILD

        return random.choice(actions)

class Compulsive_buyer_builder_agent(Agent):
    def select_action(self, state: State, actions: Actions):
        if BUY_PROPERTY in actions:
            return BUY_PROPERTY
        if BUILD in actions:
            return BUILD
        return random.choice(actions)

class Compulsive_roller_agent(Agent):
    def select_action(self, state: State, actions: Actions):
        if ROLL_DICE in actions:
            return ROLL_DICE

        return random.choice(actions)

class Buyer_then_builder_agent(Agent):
    def __init__(self):
        self.late_game_agent = Compulsive_builder_agent()
        self.early_game_agent = Compulsive_buyer_agent()

    def select_action(self, state: State, actions: Actions):
        players, properties, current_player, player_can_roll_dice, current_turn, max_turns = state
        if current_turn < max_turns:
            return self.early_game_agent.select_action(state,actions)
        else:
            return  self.late_game_agent.select_action(state,actions)
