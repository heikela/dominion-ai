from player import HumanPlayer, RandomPlayer
import dominion


class Game:
    def __init__(self):
        self.players = {
            #'mikko': HumanPlayer(),
            'mikko': RandomPlayer(print_observations=True),
            'beta-ai': RandomPlayer()
        }
        self.game_state = dominion.GameState(['mikko', 'beta-ai'])

    def play(self):
        observations, choice = self.game_state.get_first_choice()
        chosen = self._next_choice(observations, choice)
        while not self.game_state.is_game_over():
            observations, choice = self.game_state.get_next_choice(chosen)
            chosen = self._next_choice(observations, choice)
        self.game_state.print_result()

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
