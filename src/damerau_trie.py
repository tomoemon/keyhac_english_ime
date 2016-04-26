# -*- coding: utf-8 -*-
from operator import itemgetter
import pickle


class DamerauTrieNode(dict):
    def __init__(self, row_letter="", ancestors=[], da={}):
        self.word = ""
        self.row_letter = row_letter
        self.col_letter = ""
        self.ancestors = ancestors
        self.ancestors_with_self = ancestors[1:] + [self]

        self.da = da
        self.row = [len(ancestors)] + [0] * len(ancestors)
        self.row_db_list = [-1] * (len(ancestors) + 2)
        self.col = [len(ancestors)] + [0] * len(ancestors)
        self.empty_expanded_row = 0
        self.empty_expanded_col = 0

    def dump(self, filename):
        with open(filename, "wb") as fp:
            pickle.dump(self, fp)

    @classmethod
    def load(cls, filename):
        with open(filename, "rb") as fp:
            return pickle.load(fp)

    def set(self, new_col_letter):
        self.col_letter = new_col_letter

        # shortcut
        parent = self.ancestors[-1]
        self.empty_expanded_col = parent.empty_expanded_col + (1 if not new_col_letter else 0)
        ancestors_with_self = self.ancestors_with_self
        row_db_list = self.row_db_list
        row = self.row
        col = self.col
        depth = self.depth

        if new_col_letter:
            for row_index, node in zip(range(1, depth + 1 - self.empty_expanded_row), ancestors_with_self):
                r1 = node.da.get(new_col_letter, -1)
                c1 = parent.row_db_list[row_index]
                if new_col_letter == node.row_letter:
                    cost = 0
                    # 上書きしてもしなくても結果変わらないっぽい
                    row_db_list[row_index] = row_index
                else:
                    cost = 1
                    if new_col_letter.lower() == node.row_letter.lower():
                        cost = 0
                    # 上書きしてもしなくても結果変わらないっぽい
                    row_db_list[row_index] = parent.row_db_list[row_index]

                if r1 < 0 or c1 < 0:
                    transposition_cost = 99
                else:
                    transposition_cost = self.get_score(r1 - 1 , c1 - 1) + (row_index - r1 - 1) + 1 + (depth - c1 - 1)

                row[row_index] = min(parent.row[row_index-1] + cost,                       # 左上
                                  parent.row[row_index] + 1 if row_index < depth else 999, # 左
                                  row[row_index-1] + 1,                                    # 上
                                  transposition_cost)

        if self.row_letter:
            db = -1
            da = self.da
            for col_index, node in zip(range(1, depth + 1 - self.empty_expanded_col), ancestors_with_self):
                col_letter = node.col_letter
                r1 = da.get(col_letter, -1)
                c1 = db
                if col_letter == self.row_letter:
                    cost = 0
                    db = col_index
                    row_db_list[depth] = col_index
                else:
                    cost = 1
                    if col_letter.lower() == self.row_letter.lower():
                        cost = 0

                if r1 < 0 or c1 < 0:
                    transposition_cost = 99
                else:
                    transposition_cost = self.get_score(r1 - 1, c1 - 1) + (depth - r1 - 1) + 1 + (col_index - c1 - 1)

                col[col_index] = min(parent.col[col_index-1] + cost,                                  # 左上
                                  (parent.col[col_index] if col_index < depth else self.row[-2]) + 1, # 上
                                  col[col_index-1] + 1,                                               # 左
                                  transposition_cost)
            row[-1] = col[-1]
        return col[-1]

    def get_score(self, row, col):
        if row > col:
            return self.ancestors[row].col[col]
        else:
            return self.ancestors[col].row[row]

    @property
    def depth(self):
        return len(self.ancestors)

    @property
    def score(self):
        empty_row = self.empty_expanded_row
        empty_col = self.empty_expanded_col
        if empty_row > 0 and empty_col > 0:
            empty = min(empty_row, empty_col)
            return self.ancestors[-empty].score
        elif self.empty_expanded_row > 0:
            return self.row[-1-self.empty_expanded_row]
        else:
            return self.col[-1-self.empty_expanded_col]

    @property
    def max_depth(self):
        def _search(node, depth):
            max_depth = depth
            for n in node.values():
                d = _search(n, depth + 1)
                if d > max_depth:
                    max_depth = d
            return max_depth
        return _search(self, 0)

    @property
    def min_score(self):
        if self.empty_expanded_row > 0:
            return min(self.row[:-self.empty_expanded_row])
        else:
            return min(self.col)

    def expand_empty_nodes(self, expand_depth, min_depth=1):
        def _expand(node, times):
            for i in range(times):
                added_node = node.insert_letter("")
                added_node.word = node.word
                added_node.empty_expanded_row = node.empty_expanded_row + 1
                node = added_node

        def _search(node):
            if min_depth <= node.depth:
                _expand(node, expand_depth)
            for child in node.values():
                if child.row_letter:
                    _search(child)
        _search(self)

    def insert_letter(self, letter):
        node = self
        if letter not in node:
            node[letter] = DamerauTrieNode(letter,
                    node.ancestors + [node],
                    dict(list(node.da.items()) + [(node.row_letter, node.depth)]))
        return node[letter]

    def insert(self, word):
        node = self
        for letter in word:
            node = node.insert_letter(letter)
        node.word = word
        return node

    def print(self, indent=2, eol="\n"):
        def _format(result, node, last_indent):
            for key, child in node.items():
                result.append("{}'{}': {}".format(
                    " " * last_indent,
                    key,
                    (child.row_letter, child.word, len(child.ancestors), "e.row: ", child.empty_expanded_row, "e.col: ", child.empty_expanded_col, "score: ", child.score)))
                    #(child.row_letter, child.word, len(child.ancestors), child.da, child.row)))
                _format(result, child, last_indent + indent)
            return result
        print(eol.join(_format([], self, 0)))

    def get_word_nodes(self, words=[]):
        def _search(node, result):
            if node.word and (words and node.word in words):
                result.append(node)
            for key, child in node.items():
                _search(child, result)
            return result
        return _search(self, [])

    def print_score(self):
        from pprint import pprint
        result = []
        get_score = self.get_score
        for row in range(self.depth):
            result.append([get_score(row, col) for col in range(self.depth)] + [self.row[row]])
        result.append(self.col)
        print("score: ")
        for line in result:
            print(line)
        print("word: ", self.word)
        print("score: ", self.score)
        print("da: ", self.da)
        print("db: ", self.row_db_list)
        print("empty_row: ", self.empty_expanded_row)
        print("empty_col: ", self.empty_expanded_col)
        print()

    def count_nodes(self, max_depth=999):
        def _count(node, current_depth):
            total = len(node)
            if current_depth < max_depth:
                for key in node:
                    total += _count(node[key], current_depth + 1)
            return total
        return _count(self, 1)

    def count_words(self, max_depth=999):
        def _count(node, current_depth):
            total = 0
            if node.word:
                total += 1
            if current_depth < max_depth:
                for key in node:
                    total += _count(node[key], current_depth + 1)
            return total
        return _count(self, 1)


    def search(self, input_str, max_distance, expand=0, initial_nodes=None):
        def _search(nodes, letter, result):
            next_nodes = []
            for child in nodes:
                child.set(letter)
                if child.min_score < max_distance:
                    next_nodes.extend(child.values())
                    if child.word:
                        result.append((child.word, child.score))
            return next_nodes

        if initial_nodes:
            nodes = initial_nodes
        else:
            nodes = self.values()

        result = []
        for input_letter in input_str:
            nodes = _search(nodes, input_letter, result)
        last_letter_nodes = nodes
        for i in range(expand):
            nodes = _search(nodes, "", result)
        result.sort(key=itemgetter(1), reverse=False)
        return result, last_letter_nodes
