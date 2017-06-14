# trello-next-actions

[![Build Status](https://travis-ci.org/stevecshanks/trello-next-actions.svg?branch=master)](https://travis-ci.org/stevecshanks/trello-next-actions)
[![Coverage Status](https://coveralls.io/repos/github/stevecshanks/trello-next-actions/badge.svg?branch=master)](https://coveralls.io/github/stevecshanks/trello-next-actions?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/436446417d784d229f8bd76e8c9188c8)](https://www.codacy.com/app/stevecshanks/trello-next-actions?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=stevecshanks/trello-next-actions&amp;utm_campaign=Badge_Grade)

## Introduction

If you've read David Allen's "Getting Things Done", then hopefully the idea of a
"Next Actions" list is familiar to you.  If not, the idea is that you have a
list of projects, each of which has a "next action", which is the very next
thing you could do to move that project forward.  Your "Next Actions" list gives
you a summary of all of those actions, so you can pick the most appropriate
action to do right now.

Trello is great for building boards for projects, but it's not great at giving
you that summary level.  This script was intended to fix that, and is something
I use pretty-much every day.  It was never intended to support anyone else's
workflow, but here it is anyway...

## Usage

If you want to use my workflow, there are unfortunately a few hoops you'll need
to jump through:

1. You'll need a GTD board with at least two lists - "Next Actions" and "Projects"
1. Each card in "Projects" should have the URL of the project board as its description
1. Each project board should have a "Todo" list
1. You'll need to know the ID of this list, which you can get from the board URL e.g. https://trello.com/b/1234abcd/my-board has the ID 1234abcd
1. You'll need to get your Trello application key from here: https://trello.com/app-key
1. You'll need to authorize the Trello Next Actions app by adding your application key to this URL: https://trello.com/1/connect?key=YourApplicationKeyGoesHere&name=TrelloNextActions&expiration=never&response_type=token&scope=read,write

Once you've got all that set up, you'll need to create a config file.  The default
is `~/.trellonextactions.json`, but put it somewhere else if you like (you can specify its location when running using `--config=...`).

The file
should look like this:

```
{
    "gtd_board_id": "1234abcd",
    "application_key": "1a2a3a4a4...",
    "auth_token": "2b2b2b2b2b4b5b5..."
}
```

That's it!  To sync, you just need to run:

```
python3 -m nextactions.cmdline sync
```

and if you want to start over, just run:

```
python3 -m nextactions.cmdline reset
```

If you want to run the tests, you can run:

```
python3 -m unittest
```

or you can take a look at [green](https://github.com/CleanCut/green), which has
replaced the built-in test runner for me.
