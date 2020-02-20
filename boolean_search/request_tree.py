from abc import abstractmethod


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
