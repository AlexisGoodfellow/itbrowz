#!/usr/bin/env python3

import argparse
import base64
import os

ESCAPE = "\x1b"
RIGHT_BRACKET = "\x5D"
BACKSLASH = "\x5C"
BELL = "\a"


def shell_printf(arg):
    print(arg, end="")


# tmux requires unrecognized OSC sequences to be wrapped with DCS tmux;
# <sequence> ST, and for all ESCs in <sequence> to be replaced with ESC ESC. It
# only accepts ESC backslash for ST. We use TERM instead of TMUX because TERM
# gets passed through ssh.
def operating_system_code():
    term = os.getenv("TERM")
    base_string = ESCAPE + RIGHT_BRACKET
    if "screen" in term:
        return ESCAPE + "Ptmux;" + ESCAPE + base_string
    return base_string


# More of the tmux workaround described above.
def string_terminator():
    term = os.getenv("TERM")
    base_string = BELL
    if "screen" in term:
        return base_string + ESCAPE + BACKSLASH
    return base_string


def print_image_in_iterm(filename):
    fn = os.path.abspath(filename)
    with open(fn, "rb") as f:
        file_contents = f.read()
    size = os.path.getsize(fn)
    encoded_filename = base64.b64encode(fn.encode(encoding="utf-8")).decode("utf-8")
    shell_printf(operating_system_code())
    shell_printf("1337;File=")
    shell_printf(f"name={encoded_filename};size={size};inline=1:")
    shell_printf(base64.b64encode(file_contents).decode("utf-8"))
    shell_printf(string_terminator())
    print("")


def main():
    parser = argparse.ArgumentParser(description="Image printer for iterm")
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        dest="url",
        default="",
        help="URL where image is sourced from the internet",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        dest="filename",
        default="",
        help="File to print to terminal",
    )
    args = parser.parse_args()
    if args.filename:
        try:
            print_image_in_iterm(args.filename)
        except IOError:
            print(f"File {args.filename} could not be opened!")


if __name__ == "__main__":
    main()
