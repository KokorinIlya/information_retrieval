import pandas
from spellcheck.language_detection import is_russian
from spellcheck.trie import Trie, TrieSearcher
from spellcheck.levenshtein_calculator import calc_distance
from spellcheck.error_estimation import ErrorEstimator
from spellcheck.ranking import Ranker


def main():
    words_data = pandas.read_csv('data/words.csv', keep_default_na=False)
    russian_words = words_data[words_data.Id.apply(is_russian)]
    trie = Trie(russian_words.Id)
    action_types_frequency = {}
    actions_frequency = {}
    context_actions_frequency = {}

    train_data = pandas.read_csv('data/train.csv', dtype={'Id': str, 'Expected': str})
    clear_data = train_data[(train_data.Id.apply(len) < 100) & (train_data.Expected.apply(len) < 100)]
    for cur_row in clear_data.itertuples():
        word, correct_word = cur_row.Id, cur_row.Expected
        dist, actions = calc_distance(word, correct_word)
        prev_action = None
        for cur_action in actions:
            # TODO: try to write better code
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

    estimator = ErrorEstimator(action_types_frequency, actions_frequency, context_actions_frequency,
                               0., 1., 0.)

    words_frequency = {}
    for cur_row in russian_words.itertuples():
        cur_word = cur_row.Id
        cur_freq = cur_row.Freq
        words_frequency[cur_word] = cur_freq
    ranker = Ranker(words_frequency, 0., 0.)

    data_to_predict = pandas.read_csv('data/no_fix.submission.csv',
                                      dtype={'Id': str, 'Predicted': str}, na_values=[]).Id
    with open('data/answer.csv', 'w') as file:
        file.write('Id,Predicted\n')
        for cur_word in data_to_predict:
            if type(cur_word) is not str:
                cur_word = str(cur_word)
            if len(cur_word) < 100 and is_russian(cur_word):
                searcher = TrieSearcher(trie, cur_word, 1, 10, estimator, True, False, False)
                candidates = searcher.search()
                best_candidate = ranker.get_best(cur_word, candidates)
                if best_candidate is None:
                    answer = cur_word
                else:
                    # if best_candidate != cur_word:
                    #    print(cur_word, best_candidate)
                    answer = best_candidate
            else:
                answer = cur_word
            file.write('{0},{1}\n'.format(cur_word, answer))


if __name__ == '__main__':
    main()
