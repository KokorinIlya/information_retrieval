class Ranker:
    def __init__(self, words_frequency, rel_threshold, absolute_threshold):
        self.__words_frequency = words_frequency
        self.__rel_threshold = rel_threshold
        self.__absolute_threshold = absolute_threshold
        self.__total_words = sum(self.__words_frequency.values())

    def get_best(self, word, candidates):
        if len(candidates) == 0:
            return None
        best_candidate = max(candidates, key=lambda candidate: self.__words_frequency.get(candidate, 0))
        best_freq = self.__words_frequency.get(best_candidate, 0)
        if best_freq / self.__total_words > self.__absolute_threshold and \
                best_freq / self.__words_frequency.get(word, 1) > self.__rel_threshold:
            return best_candidate
        else:
            return None
