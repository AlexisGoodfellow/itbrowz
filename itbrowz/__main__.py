#!/usr/bin/env python3
import argparse

from itbrowz.itbrowz import (
    arbitrary_url_lookup,
    class_lookup,
    race_lookup,
    spell_lookup,
)


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


if __name__ == "__main__":
    exit(main())
