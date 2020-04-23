from spellcheck.editorial_actions import Match, Replacement, Removal, Insertion


class TrieNode:
    def __init__(self, is_terminal=False):
        self.is_terminal = is_terminal
        self.children = {}


class Trie:
    def __add_word(self, word):
        cur_node = self.root
        for cur_letter in word:
            if cur_letter not in cur_node.children.keys():
                cur_node.children[cur_letter] = TrieNode(False)
            cur_node = cur_node.children[cur_letter]
        cur_node.is_terminal = True

    def __build(self, dictionary):
        for cur_word in dictionary:
            self.__add_word(cur_word)

    def __init__(self, dictionary):
        self.root = TrieNode()
        self.__build(dictionary)


class TrieSearcher:
    def __init__(self, trie, word, max_changes, max_transitions, estimator,
                 can_replace=True, can_delete=True, can_insert=True):
        self.__max_changes = max_changes
        self.__can_replace = can_replace
        self.__can_delete = can_delete
        self.__can_insert = can_insert
        self.__word = word
        self.__trie = trie
        self.__max_transitions = max_transitions
        self.__estimator = estimator
        if len(word) <= 4:
            self.__ending_size = 1
        elif len(word) <= 6:
            self.__ending_size = 2
        else:
            self.__ending_size = 3

    def __get_transitions_from_node(self, word_index, cur_node, changes_made):
        result = []
        can_change = changes_made < self.__max_changes and \
                     len(self.__word) - word_index > self.__ending_size
        if word_index < len(self.__word):
            cur_letter = self.__word[word_index]
            for edge_letter in cur_node.children.keys():
                if cur_letter == edge_letter:
                    result.append(Match(cur_letter))
                elif can_change and self.__can_replace:
                    result.append(Replacement(cur_letter, edge_letter))
            if can_change and self.__can_delete:
                result.append(Removal(cur_letter))
        if can_change and self.__can_insert:
            for edge_letter in cur_node.children.keys():
                result.append(Insertion(edge_letter))
        return result

    def __get_best_transitions(self, actions, count_to_take, prev_action):
        return sorted(actions,
                      key=lambda cur_action: self.__estimator.estimate_editorial_action(
                          cur_action, prev_action
                      ),
                      reverse=True)[:count_to_take]

    # TODO: make cur_candidate persistent stack
    def __search(self, word_index, cur_node, cur_candidate, changes_made, prev_action):
        if word_index == len(self.__word) and cur_node.is_terminal:
            result = [cur_candidate]
        else:
            result = []
        all_transitions = \
            self.__get_transitions_from_node(word_index, cur_node, changes_made)
        best_transitions = \
            self.__get_best_transitions(all_transitions, self.__max_transitions, prev_action)
        for cur_transition in best_transitions:
            if type(cur_transition) is Match:
                result += self.__search(
                    word_index + 1, cur_node.children[cur_transition.letter],
                    cur_candidate + cur_transition.letter,
                    changes_made, cur_transition
                )
            elif type(cur_transition) is Replacement:
                result += self.__search(
                    word_index + 1, cur_node.children[cur_transition.letter_to],
                    cur_candidate + cur_transition.letter_to,
                    changes_made + 1, cur_transition
                )
            elif type(cur_transition) is Removal:
                result += self.__search(
                    word_index + 1, cur_node, cur_candidate, changes_made + 1, cur_transition
                )
            else:
                result += self.__search(
                    word_index, cur_node.children[cur_transition.letter],
                    cur_candidate + cur_transition.letter,
                    changes_made + 1, cur_transition
                )
        return result

    def search(self):
        return self.__search(0, self.__trie.root, "", 0, None)
