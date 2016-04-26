# -*- coding: utf-8 -*-
import os
from os import path
import codecs
from .damerau_trie import DamerauTrieNode


class Word(str):
    def set_level(self, value):
        self.level = value
        return self


class EnglishIme:
    def __init__(self, dict_file, max_candidates=999):
        word_definitions = self.load_dictionary(dict_file)
        node = DamerauTrieNode()
        for word, level in word_definitions:
            node.insert(Word(word).set_level(int(level)))
        self.damerau_trie_node = node
        self.max_candidates = max_candidates
        self.reset()

    def load_dictionary(self, dict_file):
        dictionary_file = path.join(path.dirname(__file__), dict_file)
        with codecs.open(dictionary_file, "rb", encoding="utf-8") as fp:
            data = [line.strip().split("\t") for line in fp.readlines()]
        return data

    @property
    def candidates(self):
        return self._current_candidates

    @property
    def _current_candidates(self):
        if not self.candidates_history:
            return []

        # find big letter in inputs
        big_letter_index = -1
        for index, char in enumerate(self.inputs):
            if not self.is_mark(char):
                if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    big_letter_index = index
                break

        # insert mark signs into candidates
        result = []
        for word, dist in self.candidates_history[-1]:
            word_as_list = list(word)
            if big_letter_index > 0:
                word_as_list[0] = word_as_list[0].upper()
            for i, l in self.mark_inputs:
                word_as_list.insert(i, l)
            result.append(("".join(word_as_list), dist))
        return result

    @property
    def _last_nodes(self):
        if self.nodes_history:
            return self.nodes_history[-1]
        return []

    def back(self):
        if self.inputs:
            self.candidates_history.pop()
            self.nodes_history.pop()
            self.inputs = self.inputs[:-1]
            self.mark_inputs = [(index, letter) for index, letter in self.mark_inputs if index < len(self.inputs)]
        return self._current_candidates, self._last_nodes

    def is_mark(self, letter):
        return letter in "!\"#$%&'()-=^\\@`[{;+:*]},<.>/?_"

    def reset(self):
        self.candidates_history = []
        self.nodes_history = []
        self.inputs = []
        self.mark_inputs = []

    def input(self, letter, max_distance, expand):
        if self.inputs and not self._last_nodes:
            # 候補がなくなって last_nodes が空になると
            # また TrieNode の先頭（1文字目）から検索を始めてしまうのを避ける
            result, nodes = [], []
        else:
            result, nodes = self.damerau_trie_node.search(letter, max_distance, expand, self._last_nodes)
        result = result[:self.max_candidates]
        self.inputs.append(letter)
        self.candidates_history.append(result)
        self.nodes_history.append(nodes)

        if self.should_input_as_mark(letter, self.candidates_history):
            index = len(self.inputs) - 1
            self.mark_inputs.append((index, letter))
            if len(self.candidates_history) >= 2:
                new_nodes = self.nodes_history[-2]
                new_candidates = self.candidates_history[-2]
            else:
                new_nodes = self.damerau_trie_node.values()
                new_candidates = [("", 0)]
            self.nodes_history[-1] = new_nodes
            self.candidates_history[-1] = new_candidates

        return self._current_candidates, self._last_nodes

    def should_input_as_mark(self, letter, history):
        """
        "hoge" のように辞書にない記号が前後に入った場合に、補完候補を消さないようにする
        判定条件は
        ・letter が記号である
        ・直前の最良候補よりもコストが1増えている
        """
        current_cost = history[-1][0][1] if len(history) >= 1 and history[-1] else 999
        last_cost = history[-2][0][1] if len(history) >= 2 and history[-2] else 0
        return self.is_mark(letter) and current_cost - last_cost> 0


def load_ime(dictionary_name, max_candidates):
    ime = EnglishIme(dictionary_name, max_candidates=max_candidates)
    ime.damerau_trie_node.expand_empty_nodes(2)
    return ime


def test():
    ime = load_ime()
    for c in "asdfdefence":
        result, nodes = ime.input(c, 2, 2)
        print(c, result[:10])


if __name__ == '__main__':
    import sys
    globals()[sys.argv[1]](*sys.argv[2:])

