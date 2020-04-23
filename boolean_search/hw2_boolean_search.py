import argparse
import codecs
from abc import abstractmethod


class Index:
    def __init__(self, docs_file):
        self.reverse_index = {}
        with open(docs_file, 'r') as file:
            for cur_line in file.readlines():
                parts = cur_line.split()
                doc_id = int(parts[0])
                words = parts[1:]
                for cur_word in words:
                    if cur_word not in self.reverse_index:
                        self.reverse_index[cur_word] = set()
                    self.reverse_index[cur_word].add(doc_id)


class TreeElement:
    @abstractmethod
    def to_string(self):
        raise NotImplementedError("abstract to_string")

    @abstractmethod
    def get_documents(self, reverse_index):
        raise NotImplementedError("abstract get_documents")


class TreeLeaf:
    def __init__(self, word):
        self.word = word

    def to_string(self):
        return self.word

    def get_documents(self, reverse_index):
        return reverse_index.get(self.word, set())


class TreeNode:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def to_string(self):
        return "(" + self.op + " " + self.left.to_string() + " " + self.right.to_string() + ")"

    def get_documents(self, reverse_index):
        left_set = self.left.get_documents(reverse_index)
        right_set = self.right.get_documents(reverse_index)
        if self.op == '|':
            return left_set | right_set
        else:
            return left_set & right_set


class Parser:
    def __init__(self, _line):
        self.line = _line + '$'
        self.pos = 0

    def __skip(self, s):
        if self.line.startswith(s, self.pos):
            self.pos += len(s)
            return True
        return False

    def __parse_disjunction(self):
        x = self.__parse_conjunction()
        while self.__skip('|'):
            x = TreeNode('|', x, self.__parse_conjunction())
        return x

    def __parse_conjunction(self):
        x = self.__parse_atom()
        while self.__skip(' '):
            x = TreeNode('&', x, self.__parse_atom())
        return x

    def __parse_atom(self):
        if self.__skip('('):
            x = self.__parse_disjunction()
            self.__skip(')')
            return x
        x = ''
        while self.line[self.pos].isdigit() or self.line[self.pos].isalpha():
            x += self.line[self.pos]
            self.pos += 1
        return TreeLeaf(x)

    def parse(self):
        return self.__parse_disjunction()


class QueryTree:
    def __init__(self, qid, query):
        self.qid = qid
        self.tree = Parser(query).parse()

    def search(self, index):
        return self.qid, self.tree.get_documents(index.reverse_index)


def get_objects(objects_file):
    with open(objects_file, 'r') as file:
        file.readline()
        for cur_line in file.readlines():
            object_id, query_id, document_id = cur_line.split(',')
            yield object_id, int(query_id), int(document_id)


class SearchResults:
    def __init__(self):
        self.result = {}

    def add(self, found):
        qid, docs = found
        self.result[qid] = docs

    def print_submission(self, objects_file, submission_file):
        with open(submission_file, 'w') as file:
            file.write("ObjectId,Relevance\n")
            for object_id, query_id, document_id in get_objects(objects_file):
                if document_id in self.result[query_id]:
                    file.write(object_id + ",1\n")
                else:
                    file.write(object_id + ",0\n")


def main():
    # Command line arguments.
    parser = argparse.ArgumentParser(description='Homework 2: Boolean Search')
    parser.add_argument('--queries_file', required=False, default='data/queries.numerate.txt')
    parser.add_argument('--objects_file', required=False, default='data/objects.numerate.txt')
    parser.add_argument('--docs_file', required=False, default='data/docs.tsv')
    parser.add_argument('--submission_file', required=False, default='data/result.txt')
    args = parser.parse_args()

    # Build index.
    index = Index(args.docs_file)

    # Process queries.
    search_results = SearchResults()
    with codecs.open(args.queries_file, mode='r', encoding='utf-8') as queries_fh:
        for line in queries_fh:
            fields = line.rstrip('\n').split('\t')
            qid = int(fields[0])
            query = fields[1]

            # Parse query.
            query_tree = QueryTree(qid, query)

            # Search and save results.
            search_results.add(query_tree.search(index))

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)


if __name__ == "__main__":
    main()
