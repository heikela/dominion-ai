from random import random, randrange


class Policy:
    """Abstract base for policies"""
    def choose(self, S, actions):
        raise NotImplementedError()


class Greedy(Policy):
    """A policy that acts greedily based on a given estimate for
    the action value function Q"""
    def __init__(self, q_estimator):
        self._estimator = q_estimator

    def choose(self, S, actions):
        best = self._estimator.predict(S, actions[0])
        best_i = 0
        for i, action in enumerate(actions):
            Q = self._estimator.predict(S, action)
            if Q > best:
                best_i = i
                best = Q
        return best_i


class EpsilonSoft(Policy):
    """A policy that explores randomly with probability epsilon, and otherwise
    follows any given policy (often greedy policy in practice)"""
    def __init__(self, epsilon, policy):
        self._epsilon = epsilon
        self._policy = policy

    def choose(self, S, actions):
        if random() < self._epsilon:
            return randrange(len(actions))
        else:
            return self._policy.choose(S, actions)
