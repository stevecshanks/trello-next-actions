import argparse
import os
import sys
from nextactions.config import Config
from nextactions.trello import Trello
from nextactions.synctool import SyncTool


def main(args):
    options = parseArgs(args)
    config = getConfig(options)
    try:
        handleAction(options.action, config)
    except Exception as e:
        sys.stderr.write("Error: " + str(e) + "\n")
        return 1
    return 0


def parseArgs(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="action to perform (sync/reset)")
    parser.add_argument("--config", help="config file to use")
    return parser.parse_args(args)


def getConfig(options):
    config = Config()
    config.loadFromFile(getConfigFileName(options))
    return config


def getConfigFileName(options):
    if (options.config):
        return options.config
    else:
        return os.path.join(os.path.expanduser('~'), '.trellonextactions.json')


def handleAction(name, config):
    trello = Trello(config)
    sync_tool = SyncTool(config, trello)
    if name == 'sync':
        created, archived = sync_tool.sync()
        print_card_list("Created", created)
        print_card_list("Archived", archived)
    elif name == 'reset':
        archived = sync_tool.reset()
        print_card_list("Archived", archived)
    else:
        raise ValueError("'" + name + "' is not a valid action")


def print_card_list(name, card_list):
    if not len(card_list):
        return
    print(name + ":")
    print()
    for c in card_list:
        print(" - " + c.name + " (" + c.id + ")")
    print()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
