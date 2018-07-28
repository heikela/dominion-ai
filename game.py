from player import HumanPlayer, RandomPlayer
from random import shuffle
import dominion


class Game:
    def __init__(self, players={
                                'mikko': HumanPlayer(),
                                'beta-ai': RandomPlayer()
                                }):
        self.players = players
        player_names = list(players.keys())
        shuffle(player_names)
        self.game_state = dominion.GameState(player_names)

    def play(self):
        observations, choice = self.game_state.get_first_choice()
        chosen = self._next_choice(observations, choice)
        while not self.game_state.is_game_over():
            observations, choice = self.game_state.get_next_choice(chosen)
            chosen = self._next_choice(observations, choice)

    def get_winner(self):
        return self.game_state.get_winner()

    def get_stats(self):
        return self.game_state.get_stats()

    def _communicate_observations(self, observations):
        for observation in observations:
            for player_name, player in self.players.items():
                if player_name == observation.audience:
                    player.observation(observation.private)
                else:
                    player.observation(observation.public)

    def _next_choice(self, observations, choice):
        self._communicate_observations(observations)
        choice_idx = self.players[choice.player].choose(choice.alternatives)
        return choice.alternatives[choice_idx]


if __name__ == '__main__':
    game = Game()
    game.play()
    game.game_state.print_result()
