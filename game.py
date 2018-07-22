import player
import dominion

class Game:
    def __init__(self):
        self.players = {
            'mikko': player.HumanPlayer(),
            'beta-ai': player.RandomPlayer()
        }
        self.game_state = dominion.GameState(['mikko', 'beta-ai'])

    def play(self):
        choice = self.game_state.get_first_choice()
        chosen = choice.alternatives[self.players[choice.player].choose(choice.alternatives)]
        while not self.game_state.is_game_over():
            choice = self.game_state.get_next_choice(chosen)
            chosen = choice.alternatives[self.players[choice.player].choose(choice.alternatives)]

if __name__ == '__main__':
    game = Game()
    game.play()
