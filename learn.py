from game import Game
from player import RandomPlayer, ObservationIgnoringAgent
from collections import namedtuple, OrderedDict
import numpy as np
from estimators import TabularQEstimator
from policy import Greedy, EpsilonSoft
from datetime import datetime
import pickle

import matplotlib.pyplot as plt

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
            ('average_turns', np.mean([game.turns for game in self._stats])),
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
    all_stats = []
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
            all_stats.append(stats.summarise())
    return all_stats


def improve_via_self_play():
    total_games = 20000
    opponent = RandomPlayer()
    estimator = TabularQEstimator()
    old_estimator = None
    policy = EpsilonSoft(0.1, Greedy(estimator))
    games_between_stats = 100
    game = 0
    all_stats = []
    while game < total_games:
        stats = mc_evaluate(
            [estimator],
            policy=policy,
            opponent=opponent,
            games=1000,
            games_between_stats=games_between_stats)
        for stat_entry in stats:
            game += stat_entry['games']
        all_stats.extend(stats)
        print('current estimator')
        print(estimator)
        print('old estimator')
        print(old_estimator)
        if (stats[-1]['win_rate'] > 0.65):
            old_estimator = estimator
            opponent = ObservationIgnoringAgent(
                Greedy(old_estimator))
            policy = EpsilonSoft(0.1, Greedy(old_estimator))
            estimator = TabularQEstimator(estimator)
            print('Win rate of over 65% reached.')
            print('Making greedy version of current policy the opponent')
        else:
            policy = EpsilonSoft(0.1, Greedy(estimator))
    x_values = range(
        0,
        games_between_stats * len(all_stats),
        games_between_stats)
    plt.plot(
        x_values,
        list(map(lambda s: s['average_turns'], all_stats)),
        label='turns')
    plt.plot(
        x_values,
        list(map(lambda s: s['average_score'], all_stats)),
        label='winning score')
    plt.plot(
        x_values,
        list(map(lambda s: s['win_rate'] * 100, all_stats)),
        label='win rate')
    plt.xlabel('game')
    plt.legend()
    now = datetime.now()
    now = now.replace(microsecond=0)
    timestamp = now.isoformat()
    plt.savefig('results/learning-results-' + timestamp + '.png')
    with open('models/final-models-' + timestamp + '.p', 'wb') as file:
        pickle.dump(
            {
                'old_estimator': old_estimator,
                'latest_estimator': estimator
            }, file)


if __name__ == '__main__':
    improve_via_self_play()
