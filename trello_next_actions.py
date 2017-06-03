#!/usr/bin/env python3
import sys
import getopt
import os
from nextactions.board import Board
from nextactions.config import Config
from nextactions.trello import Trello
from nextactions.synctool import SyncTool


def main():
    config_file = os.path.join(
        os.path.expanduser('~'), '.trellonextactions.json'
    )
    action = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["config="])
        for opt, arg in opts:
            if opt == '--config':
                config_file = arg
    except getopt.GetoptError as e:
        print_error_and_exit(str(e))

    if len(args) > 1:
        print_error_and_exit("Too many arguments supplied")
    elif len(args) == 1:
        action = args[0]

    try:
        config = load_config(config_file)
    except Exception:
        print_error_and_exit("Failed to load config '" + config_file + "'")

    trello = Trello(config)
    sync_tool = SyncTool(config, trello)

    if action == 'sync':
        created, archived = sync_tool.sync()
        print_list("Created", created)
        print_list("Archived", archived)
    elif action == 'reset':
        archived = sync_tool.reset()
        print_list("Archived", archived)
    else:
        print_error_and_exit("Unrecognised action '" + action + "'")


def print_error_and_exit(message):
    sys.stderr.write(message + "\n")
    sys.exit(1)


def load_config(config_file):
    config = Config()
    config.loadFromFile(config_file)

    return config


def print_list(name, card_list):
    print(name + ":")
    print()
    for c in card_list:
        print(" [ ] " + c.name + " (" + c.id + ")")
    print()


if __name__ == '__main__':
    sys.exit(main())
