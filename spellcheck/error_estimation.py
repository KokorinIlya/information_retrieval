import math


class ErrorEstimator:
    def __init__(self, action_types_frequency, actions_frequency, context_actions_frequency, a, b, c):
        assert math.isclose(a + b + c, 1.)
        self.__action_types_frequency = action_types_frequency
        self.__actions_frequency = actions_frequency
        self.__context_actions_frequency = context_actions_frequency
        self.__a = a
        self.__b = b
        self.__c = c
        self.__total_actions = sum(self.__action_types_frequency.values())

    def estimate_editorial_action(self, cur_action, prev_action=None):
        estimation_by_type = self.__action_types_frequency.get(type(cur_action), 0.)
        estimation_by_action = self.__actions_frequency.get(cur_action, 0.)
        estimation_by_action_and_prev_action = \
            self.__action_types_frequency.get((prev_action, cur_action), 0.)
        return (
                       self.__a * estimation_by_type +
                       self.__b * estimation_by_action +
                       self.__c * estimation_by_action_and_prev_action
               ) / self.__total_actions
