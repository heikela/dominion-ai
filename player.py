import random


class HumanPlayer:
    def observation(self, observation):
        print(observation)

    def choose(self, actions):
        print('Choose:')
        for i, action in enumerate(actions):
            print('{:3d} : {}'.format(i, action))
        choice = -1
        while choice < 0 or choice >= len(actions):
            choiceStr = input('Choose 0 to {} '.format(len(actions) - 1))
            try:
                choice = int(choiceStr)
            except ValueError:
                choice = -1
        return choice


class RandomPlayer:
    def __init__(self, print_observations=False):
        self._print_observations = print_observations

    def observation(self, observation):
        if self._print_observations:
            print(observation)

    def choose(self, actions):
        return random.randrange(len(actions))
