from agents import Random_agent, Compulsive_buyer_agent, Compulsive_builder_agent, \
    Compulsive_buyer_builder_agent, Compulsive_roller_agent, Buyer_then_builder_agent
from environments import Monopoly


class Game:
    def __init__(self, number_of_players=6, max_turns=5000,board_file='board.csv'):
        self.default_agent = Random_agent()
        self.agents = {
            0: Random_agent(),
            1: Compulsive_buyer_agent(),
            2: Compulsive_builder_agent(),
            3: Compulsive_buyer_builder_agent(),
            4: Compulsive_roller_agent(),
            5: Buyer_then_builder_agent()
        }
        self.number_of_players = number_of_players
        self.total_rewards = [0 for i in range(self.number_of_players)]
        self.monopoly = Monopoly(number_of_players=number_of_players, max_turns=max_turns, board_file=board_file)

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
        self.monopoly.reset()
        terminal_state = False
        state = self.monopoly.state()
        for i in range(1, 500000):
            if terminal_state:
                break
            current_player = state[2]
            possible_actions = self.monopoly.possible_actions()

            agent = self.agent_for_player(current_player)
            action = agent.select_action(state, possible_actions)
            state, reward, terminal_state, messages = self.monopoly.step(action)
            self.total_rewards[current_player] += reward

    def game_with_history(self):
        history = []
        self.monopoly.reset()
        terminal_state = False
        state = self.monopoly.state()
        for i in range(1, 500000):
            if terminal_state:
                self.monopoly.render()
                return history
            current_player = state[2]
            possible_actions = self.monopoly.possible_actions()
            agent = self.agent_for_player(current_player)
            action = agent.select_action(state, possible_actions)
            state, reward, terminal_state, messages = self.monopoly.step(action)
            _, money, _ = state[0][current_player]
            history.append((current_player, money ,action, reward))
            print('{} [{}]'.format(reward, '\n'.join(messages)))

if __name__ == "__main__":
    game = Game(board_file='board_small.csv',number_of_players=6, max_turns =30000)
    game.run_games(50)
    # print(game.game_with_history())
