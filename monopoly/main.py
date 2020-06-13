from monopoly.agents import Random_agent, Compulsive_buyer_agent, Compulsive_builder_agent, \
    Compulsive_buyer_builder_agent, Compulsive_roller_agent, Buyer_then_builder_agent
from monopoly.environment import Monopoly, DEFAULT_SETUP

class Game:
    def __init__(self, config=DEFAULT_SETUP):
        self.default_agent = Random_agent()
        self.agents = {
            0: Random_agent(),
            1: Compulsive_buyer_agent(),
            2: Compulsive_builder_agent(),
            3: Compulsive_buyer_builder_agent(),
            4: Compulsive_roller_agent(),
            5: Buyer_then_builder_agent()
        }
        self.number_of_players = config['number_of_players']
        self.total_rewards = [0 for i in range(self.number_of_players)]
        self.game = Monopoly(config=config)

    def run_games(self, number_of_games):
        for i in range(number_of_games):
            if (i % 10)==0:
                print('played {}/{}'.format(i,number_of_games))
            self.run_game()

        print("Average of reward over {} games".format(number_of_games))
        for i in range(self.number_of_players):
            average = self.total_rewards[i] / number_of_games
            agent_type = type(self.agent_for_player(i))
            print("{} average: {}".format(agent_type, average))

    def agent_for_player(self,player):
        return self.agents[player] if player in self.agents else self.default_agent

    def run_game(self):
        self.game.reset()
        terminal_state = False
        state = self.game.state()
        for i in range(1, 500000):
            if terminal_state:
                break
            current_player = state[2]
            possible_actions = self.game.possible_actions()

            agent = self.agent_for_player(current_player)
            action = agent.select_action(state, possible_actions)
            state, reward, terminal_state, messages = self.game.step(action)
            self.total_rewards[current_player] += reward

    def game_with_history(self):
        history = []
        self.game.reset()
        terminal_state = False
        state = self.game.state()
        for i in range(1, 500000):
            if terminal_state:
                self.game.render()
                return history
            current_player = state[2]
            possible_actions = self.game.possible_actions()
            agent = self.agent_for_player(current_player)
            action = agent.select_action(state, possible_actions)
            state, reward, terminal_state, messages = self.game.step(action)
            _, money, _ = state[0][current_player]
            history.append((current_player, money ,action, reward))
            print('{} [{}]'.format(reward, '\n'.join(messages)))

if __name__ == "__main__":
    TEST_BOARD = {
        'board_file': 'monopoly/boards/board_small.csv',
        'number_of_players': 6,
        'max_money': 5000,
        'max_turns': 1000
    }
    game = Game(config=TEST_BOARD)
    game.run_games(10000)
    # history = game.game_with_history()

