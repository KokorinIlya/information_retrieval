from boolean_search.request_tree import TreeNode, TreeLeaf


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
        return TreeLeaf(x.upper())

    def parse(self):
        return self.__parse_disjunction()


def main():
    line = input()
    parser = Parser(line)
    e = parser.parse()
    print(e.to_string())


if __name__ == '__main__':
    main()
