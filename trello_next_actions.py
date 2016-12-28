import requests
import json
import ConfigParser
import sys
import getopt
import sqlite3
from urlparse import urlparse

application_key = ""
auth_token = ""
gtd_board_id = ""

db_file = 'trellonextactions.db'


def print_error_and_exit(message):
    sys.stderr.write(message + "\n")
    sys.exit(1)


def setup_database():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS next_action ('
              'id INTEGER NOT NULL PRIMARY KEY, '
              'project_board_id VARCHAR(255) NOT NULL, '
              'project_next_action_id VARCHAR(255) NOT NULL, '
              'gtd_next_action_id VARCHAR(255) NOT NULL)')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS project_board '
              'ON next_action (project_board_id)')

    conn.commit()
    conn.close()


def trello_create_card(name, description):
    # TODO Make this look up automatically
    list_id = '586416e065011a16b0f86914'
    data = {
        'name': name,
        'desc': description,
        'idList': list_id,
        'key': application_key,
        'token': auth_token
    }

    response = trello_post_request('https://api.trello.com/1/cards/', data)
    return response['id']


def trello_delete_card(card_id):
    # Note: Only archive cards, just in case they've been edited by the user
    data = {
        'value': 'true',
        'key': application_key,
        'token': auth_token
    }

    response = trello_put_request('https://api.trello.com/1/cards/'
                                  + card_id + "/closed",
                                  data)


def sync_card(project_name, next_action_card):
    # Do we have a next action for this project board?
    has_next_action = False

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute('SELECT project_next_action_id, gtd_next_action_id '
              'FROM next_action WHERE project_board_id = ?',
              (next_action_card['idBoard'],))
    next_action = c.fetchone()

    if next_action is not None:
        print "Found next action: " + next_action[1]
        # Is it the same as our current next action?
        if next_action_card['id'] == next_action[0]:
            print "... but it's the same as our current action"
            has_next_action = True
        else:
            # If not, delete from GTD board and database
            print "Need to sync these up"
            trello_delete_card(next_action[1])
            c.execute('DELETE FROM next_action WHERE project_board_id = ?',
                      (next_action_card['idBoard'],))

    # If no next action, create one and add to DB
    if has_next_action is False:
        gtd_next_action_id = trello_create_card(project_name + " - "
                                                + next_action_card['name'],
                                                next_action_card['url'])
        c.execute('INSERT INTO next_action (project_board_id, '
                  'project_next_action_id, gtd_next_action_id) '
                  'VALUES (?, ?, ?)',
                  (next_action_card['idBoard'], next_action_card['id'],
                   gtd_next_action_id))

    conn.commit()
    conn.close()

    # TODO: error handling etc


def trello_get_request(url):
    try:
        response = requests.get(url)
        return trello_handle_response(url, response)
    except:
        print_error_and_exit("Failed API request to " + url)


def trello_post_request(url, data):
    try:
        response = requests.post(url, data)
        return trello_handle_response(url, response)
    except:
        print_error_and_exit("Failed API request to " + url)


def trello_put_request(url, data):
    try:
        response = requests.put(url, data)
        return trello_handle_response(url, response)
    except:
        print_error_and_exit("Failed API request to " + url)       


def trello_handle_response(url, response):
    if response.status_code != 200:
        print_error_and_exit("HTTP " + str(response.status_code)
                             + " response from " + url)

    try:
        json = response.json()
    except:
        print_error_and_exit("Could not parse JSON response from " + url)

    return json


def get_cards_in_list(board_id, list_name):
    lists_on_board = trello_get_request('https://api.trello.com/1/boards/'
                                        + board_id + '/lists?cards=none&key='
                                        + application_key + '&token='
                                        + auth_token)

    # Find the named list
    list_id = None
    for l in lists_on_board:
        if l['name'] == list_name:
            list_id = l['id']
            break

    if list_id is None:
        raise ValueError("No list with name '" + list_name + "' found")

    # List the cards on that list
    cards_in_list = trello_get_request('https://api.trello.com/1/lists/'
                                       + list_id + '/cards?key='
                                       + application_key + '&token='
                                       + auth_token)

    return cards_in_list


def get_next_action_per_project():
    next_action_list = []
    error_list = []

    try:
        project_card_list = get_cards_in_list(gtd_board_id, 'Projects')
    except ValueError as e:
        print_error_and_exit(str(e))

    for project_card in project_card_list:
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
                next_action_list.append([project_card, next_action_card])
            else:
                error_list.append(project_card['name']
                                  + " - Todo list is empty")
        except ValueError as e:
            error_list.append(project_card['name'] + " - " + str(e))

    return next_action_list, error_list


def get_next_action_list():
    next_action_list = []
    error_list = []

    per_project_list, per_project_error_list = get_next_action_per_project()
    error_list += per_project_error_list

    for project_card, next_action_card in per_project_list:
        next_action_text = project_card['name'] + ' - '
        next_action_text += next_action_card['name']
        next_action_list.append(next_action_text)

    # Now return all the non-project Next Actions so that there's a
    # consolidated list
    next_action_card_list = get_cards_in_list(gtd_board_id, 'Next Actions')

    for next_action_card in next_action_card_list:
        next_action_list.append(next_action_card['name'])

    return next_action_list, error_list


def sync_next_actions():
    message_list = []
    error_list = []

    per_project_list, per_project_error_list = get_next_action_per_project()
    error_list += per_project_error_list

    try:
        setup_database()
    except Exception as e:
        print_error_and_exit("Error setting up DB: " + str(e))

    for project_card, next_action_card in per_project_list:
        sync_card(project_card['name'], next_action_card)

    return message_list, error_list


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
        opts, args = getopt.getopt(sys.argv[1:], "", ["config="])
        for opt, arg in opts:
            if opt == '--config':
                config_name = arg
    except getopt.GetoptError as e:
        print_error_and_exit(str(e))

    if len(args) > 1:
        print_error_and_exit("Too many arguments supplied")
    elif len(args) == 1:
        action = args[0]

    try:
        load_config(config_name)
    except:
        print_error_and_exit("Failed to load config '" + config_name + "'")

    if action == 'list':
        next_action_list, error_list = get_next_action_list()

        print_list('Next Actions', next_action_list)
        if (len(error_list) > 0):
            print_list('Errors', error_list)
    elif action == 'sync':
        message_list, error_list = sync_next_actions()

        print_list('Messages', message_list)
        if (len(error_list) > 0):
            print_list('Errors', error_list)
    else:
        print_error_and_exit("Unrecognised action '" + action + "'")

if __name__ == '__main__':
    sys.exit(main())
