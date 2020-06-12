from agents import Random_agent, Compulsive_buyer_agent, Compulsive_builder_agent, \
    Compulsive_buyer_builder_agent, Compulsive_roller_agent, Buyer_then_builder_agent
from environments import Monopoly


class Game:

    def __init__(self):
        self.agents = {
            1: Random_agent(),
            2: Compulsive_buyer_agent(),
            3: Compulsive_builder_agent(),
            4: Compulsive_buyer_builder_agent(),
            5: Compulsive_roller_agent(),
            6: Buyer_then_builder_agent()
        }
        self.total_rewards = [0 for i, _ in enumerate(self.agents)]
        self.number_of_players = len(self.agents)
        self.monopoly = Monopoly(number_of_players=6, max_turns=300)

    def run_games(self, number_of_games):
        for i in range(number_of_games):
            self.run_game()

        print("Average of reward over {} games".format(number_of_games))
        for i, agent in enumerate(self.agents):
            average = self.total_rewards[i] / number_of_games
            agent_type = type(self.agents[agent])
            print("{} average: {}".format(agent_type, average))

    def run_game(self):
        self.monopoly.reset()
        terminal_state = False
        state = self.monopoly.state()
        for i in range(1, 500000):
            if terminal_state:
                break
            current_player = state[2]
            possible_actions = self.monopoly.possible_actions()
            action = self.agents[current_player].select_action(state, possible_actions)
            state, reward, terminal_state, messages = self.monopoly.step(action)
            self.total_rewards[current_player - 1] += reward

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
            action = self.agents[current_player].select_action(state, possible_actions)
            state, reward, terminal_state, messages = self.monopoly.step(action)
            _, money, _ = state[0][current_player]
            history.append((current_player, money ,action, reward))
            print('{} [{}]'.format(reward, '\n'.join(messages)))


if __name__ == "__main__":
    game = Game()
    # game.run_games(1000)
    print(game.game_with_history())
