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
    if name == 'sync':
        pass
    elif name == 'reset':
        pass
    else:
        raise ValueError("'" + name + "' is not a valid action")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
