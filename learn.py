from game import Game
from player import RandomPlayer
from collections import namedtuple, OrderedDict
import numpy as np
from estimators import TabularQEstimator
from policy import Greedy, EpsilonSoft


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


def mc_evaluate(estimators,
                policy,
                opponent,
                games=1000,
                games_between_stats=100):
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
        for estimator in estimators:
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
    old_estimator = None
    policy = EpsilonSoft(0.1, Greedy(estimator))
    while True:
        stats = mc_evaluate(
            [estimator],
            policy=policy,
            opponent=opponent,
            games=1000,
            games_between_stats=100)
        print('current estimator')
        print(estimator)
        print('old estimator')
        print(old_estimator)
        if (stats.summarise()['win_rate'] > 0.65):
            old_estimator = estimator
            opponent = ObservationIgnoringAgent(
                Greedy(old_estimator))
            policy = EpsilonSoft(0.1, Greedy(old_estimator))
            estimator = TabularQEstimator(estimator)
            print('Win rate of over 65% reached.')
            print('Making greedy version of current policy the opponent')
        else:
            policy = EpsilonSoft(0.1, Greedy(estimator))


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


if __name__ == '__main__':
    improve_via_self_play()