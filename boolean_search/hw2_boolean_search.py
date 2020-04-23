from abc import abstractmethod
from argparse import ArgumentParser
from array import array
from bisect import bisect_left
from codecs import open as codecs_open
from zlib import crc32

HASH_TABLE_SIZE = 100000


def hash_string(string, mod):
    return crc32(bytes(string, "utf-8")) % mod


class Index:
    def __build_index(self, docs_file):
        index = [array('H', []) for _ in range(self.__index_size)]
        with open(docs_file, mode="r") as file:
            for cur_line in file:
                line_parts = cur_line.split()
                doc_id = int(line_parts[0])
                words = line_parts[1:]
                for word in set(words):
                    word_hash = hash_string(word, self.__index_size)
                    assert len(index[word_hash]) == 0 or doc_id >= index[word_hash][-1]
                    if len(index[word_hash]) == 0 or doc_id > index[word_hash][-1]:
                        index[word_hash].append(doc_id)
        return index

    def __init__(self, docs_file, index_size):
        self.__index_size = index_size
        self.__reverse_index = self.__build_index(docs_file)

    def get_docs_by_word(self, word):
        word_hash = hash_string(word, self.__index_size)
        return self.__reverse_index[word_hash]


class Parser:
    def __init__(self, line):
        self.__line = line + '$'
        self.__pos = 0

    def __skip(self, s):
        if self.__line.startswith(s, self.__pos):
            self.__pos += len(s)
            return True
        return False

    def __parse_disjunction(self):
        x = self.__parse_conjunction()
        while self.__skip('|'):
            x = OrNode(x, self.__parse_conjunction())
        return x

    def __parse_conjunction(self):
        x = self.__parse_atom()
        while self.__skip(' '):
            x = AndNode(x, self.__parse_atom())
        return x

    def __parse_atom(self):
        if self.__skip('('):
            x = self.__parse_disjunction()
            self.__skip(')')
            return x
        x = ''
        while self.__line[self.__pos].isdigit() or self.__line[self.__pos].isalpha():
            x += self.__line[self.__pos]
            self.__pos += 1
        return TreeLeaf(x)

    def parse(self):
        return self.__parse_disjunction()


class TreeElement:
    @abstractmethod
    def get_documents(self, index):
        raise NotImplementedError("abstract get_documents")


class TreeLeaf(TreeElement):
    def __init__(self, word):
        self.word = word

    def get_documents(self, index):
        return index.get_docs_by_word(self.word)


class TreeNode:
    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @abstractmethod
    def _process_children_results(self, left_result, right_result):
        raise NotImplementedError("abstract _process_children_results")

    def get_documents(self, index):
        left_res = self.__left.get_documents(index)
        right_res = self.__right.get_documents(index)
        return self._process_children_results(left_res, right_res)


class AndNode(TreeNode):
    def _process_children_results(self, left_result, right_result):
        result = array('H', [])
        left_index = 0
        right_index = 0
        while left_index < len(left_result) and right_index < len(right_result):
            left_elem = left_result[left_index]
            right_elem = right_result[right_index]
            if left_elem < right_elem:
                left_index += 1
            elif left_elem > right_elem:
                right_index += 1
            else:
                result.append(left_elem)
                left_index += 1
                right_index += 1
        return result

    def __init__(self, left, right):
        super().__init__(left, right)


class OrNode(TreeNode):
    def _process_children_results(self, left_result, right_result):
        result = array('H', [])
        left_index = 0
        right_index = 0
        while (left_index < len(left_result)) and (right_index < len(right_result)):
            left_elem = left_result[left_index]
            right_elem = right_result[right_index]
            if left_elem < right_elem:
                result.append(left_elem)
                left_index += 1
            elif left_elem > right_elem:
                result.append(right_elem)
                right_index += 1
            else:
                result.append(left_elem)
                left_index += 1
                right_index += 1
        result += left_result[left_index:]
        result += right_result[right_index:]
        return result

    def __init__(self, left, right):
        super().__init__(left, right)


class QueryTree:
    def __init__(self, qid, query):
        self.__qid = qid
        self.__tree = Parser(query).parse()

    def search(self, index):
        return self.__qid, self.__tree.get_documents(index)


def get_objects(objects_file):
    with open(objects_file, 'r') as file:
        file.readline()
        for cur_line in file:
            object_id, query_id, document_id = cur_line.split(',')
            yield object_id, int(query_id), int(document_id)


class SearchResults:
    def __init__(self):
        self.__results = {}

    def add(self, found):
        qid, docs = found
        self.__results[qid] = docs

    def print_submission(self, objects_file, submission_file):
        with open(submission_file, mode="w") as file:
            file.write("ObjectId,Relevance\n")
            for object_id, query_id, document_id in get_objects(objects_file):
                query_result = self.__results[query_id]
                possible_doc_index = bisect_left(query_result, document_id)
                if possible_doc_index < len(query_result) and query_result[possible_doc_index] == document_id:
                    file.write(object_id + ",1\n")
                else:
                    file.write(object_id + ",0\n")


def main():
    # Command line arguments.
    parser = ArgumentParser(description="Homework 2: Boolean Search")
    parser.add_argument("--queries_file", required=True, help="queries.numerate.txt")
    parser.add_argument("--objects_file", required=True, help="objects.numerate.txt")
    parser.add_argument("--docs_file", required=True, help="docs.tsv")
    parser.add_argument("--submission_file", required=True, help="output file with relevances")
    args = parser.parse_args()

    # Build index.
    index = Index(args.docs_file, HASH_TABLE_SIZE)

    # Process queries.
    search_results = SearchResults()
    with codecs_open(args.queries_file, mode="r", encoding="utf-8") as queries_fh:
        for line in queries_fh:
            line_parts = line.rstrip("\n").split("\t")
            qid = int(line_parts[0])
            query = line_parts[1]

            # Parse query.
            query_tree = QueryTree(qid, query)

            # Search and save results.
            search_results.add(query_tree.search(index))

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)


if __name__ == "__main__":
    main()
