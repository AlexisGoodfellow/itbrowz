from .constants import UNICODE_MAP


def eprint(arg):
    print(arg, end="")


def deep_flatten(nested_list):
    if nested_list is None:
        return []
    flattened = []
    for x in nested_list:
        if isinstance(x, list):
            for y in x:
                flattened.append(y)
        else:
            flattened.append(x)
    if any(isinstance(x, list) for x in flattened):
        return deep_flatten(flattened)
    else:
        return flattened


def superscript_translate(s):
    ret = ""
    for letter in s:
        translated = UNICODE_MAP[letter][0]
        let = letter if translated == "?" else translated
        ret.append(let)
    return ret


def subscript_translate(s):
    ret = ""
    for letter in s:
        translated = UNICODE_MAP[letter][1]
        let = letter if translated == "?" else translated
        ret.append(let)
    return ret


def get_elem_link_attr(elem, render_info, link_attr):
    try:
        attr = elem[link_attr]
    except KeyError:
        return ""
    if "http" not in attr:
        if attr.startswith("//"):
            attr = "https:" + attr
        elif attr.startswith("/.."):
            attr = render_info.base_url + attr[1:]
        elif attr.startswith(".."):
            attr = render_info.base_url + attr
        else:
            attr = render_info.root_url + attr
    return attr
