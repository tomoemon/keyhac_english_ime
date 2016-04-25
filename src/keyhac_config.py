# -*- coding: utf-8 -*-
from keyhac import *
from .english_ime import load_ime


settings = {
        "list_font_size": 20,
        "list_candidates_num": 8,
        "list_width": 25,
        "is_append_space": True,
}


sign_name_key_dict = {
    "S-A": "A",
    "S-B": "B",
    "S-C": "C",
    "S-D": "D",
    "S-E": "E",
    "S-F": "F",
    "S-G": "G",
    "S-H": "H",
    "S-I": "I",
    "S-J": "J",
    "S-K": "K",
    "S-L": "L",
    "S-M": "M",
    "S-N": "N",
    "S-O": "O",
    "S-P": "P",
    "S-Q": "Q",
    "S-R": "R",
    "S-S": "S",
    "S-T": "T",
    "S-U": "U",
    "S-V": "V",
    "S-W": "W",
    "S-X": "X",
    "S-Y": "Y",
    "S-Z": "Z",
    "A": "a",
    "B": "b",
    "C": "c",
    "D": "d",
    "E": "e",
    "F": "f",
    "G": "g",
    "H": "h",
    "I": "i",
    "J": "j",
    "K": "k",
    "L": "l",
    "M": "m",
    "N": "n",
    "O": "o",
    "P": "p",
    "Q": "q",
    "R": "r",
    "S": "s",
    "T": "t",
    "U": "u",
    "V": "v",
    "W": "w",
    "X": "x",
    "Y": "y",
    "Z": "z",
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    #"Plus": "+",
    #"BackQuote": "`",
    #"BackSlash": "BackSlash",
    #"Quote": "'",
    #"DoubleQuote": "\"",
    #"Asterisk": "*",
    #"Atmark": "@",
    #"Caret": "^",
    "Space": "Space",
    "Back": "Back",
    "Enter": "Enter",
    "Esc": "Esc",
    # シフト押下時の対応
    "S-1": "!",
    "S-2": "\"",
    "S-3": "#",
    "S-4": "$",
    "S-5": "%",
    "S-6": "&",
    "S-7": "'",
    "S-8": "(",
    "S-9": ")",
    "Minus": "-",
    "S-Minus": "=",
    "Tilde": "^",
    "S-Tilde": "~",
    "Yen": "\\",
    "S-Yen": "|",
    "BackQuote": "@",
    "S-BackQuote": "`",
    "OpenBracket": "[",
    "S-OpenBracket": "{",
    "Semicolon": ";",
    "S-Semicolon": "+",
    "Colon": ":",
    "S-Colon": "*",
    "CloseBracket": "]",
    "S-CloseBracket": "}",
    "Comma": ",",
    "S-Comma": "<",
    "Period": ".",
    "S-Period": ">",
    "Slash": "/",
    "S-Slash": "?",
    "Underscore": "\\",
    "S-Underscore": "_",
}
key_sign_name_dict = {item: key for key, item in sign_name_key_dict.items()}


def setup_list_window(window):
    window.setFont("", settings["list_font_size"])
    window.skin_statusbar.show(False)
    #window.setTitle("hoge")
    #def mywidth(self):
    #    return self._TextWindow__size_in_char[0]
    #config_util.bind_method(window, "width", mywidth)


def setup(keymap):
    ime = None

    def update_list():
        if keymap.list_window:
            candidates_num = settings["list_candidates_num"]
            candidates = ime.candidates
            input_string = "".join(ime.inputs)
            new_list = ([input_string]
                        + [""]
                        + ["{} - {:.1f}".format(word, dist) for word, dist in candidates]
                        + [""] * (candidates_num - len(candidates)))
            keymap.list_window.setItems(new_list)
            keymap.list_window.select = 2
            keymap.list_window.paint()

    def next_select():
        if ime and ime.candidates and keymap.list_window:
            keymap.list_window.select = min(
                    keymap.list_window.select + 1,
                    max(len(ime.candidates) + 1, 2))
            keymap.list_window.paint()
        else:
            input_key(["Tab"])

    def back_select():
        if ime and ime.candidates and keymap.list_window:
            keymap.list_window.select = max(keymap.list_window.select - 1, 2)
            keymap.list_window.paint()
        else:
            input_key(["S-Tab"])

    def hook_input(key):
        if not ime:
            input_key([key])
            return
        ime.input(key, max_distance=2, expand=2)
        update_list()

    def input_candidate(inputs, candidates, end):
        if not inputs:
            input_key(end)
        elif candidates:
            word, level = candidates[keymap.list_window.select - 2 if keymap.list_window else 0]
            input_key(list(word) + (end if settings["is_append_space"] else []))
        else:
            input_key(list(ime.inputs) + (end if settings["is_append_space"] else []))

    def hook_space():
        if not ime:
            input_key(["Space"])
            return
        input_candidate(ime.inputs, ime.candidates, ["Space"])
        ime.reset()
        update_list()

    def hook_enter():
        if not ime:
            input_key(["Enter"])
            return
        input_candidate(ime.inputs, ime.candidates, ["Enter"])
        ime.reset()
        update_list()

    def hook_backspace():
        if not ime:
            input_key(["Back"])
            return
        if not ime.inputs:
            input_key(["Back"])
        else:
            ime.back()
        update_list()

    def hook_escape():
        if not ime:
            input_key(["Esc"])
            return
        if not ime.inputs:
            input_key(["Esc"])
        ime.reset()
        update_list()

    def input_key(input_list):
        result = []
        for char in input_list:
            result.append(key_sign_name_dict[char])
        keymap.InputKeyCommand(*result)()

    def command_PopApplicationList():

        if keymap.isListWindowOpened():
            keymap.cancelListWindow()
            return

        def popApplicationList():

            applications = [(" " * settings["list_width"], None)
                    for i in range(settings["list_candidates_num"] + 2)]

            listers = [
                ("List", cblister_FixedPhrase(applications)),
            ]
            item, mod = keymap.popListWindow(listers)
            update_list()

        keymap.delayedCall(popApplicationList, 0)

    def command_Initialize():

        def jobTest(item):
            nonlocal ime

            print("Loading dictionary...")
            ime = load_ime(max_candidates=settings["list_candidates_num"])

        def jobTestFinished(item):
            print("Done.")
            command_PopApplicationList()

        job_item = JobItem(jobTest, jobTestFinished)
        JobQueue.defaultQueue().enqueue(job_item)

    command_Initialize()

    keymap_global = keymap.defineWindowKeymap()

    for key_name_on_keyhac, char in sign_name_key_dict.items():
        keymap_global[key_name_on_keyhac] = lambda c=char: hook_input(c)

    # special keys
    keymap_global["Space"] = lambda x=0: hook_space()
    keymap_global["Back"] = lambda x=0: hook_backspace()
    keymap_global["Enter"] = lambda x=0: hook_enter()
    keymap_global["Esc"] = lambda x=0: hook_escape()
    keymap_global["Tab"] = lambda x=0: next_select()
    keymap_global["S-Tab"] = lambda x=0: back_select()

    keymap_global["C-Space"] = command_PopApplicationList

