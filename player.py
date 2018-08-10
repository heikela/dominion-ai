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


class ObservationIgnoringAgent:
    """An agent that ignores observations given to it, and passes
    an empty tuple as the state to the policy function given
    to the constructor. Acts according to the policy."""
    def __init__(self, policy):
        self._policy = policy
        self._decisions = []

    def observation(self, observation):
        pass

    def choose(self, actions):
        choice = self._policy.choose((), actions)
        self._decisions.append(((), actions[choice]))
        return choice

    def get_decisions(self):
        return self._decisions


def identity_projection(state):
    return state


class AgentWithLatestObservationAsState:
    """An agent that assumes that the latest observation is the state.
    Passes this and the choices to the policy and acts accordingly."""
    def __init__(self, policy, projection=identity_projection):
        self._policy = policy
        self._decisions = []
        self._state = ()
        self._projection = projection

    def observation(self, observation):
        self._state = self._projection(observation)

    def choose(self, actions):
        choice = self._policy.choose(self._state, actions)
        self._decisions.append((self._state, actions[choice]))
        return choice

    def get_decisions(self):
        return self._decisions
