from game import Game
from player import RandomPlayer
from random import random, randrange
from collections import defaultdict, namedtuple, OrderedDict
import numpy as np
import copy


class QEstimatorBase:
    """Base class for estimators that can predict Q values based on
    state and action, and learn from experience based on
    externally provided learning target values"""
    def predict(S, A):
        raise NotImplementedError()

    def learnFrom(S, A, target):
        raise NotImplementedError()


class TabularQEstimator(QEstimatorBase):
    """An Estimator that simply keeps track of number of occurrences
    of each state, action pair, and the average of the provided target
    values"""
    def __init__(self, other=None):
        def default_for_s_a():
            return (0, 0)
        if other:
            self._q_estimates = copy.deepcopy(other._q_estimates)
        else:
            self._q_estimates = defaultdict(default_for_s_a)

    def predict(self, S, A):
        return self._q_estimates[(S, A)][1]

    def learnFrom(self, S, A, target):
        old_n, old_q = self._q_estimates[(S, A)]
        new_n = old_n + 1
        updated = (new_n, (old_n * old_q + target) / new_n)
        self._q_estimates[(S, A)] = updated

    def __repr__(self):
        return repr(self._q_estimates)

    def __str__(self):
        items = list(self._q_estimates.items())
        items.sort(key=lambda item: (-item[1][1], -item[1][0]))

        def format_rule(s_a, n_q):
            _, (action_type, *action_params) = s_a
            n, q = n_q
            return '{} {} : Q={}, N={}'.format(
                action_type, action_params, q, n)

        lines = [format_rule(s_a, n_q)
                 for s_a, n_q in items]
        return '\n'.join(lines)


GameStats = namedtuple('GameStats', 'win turns score')


class Stats:
    def __init__(self):
        self._stats = []

    def add_game(self, stats):
        self._stats.append(stats)

    def summarise(self):
        return OrderedDict([
            ('games', len(self._stats)),
            ('win_rate', np.mean([game.win for game in self._stats])),
            ('averate_turns', np.mean([game.turns for game in self._stats])),
            ('average_score', np.mean([game.score for game in self._stats])),
        ])


def dominion_stats_to_game_stats(stats, player):
    return GameStats(
        win=stats.winner == player,
        turns=stats.turns,
        score=stats.score)


def mc_evaluate(estimator, policy, opponent, games=1000, games_between_stats=100):
    for i in range(games):
        if i % games_between_stats == 0:
            stats = Stats()
        agent = ObservationIgnoringAgent(policy)
        game = Game({
            'epsilon': agent,
            'random': opponent
        })
        game.play()
        winner, score = game.get_winner()
        current_game_stats = game.get_stats()
        subjective_current_game_stats = dominion_stats_to_game_stats(
            current_game_stats, 'epsilon')
        stats.add_game(subjective_current_game_stats)
        if winner == 'epsilon':
            return_ = 1
        else:
            return_ = -1
        for S, A in agent.get_decisions():  # TODO split responsibilities
            estimator.learnFrom(S, A, return_)
        if (i + 1) % games_between_stats == 0:
            print('stats for games {} to {}'.format(
                i - games_between_stats + 1,
                i))
            for stat, value in stats.summarise().items():
                print('{} = {}'.format(stat, value))
    return stats


def improve_via_self_play():
    opponent = RandomPlayer()
    estimator = TabularQEstimator()
    old_estimator = estimator
    while True:
        stats = mc_evaluate(
            estimator,
            policy=EpsilonGreedy(estimator, 0.1),
            opponent=opponent,
            games=1000,
            games_between_stats=100)
        print(estimator)
        if (stats.summarise()['win_rate'] > 0.75):
            old_estimator = estimator
            opponent = ObservationIgnoringAgent(
                EpsilonGreedy(old_estimator, 0))
            estimator = TabularQEstimator(estimator)
            print('Win rate of over 75% reached.')
            print('Making greedy version of current policy the opponent')


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
        choice = self._policy.choose(actions)
        self._decisions.append(((), actions[choice]))
        return choice

    def get_decisions(self):
        return self._decisions


class EpsilonGreedy:
    def __init__(self, estimator, epsilon):
        self._estimator = estimator
        self._epsilon = epsilon

    def observation(self, observation):
        # TODO collect experience
        pass

    def choose(self, actions):
        if random() < self._epsilon:
            return randrange(len(actions))
        else:
            best = -1000
            best_i = None
            for i, action in enumerate(actions):
                Q = self._estimator.predict((), action)
                if Q > best:
                    best_i = i
                    best = Q
            return best_i


if __name__ == '__main__':
    improve_via_self_play()
