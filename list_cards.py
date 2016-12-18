import requests
import json
from urlparse import urlparse
import ConfigParser
import sys, getopt

# Read in any command-line config
config_name = 'default'

# TODO: Handle errors
opts, args = getopt.getopt(sys.argv[1:], None ,["config="])
for opt, arg in opts:
    if opt == '--config':
        config_name = arg

# Pull config from user's home directory
# TODO: Had to do this in current directory, not sure this has access to ~ by default
# TODO: Make this cross-platform

config = ConfigParser.ConfigParser()
config.read(".trellonextactions")

board_id = config.get(config_name, 'board_id')
# TODO: Probably don't need to make this user-configurable as it shouldn't change...
application_key = config.get(config_name, 'application_key')
auth_token = config.get(config_name, 'auth_token')

# Get a list of Lists on the board
response = requests.get('https://api.trello.com/1/boards/' + board_id + '/lists?cards=none&key=' + application_key + '&token=' + auth_token)

lists_json = response.json();
#print json.dumps(response.json(), indent=4)

# TODO: handle failed response

# Find the "Projects" list
projects_id = None
for l in lists_json:
    if l['name'] == 'Projects':
        projects_id = l['id']
        break

# TODO: handle missing projects list

# List the cards on that list
response = requests.get('https://api.trello.com/1/lists/' + projects_id + '/cards?key=' + application_key + '&token=' + auth_token)

# TODO: handle failed response

#print json.dumps(response.json(), indent=4)

cards_json = response.json()
for project_card in cards_json:
    # The description of each card should contain the URL
    url = project_card['desc']

    # Parse the URL to get the short link
    url_bits = urlparse(url)
    # URLs all seem to be of the form /x/xyz123/nice-description
    path_bits = url_bits.path.split('/')

    # TODO: Handle missing URL or failed parse (create a Next Action to fix it, assuming one doesn't exist already?)
    
    short_id = path_bits[2]
    # Use the short link to look up the real ID
    # The link in the URL is known as the short link, you can use it to query (eg GET /boards/PxEQPoMz/) but you can't use it as part of a post / put. For that you need the real board ID.
    # https://www.reddit.com/r/trello/comments/4axfcd/where_is_my_trello_board_id/
    response = requests.get('https://api.trello.com/1/boards/' + short_id + '?key=' + application_key + '&token=' + auth_token)

    # TODO: Error handling
    real_id = response.json()['id']

    # Get the Todo list
    # TODO: Refactor to remove duplication
    response = requests.get('https://api.trello.com/1/boards/' + real_id + '/lists?cards=none&key=' + application_key + '&token=' + auth_token)

    lists_json = response.json();

    # TODO: handle failed response

    todo_id = None
    for l in lists_json:
        if l['name'] == 'Todo':
            todo_id = l['id']
            break

    # TODO: handle missing todo list

    # Get the top card
    response = requests.get('https://api.trello.com/1/lists/' + todo_id + '/cards?key=' + application_key + '&token=' + auth_token)

    # TODO: handle failed response

    cards_json = response.json()

    # TODO: Do we always get cards in correct order?
    next_action_card = cards_json[0]
    
    # TODO: handle missing Next Action

    # Spit out a sensible Next Action name
    print project_card['name'] + ' - ' + next_action_card['name']
