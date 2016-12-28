import requests
import json
import ConfigParser
import sys
import getopt
from urlparse import urlparse

application_key = ""
auth_token = ""
gtd_board_id = ""

def print_error_and_exit(message):
    sys.stderr.write(message + "\n")
    sys.exit(1)

def trello_api_request(url):
    try:
        response = requests.get(url)
    except:
        print_error_and_exit("Failed API request to " + url)

    if response.status_code != 200:
        print_error_and_exit("HTTP " + str(response.status_code) + " response from " + url)

    try:
        json = response.json()
    except:
        print_error_and_exit("Could not parse JSON response from " + url)

    return json

def get_cards_in_list(board_id, list_name):
    lists_on_board = trello_api_request('https://api.trello.com/1/boards/' + board_id + '/lists?cards=none&key=' + application_key + '&token=' + auth_token)
    
    # Find the named list
    list_id = None
    for l in lists_on_board:
        if l['name'] == list_name:
            list_id = l['id']
            break

    if list_id == None:
        raise ValueError("No list with name '" + list_name + "' found")

    # List the cards on that list
    cards_in_list = trello_api_request('https://api.trello.com/1/lists/' + list_id + '/cards?key=' + application_key + '&token=' + auth_token)

    return cards_in_list

def get_next_action_list():
    next_action_list = []
    error_list = []

    try:
        project_card_list = get_cards_in_list(gtd_board_id, 'Projects')
    except ValueError as e:
        print_error_and_exit(str(e))

    for project_card in project_card_list:
        next_action_text = project_card['name'] + ' - '
        try:
            # The description of each card should contain the URL
            url = project_card['desc']

            # Parse the URL to get the short link
            url_bits = urlparse(url)
            # URLs all seem to be of the form /x/xyz123/nice-description
            path_bits = url_bits.path.split('/')
            short_id = path_bits[2]
            todo_card_list = get_cards_in_list(short_id, 'Todo')

            if len(todo_card_list) > 0:
                next_action_card = todo_card_list[0]
                next_action_text += next_action_card['name']
                next_action_list.append(next_action_text)
            else:
                error_list.append(project_card['name'] + " - Todo list is empty")
        except ValueError as e:
            error_list.append(project_card['name'] + " - " + str(e))

    # Now return all the non-project Next Actions so that there's a consolidated list
    next_action_card_list = get_cards_in_list(gtd_board_id, 'Next Actions')

    for next_action_card in next_action_card_list:
        next_action_list.append(next_action_card['name'])

    return next_action_list, error_list

def load_config(config_name):
    global application_key
    global auth_token
    global gtd_board_id

    config = ConfigParser.ConfigParser()
    config.read(".trellonextactions")

    gtd_board_id = config.get(config_name, 'board_id')
    application_key = config.get(config_name, 'application_key')
    auth_token = config.get(config_name, 'auth_token')

def print_list(name, card_list):
    print name + ":"
    print
    for c in card_list:
        print " [ ] " + c
    print

def main():
    config_name = 'default'
    action = 'list'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "" ,["config="])
        for opt, arg in opts:
            if opt == '--config':
                config_name = arg
    except getopt.GetoptError as e:
        print_error_and_exit(str(e))
    
    try:
        load_config(config_name)
    except:
        print_error_and_exit("Failed to load config '" + config_name + "'")

    if action == 'list':
        next_action_list, error_list = get_next_action_list()

        print_list('Next Actions', next_action_list)
        if (len(error_list) > 0):
            print_list('Errors', error_list)
    else:
        print_error_and_exit("Unrecognised action '" + action + "'")

if __name__ == '__main__':
    sys.exit(main())
