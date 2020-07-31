#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Dict
from constants import UNICODE_MAP

from bs4 import BeautifulSoup  # type: ignore
from termcolor import colored

import requests

LONG_LINK_MAP: Dict[str, str] = {}
NUM_LONG_LINKS = 1


def print_long_links():
    for k, v in LONG_LINK_MAP.items():
        print(colored(f"{k}: ", "red", attrs=[]) + colored(f"{v}", "blue", attrs=["underline"]))


def superscript_translate(s):
    ret = ""
    for letter in s:
        translated = UNICODE_MAP[letter][0]
        let = letter if translated == '?' else translated
        ret.append(let)
    return ret


def subscript_translate(s):
    ret = ""
    for letter in s:
        translated = UNICODE_MAP[letter][1]
        let = letter if translated == '?' else translated
        ret.append(let)
    return ret


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
        self.root_url = "https://" + base_url.split('/')[2]
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
        if self.list_depth == 0:
            return self.div_depth * 2
        else:
            return (self.div_depth * 2) + (self.list_depth * 4) + 3

    def avaliable_terminal_width(self):
        return self.base_terminal_width - self.consumed_width()

    def clean_strings(self, base_string):
        cut_strings = base_string.split("\n")
        cleaned_strings = []
        for string in cut_strings:
            formatted_strings = [
                str(string)[i : i + self.avaliable_terminal_width()]
                for i in range(0, len(string), self.avaliable_terminal_width())
            ]
            for s in formatted_strings:
                cleaned_strings.append(" ".join(s.split("\t")))
        return cleaned_strings

    def suffix(self, s):
        if self.link_text != "":
            if self.avaliable_terminal_width() < len(s) + len(self.link_text):
                global NUM_LONG_LINKS
                pad_str = " " * (self.avaliable_terminal_width() - len(s) - 2 - len(str(NUM_LONG_LINKS)) - (self.span_depth * 2))
                NUM_LONG_LINKS += 1
            else:
                pad_str = " " * (self.avaliable_terminal_width() - len(s) - len(self.link_text) - (self.span_depth * 2))
        else:
            pad_str = " " * (self.avaliable_terminal_width() - len(s) - (self.span_depth * 2))

        suffix = colored("}" * self.span_depth, "cyan", attrs=[])
        suffix += colored(pad_str, self.color, attrs=[])
        return suffix + colored("|" * self.div_depth, "white", attrs=[])

    def prefix(self):
        prefix = colored("|" * self.div_depth, "white", attrs=[])
        if self.list_depth != 0:
            prefix += colored(("    " * self.list_depth) + "-- ", "magenta", attrs=[])
        if self.span_depth != 0:
            prefix += colored("{" * self.span_depth, "cyan", attrs=[])

        return prefix

    def core(self, s):
        base = colored(s, self.color, attrs=self.attrs)
        if self.link_text != "":
            if self.avaliable_terminal_width() < len(s) + len(self.link_text):
                global NUM_LONG_LINKS
                LONG_LINK_MAP[NUM_LONG_LINKS] = self.link_text
                base += colored(f"[{NUM_LONG_LINKS}]", "blue", attrs=["reverse"])
            else:
                base += colored(self.link_text, "blue", attrs=["underline"])
        return base

    def render_root_text(self, base_string):
        return [
            [
                self.prefix(),
                self.core(s),
                self.suffix(s)
            ]
            for s in self.clean_strings(base_string)
        ]


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


def main():
    parser = argparse.ArgumentParser(description="DND Quick lookup")
    parser.add_argument(
        "-s", "--spell", type=str, dest="spell", default="", help="Spell"
    )
    parser.add_argument(
        "-c", "--class", type=str, dest="_class", default="", help="Class"
    )
    parser.add_argument("-r", "--race", type=str, dest="race", default="", help="Race")
    parser.add_argument(
        "-u", "--url", type=str, dest="url", default="", help="Arbitrary URL"
    )
    parser.add_argument(
        "-d", "--div", type=str, dest="div", default="", help="Div identifier"
    )
    args = parser.parse_args()
    for k, v in vars(args).items():
        vars(args)[k] = v.replace("-", "_") if k == "spell" else v
        vars(args)[k] = v.replace("_", "-") if k == "race" else v
    if args.spell:
        spell_lookup(args)
    elif args._class:
        class_lookup(args)
    elif args.race:
        race_lookup(args)
    elif args.url:
        arbitrary_url_lookup(args)
    else:
        pass


def element_renderer(elem, render_info):
    # Base case - all that's left is text
    if elem.name is None:
        return render_info.render_root_text(elem)
    # RECURSIVE CASES - THIS IS A DOOZY
    # Table is not a root element or base case, but we render it like one
    # for now because formatting tables is a royal pain in the @$$
    elif elem.name == "table":
        render_table(elem, render_info)
        return []  # THIS IS A HACK
    elif elem.name == "img":
        render_image(elem, render_info)
        return []
    elif elem.name == "ol" or elem.name == "ul" or elem.name == "nav":
        return render_list(elem, render_info)
    elif (
        elem.name == "div"
        or elem.name == "center"
        or elem.name == "header"
        or elem.name == "footer"
    ):
        return render_div(elem, render_info)
    elif elem.name == "span":
        return render_span(elem, render_info)
    elif elem.name == "sub":
        return render_subscript(elem, render_info)
    elif elem.name == "sup":
        return render_superscript(elem, render_info)
    elif elem.name == "em" or elem.name == "i":
        r = deepcopy(render_info)
        r.attrs += ["bold"]
        return [element_renderer(x, r) for x in elem.contents]
    elif elem.name == "strong" or elem.name == "b":
        r = deepcopy(render_info)
        r.attrs += ["underline"]
        return [element_renderer(x, r) for x in elem.contents]
    elif elem.name == "hr":
        return render_horizontal_line(render_info)
    elif elem.name == "p" or elem.name == "button":
        r = deepcopy(render_info)
        r.attrs = []
        return [element_renderer(x, r) for x in elem.contents]
    elif elem.name == "label":
        r = deepcopy(render_info)
        r.colr = "blue"
        r.attrs = ["underline"]
        return [element_renderer(x, r) for x in elem.contents]
    elif elem.name == "li":
        r = deepcopy(render_info)
        r.attrs = []
        r.color = "magenta"
        return [element_renderer(x, r) for x in elem.contents]
    elif elem.name == "a":
        return render_link(elem, render_info)
    elif elem.name == "blockquote":
        r = deepcopy(render_info)
        r.attrs = []
        r.color = "cyan"
        return [element_renderer(x, r) for x in elem.contents]
    elif elem.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        r = deepcopy(render_info)
        r.attrs += ["reverse"]
        r.color = "red"
        return [element_renderer(x, r) for x in elem.contents]
    elif (
        elem.name == "ins"
        or elem.name == "br"
        or elem.name == "wbr"
        or elem.name == "script"
        or elem.name == "style"
        or elem.name == "input"
        or elem.name == "form"
    ):
        return []  # Will be flattened out
    else:
        raise NotImplementedError(f"{elem.name} not implemented yet")


def render_superscript(superscript, render_info):
    r = deepcopy(render_info)
    r.is_superscript = True
    return [element_renderer(x, r) for x in superscript.contents]


def render_subscript(subscript, render_info):
    r = deepcopy(render_info)
    r.is_subscript = True
    return [element_renderer(x, r) for x in subscript.contents]

def flatten(l):
    flattened = [item for sublist in l for item in sublist]
    if any([isinstance(x, list) for x in flattened]):
        return flatten(flattened)
    else:
        return flattened


def render_html(elements, base_url):
    # Collect child elements together into a list
    render_info = TerminalRenderData(base_url)
    for x in elements:
        all_child_elements = flatten(element_renderer(x, render_info))
        for y in all_child_elements:
            eprint(y)
        eprint("\n")
    print_long_links()


def render_list(list_, render_info):
    r = deepcopy(render_info)
    r.color = "magenta"
    r.list_depth += 1
    return [element_renderer(x, r) for x in list_.contents]


def get_elem_link_attr(elem, render_info, link_attr):
    try:
        attr = elem[link_attr]
    except KeyError:
        return ""
    if "http" not in attr:
        if attr.startswith("//"):
            attr = "https:" + attr
        elif attr.startswith("/"):
            attr = render_info.root_url + attr
        else:
            attr = render_info.base_url + attr
    return attr


# TABLES AND IMAGES ARE HARD AS NAILS TO FORMAT RIGHT - THESE ARE HACKS
def render_image(image, render_info):
    image_source_url = get_elem_link_attr(image, render_info, "src")
    with tempfile.NamedTemporaryFile() as f:
        r = requests.get(image_source_url, stream=True)
        f.write(r.content)
        subprocess.call(["imgcat", f.name])


def render_horizontal_line(render_info):
    return [
        colored(
            "|" * render_info.div_depth
            + ("    " * render_info.list_depth)
            + ("-" * render_info.avaliable_terminal_width())
            + "|" * render_info.div_depth,
            "cyan",
            attrs=[],
        )
    ]
    pass


def render_link(link, render_info):
    href = get_elem_link_attr(link, render_info, "href")
    r = deepcopy(render_info)
    r.link_text = f"[{href}]"
    return [element_renderer(x, r) for x in link.contents]


def render_div(div, render_info):
    border_color = "white"
    r = deepcopy(render_info)
    r.div_depth += 1
    div_attr_keys = [k for k in div.attrs.keys()]
    if "id" in div_attr_keys:
        div_title = div["id"]
    elif "class" in div_attr_keys:
        div_title = " ".join(div["class"])
    else:
        div_title = ""
    return [
        [
            colored("|" * render_info.div_depth, border_color, attrs=[]),
            colored("/", border_color, attrs=[]),
            colored(
                div_title
                + (
                    "-"
                    * (
                        shutil.get_terminal_size().columns
                        - (2 * r.div_depth)
                        - len(div_title)
                    )
                ),
                border_color,
                attrs=[],
            ),
            colored("\\", border_color, attrs=[]),
            colored("|" * render_info.div_depth, border_color, attrs=[]),
        ],
        [element_renderer(x, r) for x in div.contents if str(x) != "\n"],
        [
            colored("|" * render_info.div_depth, border_color, attrs=[]),
            colored("\\", border_color, attrs=[]),
            colored(
                "~"
                + div_title
                + (
                    "-"
                    * (
                        shutil.get_terminal_size().columns
                        - (2 * r.div_depth)
                        - len(div_title)
                        - 1
                    )
                ),
                border_color,
                attrs=[],
            ),
            colored("/", border_color, attrs=[]),
            colored("|" * render_info.div_depth, border_color, attrs=[]),
        ],
    ]


# This will throw off alignments - thinking about a fix
def render_span(span, render_info):
    r = deepcopy(render_info)
    r.span_depth += 1
    return [element_renderer(x, r) for x in span.contents if str(x) != "\n"]


# HACK HACK HACK
def render_table(table, render_info):
    head = table.find("thead")
    head_rows = head.find("tr")
    row_head_data = [x.get_text() for x in head_rows.find_all("th")]
    body = table.find("tbody")
    body_rows = body.find_all("tr")
    body_data = [[x.get_text() for x in row.find_all("td")] for row in body_rows]
    render_table_helper(row_head_data, body_data, render_info)


def render_table_helper(row_head_data, body_data, render_info):
    row_head_lengths = [len(x) for x in row_head_data]
    max_lengths = []
    for row_elems in range(0, len(body_data[0])):
        max_lengths.append(
            max([len(body_data[rows][row_elems]) for rows in range(0, len(body_data))])
        )
    maximum_lengths = []
    for i in range(0, len(row_head_lengths)):
        max_length = (
            max_lengths[i]
            if max_lengths[i] > row_head_lengths[i]
            else row_head_lengths[i]
        )
        maximum_lengths.append(max_length)
    print_table_format_line(maximum_lengths, render_info)
    print_table_data_line(maximum_lengths, row_head_data, render_info)
    print_table_format_line(maximum_lengths, render_info)
    for row in body_data:
        print_table_data_line(maximum_lengths, row, render_info)
    print_table_format_line(maximum_lengths, render_info)


def print_table_format_line(maximum_lengths, render_info):
    eprint(colored("+", "yellow"))
    for length in maximum_lengths:
        eprint(colored("-", "yellow"))
        for x in range(0, length):
            eprint(colored("-", "yellow"))
        eprint(colored("-+", "yellow"))
    eprint(colored("\n", "yellow"))


def print_table_data_line(maximum_lengths, row_head_data, render_info):
    eprint(colored("|", "yellow"))
    for i in range(0, len(row_head_data)):
        eprint(colored(" ", "yellow"))
        padding_amount = maximum_lengths[i] - len(row_head_data[i])
        padding = ""
        for j in range(0, padding_amount):
            padding += " "
        eprint(colored(row_head_data[i] + padding, "yellow"))
        eprint(colored(" |", "yellow"))
    eprint(colored("\n", "yellow"))


def eprint(arg):
    print(arg, end="")


if __name__ == "__main__":
    main()

