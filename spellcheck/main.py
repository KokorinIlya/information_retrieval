import pandas
import re
from spellcheck.trie import Trie, TrieSearcher
from spellcheck.levenshtein_calculator import calc_distance
from spellcheck.error_estimation import ErrorEstimator


def __is_russian(word):
    return re.match('^[а-яА-ЯёЁ]+$', word) is not None


def __get_russian_words(words_file_path):
    words_data = pandas.read_csv(words_file_path, keep_default_na=False)
    return words_data[words_data.Id.apply(__is_russian)]


def __get_train_data(train_file_path):
    train_data = pandas.read_csv(train_file_path, dtype={'Id': str, 'Expected': str}, keep_default_na=False)
    return train_data[(train_data.Id.apply(len) < 50) & (train_data.Expected.apply(len) < 50)]


def __fill_frequencies(train_data):
    action_types_frequency = {}
    actions_frequency = {}
    context_actions_frequency = {}

    for cur_row in train_data.itertuples():
        word, correct_word = cur_row.Id, cur_row.Expected
        dist, actions = calc_distance(word, correct_word)
        prev_action = None
        for cur_action in actions:
            if type(cur_action) not in action_types_frequency:
                action_types_frequency[type(cur_action)] = 0
            action_types_frequency[type(cur_action)] += 1

            if cur_action not in actions_frequency:
                actions_frequency[cur_action] = 0
            actions_frequency[cur_action] += 1

            if prev_action is not None:
                if (prev_action, cur_action) not in context_actions_frequency:
                    context_actions_frequency[(prev_action, cur_action)] = 0
                context_actions_frequency[(prev_action, cur_action)] += 1

            prev_action = cur_action

    return action_types_frequency, actions_frequency, context_actions_frequency


def __get_prediction(cur_word, trie, estimator, words_frequency, absolute_threshold, rel_threshold):
    if len(cur_word) < 50 and __is_russian(cur_word):
        searcher = TrieSearcher(trie, cur_word, 1, 10, estimator, True, False, False)
        candidates = searcher.search()

        if len(candidates) == 0:
            return cur_word
        best_candidate = max(candidates, key=lambda candidate: words_frequency.get(candidate, 0))
        best_freq = words_frequency.get(best_candidate, 0)
        if best_freq > absolute_threshold and best_freq / words_frequency.get(cur_word, 1) > rel_threshold:
            return best_candidate
        else:
            return cur_word
    else:
        return cur_word


def main():
    russian_words = __get_russian_words('data/words.csv')
    trie = Trie(russian_words.Id)

    train_data = __get_train_data('data/train.csv')
    action_types_frequency, actions_frequency, context_actions_frequency = __fill_frequencies(train_data)
    estimator = ErrorEstimator(action_types_frequency, actions_frequency, context_actions_frequency,
                               0., 1., 0.)

    words_frequency = {cur_row.Id: cur_row.Freq for cur_row in russian_words.itertuples()}

    data_to_predict = pandas.read_csv('data/no_fix.submission.csv',
                                      dtype={'Id': str, 'Predicted': str}, keep_default_na=False).Id
    with open('data/answer.csv', 'w') as file:
        file.write('Id,Predicted\n')
        for cur_word in data_to_predict:
            answer = __get_prediction(cur_word, trie, estimator, words_frequency, 200, 3.)
            file.write('{0},{1}\n'.format(cur_word, answer))


if __name__ == '__main__':
    main()
