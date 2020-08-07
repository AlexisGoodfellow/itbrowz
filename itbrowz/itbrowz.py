import shutil
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup  # type: ignore
from termcolor import colored

from itbrowz.renderers import element_renderer
from itbrowz.utils import (
    deep_flatten,
    eprint,
    subscript_translate,
    superscript_translate,
)

LINK_LIST: List[str] = ["FILLER"]


def print_long_links():
    for i in range(1, len(LINK_LIST)):
        print(
            colored(f"{i}: ", "red", attrs=[])
            + colored(f"{LINK_LIST[i]}", "blue", attrs=["underline"])
        )


@dataclass
class TerminalRenderData:
    base_url: str
    color: str
    attrs: List[str]
    div_depth: int
    list_depth: int
    span_depth: int
    link_text: str
    superscript: bool
    subscript: bool
    base_terminal_width: int

    def __init__(self, base_url):
        self.base_url = base_url
        self.root_url = "https://" + base_url.split("/")[2]
        self.color = "green"
        self.attrs = []
        self.div_depth = 0
        self.list_depth = 0
        self.span_depth = 0
        self.link_text = ""
        self.superscript = False
        self.subscript = False
        self.base_terminal_width = shutil.get_terminal_size()[0]

    def consumed_width(self):
        consumed_columns = (self.div_depth) * 2
        if self.list_depth != 0:
            return consumed_columns + (self.list_depth * 4) + 3
        return consumed_columns

    def available_terminal_width(self):
        return self.base_terminal_width - self.consumed_width()

    def clean_strings(self, base_string):
        cut_strings = base_string.split("\n")
        cleaned_strings = []
        for string in cut_strings:
            formatted_strings = [
                str(string)[i : i + self.available_terminal_width()]
                for i in range(0, len(string), self.available_terminal_width())
            ]
            for s in formatted_strings:
                cleaned_strings.append(" ".join(s.split("\t")))
        return cleaned_strings

    def suffix(self, s):
        padding_amount = (
            self.available_terminal_width() - len(s) - (self.span_depth * 2)
        )
        if self.link_text != "":
            link_number = 0
            for i in range(1, len(LINK_LIST)):
                if LINK_LIST[i] == self.link_text:
                    link_number = i
            padding_amount -= len(str(link_number)) + 2
        pad_str = " " * padding_amount

        div_bars = self.div_depth
        if padding_amount <= 0:
            div_bars += padding_amount

        suffix = colored("}" * self.span_depth, "cyan", attrs=[])
        suffix += colored(pad_str, self.color, attrs=[])
        return suffix + colored("|" * div_bars, "white", attrs=[])

    def prefix(self):
        prefix = colored("|" * self.div_depth, "white", attrs=[])
        if self.list_depth != 0:
            prefix += colored(("    " * self.list_depth) + "-- ", "magenta", attrs=[])
        if self.span_depth != 0:
            prefix += colored("{" * self.span_depth, "cyan", attrs=[])

        return prefix

    def core(self, s):
        if self.subscript:
            s = superscript_translate(s)
        if self.subscript:
            s = subscript_translate(s)
        base = colored(s, self.color, attrs=self.attrs)
        if self.link_text != "":
            link_number = 0
            for i in range(1, len(LINK_LIST)):
                if LINK_LIST[i] == self.link_text:
                    link_number = i
                    break
            if link_number == 0:
                LINK_LIST.append(self.link_text)
                link_number = len(LINK_LIST) - 1
            base += colored(f"[{link_number}]", "blue", attrs=["reverse"])
        return base

    def render_root_text(self, base_string):
        elems = []
        for s in self.clean_strings(base_string):
            elems.append(self.prefix())
            elems.append(self.core(s))
            elems.append(self.suffix(s))
        return elems


def oops_i_wrote_a_browser(root_element, base_url):
    render_html(root_element.contents, base_url)


def spell_lookup(args):
    base_url = "https://5thsrd.org/spellcasting/spells/"
    res = requests.get(f"{base_url}{args.spell}")
    text = BeautifulSoup(res.content, "html.parser")
    root = text.body.find("div", class_="container", recursive=False)
    oops_i_wrote_a_browser(root, base_url)


def class_lookup(args):
    base_url = "https://5thsrd.org/character/classes/"
    res = requests.get(f"{base_url}{args._class}")
    text = BeautifulSoup(res.content, "html.parser")
    root = text.body.find("div", class_="container", recursive=False)
    oops_i_wrote_a_browser(root, base_url)


def race_lookup(args):
    base_url = "https://5thsrd.org/character/races/"
    res = requests.get(f"{base_url}{args.race}")
    text = BeautifulSoup(res.content, "html.parser")
    root = text.body.find("div", class_="container", recursive=False)
    oops_i_wrote_a_browser(root, base_url)


def arbitrary_url_lookup(args):
    base_url = "/".join(args.url.split("/")[0:-1])
    res = requests.get(args.url)
    text = BeautifulSoup(res.content, "html.parser")
    if args.div:
        root = text.body.find("div", class_=args.div, recursive=False)
        if root is None:
            root = text.body.find("div", id=args.div, recursive=False)
    else:
        root = text.body
    oops_i_wrote_a_browser(root, base_url)


def render_html(elements, base_url):
    # Collect child elements together into a list
    render_info = TerminalRenderData(base_url)
    for x in elements:
        all_child_elements = deep_flatten(element_renderer(x, render_info))
        for y in all_child_elements:
            eprint(y)
        eprint("\n")
    print_long_links()
