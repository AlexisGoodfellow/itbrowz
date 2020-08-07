import shutil
import subprocess
import tempfile
from copy import deepcopy

import requests
from termcolor import colored

from .utils import eprint, get_elem_link_attr


def render_superscript(superscript, render_info):
    r = deepcopy(render_info)
    r.superscript = True
    return [element_renderer(x, r) for x in superscript.contents]


def render_subscript(subscript, render_info):
    r = deepcopy(render_info)
    r.subscript = True
    return [element_renderer(x, r) for x in subscript.contents]


def render_link(link, render_info):
    href = get_elem_link_attr(link, render_info, "href")
    r = deepcopy(render_info)
    r.link_text = f"[{href}]"
    return [element_renderer(x, r) for x in link.contents]


# This will throw off alignments - thinking about a fix
def render_span(span, render_info):
    r = deepcopy(render_info)
    r.span_depth += 1
    return [element_renderer(x, r) for x in span.contents if str(x) != "\n"]


def render_list(list_, render_info):
    r = deepcopy(render_info)
    r.color = "magenta"
    r.list_depth += 1
    return [element_renderer(x, r) for x in list_.contents]


def render_horizontal_line(render_info):
    return [
        colored(
            "|" * render_info.div_depth
            + ("    " * render_info.list_depth)
            + ("-" * render_info.available_terminal_width())
            + "|" * render_info.div_depth,
            "cyan",
            attrs=[],
        )
    ]


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
    if div.name == "header" or div.name == "footer" or div.name == "main":
        div_title = div.name + " " + div_title
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


# TABLES AND IMAGES ARE HARD AS NAILS TO FORMAT RIGHT - THESE ARE HACKS
def render_image(image, render_info):
    image_source_url = get_elem_link_attr(image, render_info, "src")
    with tempfile.NamedTemporaryFile() as f:
        r = requests.get(image_source_url, stream=True)
        f.write(r.content)
        subprocess.call(["imgcat", f.name])


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
        or elem.name == "main"
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
    elif elem.name == "code":
        r = deepcopy(render_info)
        r.color = "grey"
        return [element_renderer(x, r) for x in elem.contents]
    elif elem.name == "p" or elem.name == "button" or elem.name == "noscript":
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
    elif elem.name == "script":
        render_script(elem)
    elif (
        elem.name == "ins"
        or elem.name == "br"
        or elem.name == "wbr"
        or elem.name == "style"
        or elem.name == "input"
        or elem.name == "form"
    ):
        return []  # Will be flattened out
    else:
        raise NotImplementedError(f"{elem.name} not implemented yet")
