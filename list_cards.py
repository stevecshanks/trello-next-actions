import requests
import json
from urlparse import urlparse
import ConfigParser
import sys, getopt

def get_cards_in_list(board_id, list_name):
    # Get a list of Lists on the board
    response = requests.get('https://api.trello.com/1/boards/' + board_id + '/lists?cards=none&key=' + application_key + '&token=' + auth_token)

    lists_json = response.json();
    
    # TODO: handle failed response

    # Find the named list
    list_id = None
    for l in lists_json:
        if l['name'] == list_name:
            list_id = l['id']
            break

    # TODO: handle missing list

    # List the cards on that list
    response = requests.get('https://api.trello.com/1/lists/' + list_id + '/cards?key=' + application_key + '&token=' + auth_token)

    # TODO: handle failed response

    return response.json()


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

gtd_board_id = config.get(config_name, 'board_id')
# TODO: Probably don't need to make this user-configurable as it shouldn't change...
application_key = config.get(config_name, 'application_key')
auth_token = config.get(config_name, 'auth_token')

# Get a list of all projects
project_card_list = get_cards_in_list(gtd_board_id, 'Projects')

# Mmmm, whitespace
print
print

for project_card in project_card_list:
    # The description of each card should contain the URL
    url = project_card['desc']

    # Parse the URL to get the short link
    url_bits = urlparse(url)
    # URLs all seem to be of the form /x/xyz123/nice-description
    path_bits = url_bits.path.split('/')

    # TODO: Handle missing URL or failed parse (create a Next Action to fix it, assuming one doesn't exist already?)
    
    short_id = path_bits[2]

    todo_card_list = get_cards_in_list(short_id, 'Todo')

    # TODO: Do we always get cards in correct order?
    next_action_card = todo_card_list[0]
    
    # TODO: handle missing Next Action

    # Spit out a sensible Next Action name
    print ' * ' + project_card['name'] + ' - ' + next_action_card['name']

# Now print out all the non-project Next Actions so that there's a consolidated list
next_action_card_list = get_cards_in_list(gtd_board_id, 'Next Actions')

for next_action_card in next_action_card_list:
    print ' * ' + next_action_card['name']

# Mmmm, whitespace
print
print

