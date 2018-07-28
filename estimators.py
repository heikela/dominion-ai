from collections import defaultdict
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


class CappedTabularQEstimator(TabularQEstimator):
    """An Estimator that simply keeps track of number of occurrences
    of each state, action pair, and the average of the provided target
    values, but a maximum imposed on weight given to old observations"""
    def __init__(self, cap, other=None):
        def default_for_s_a():
            return (0, 0)

        self._cap = cap
        if other:
            self._q_estimates = copy.deepcopy(other._q_estimates)
        else:
            self._q_estimates = defaultdict(default_for_s_a)

    def learnFrom(self, S, A, target):
        old_n, old_q = self._q_estimates[(S, A)]
        if old_n > self._cap:
            old_n = self._cap
        new_n = old_n + 1
        updated = (new_n, (old_n * old_q + target) / new_n)
        self._q_estimates[(S, A)] = updated
