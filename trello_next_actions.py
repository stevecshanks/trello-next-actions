#!/usr/bin/env python3
import requests
import json
import sys
import getopt
import sqlite3
from nextactions.board import Board
from nextactions.config import Config
from nextactions.trello import Trello
from urllib.parse import urlparse

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
    c.execute('CREATE INDEX IF NOT EXISTS project_board_id '
              'ON next_action (project_board_id)')
    c.execute('CREATE INDEX IF NOT EXISTS project_next_action_id '
              'ON next_action (project_next_action_id)')
    c.execute('CREATE INDEX IF NOT EXISTS gtd_next_action_id '
              'ON next_action (gtd_next_action_id)')

    conn.commit()
    conn.close()


def trello_create_card(name, description):
    try:
        list_id = get_list_id(gtd_board_id, 'Next Actions')
    except ValueError:
        print_error_and_exit("Could not find ID for Next Actions list")

    data = {
        'name': name,
        'desc': description + "\r\n\r\nAuto-created by TrelloNextActions",
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


def sync_board(board):
    message_list = []

    # Figure out what cards already exist and so need no action
    exclude_list = []

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    for next_action_card in board.nextActionList:
        c.execute('SELECT id '
                  'FROM next_action WHERE project_board_id = ? '
                  'AND project_next_action_id = ?',
                  (board.id, next_action_card['id']))
        next_action = c.fetchone()

        if next_action is not None:
            exclude_list.append(next_action_card['id'])

    # Delete everything else for this project board
    to_delete_query = ('SELECT gtd_next_action_id FROM next_action '
                       'WHERE project_board_id = ? ')
    parameter_list = [board.id]
    if len(exclude_list):
        placeholder_string = ','.join('?' * len(exclude_list))
        to_delete_query += ('AND project_next_action_id NOT IN ('
                            + placeholder_string + ')')
        parameter_list += exclude_list

    c.execute(to_delete_query, tuple(parameter_list))
    to_delete_list = c.fetchall()

    for to_delete_row in to_delete_list:
        trello_delete_card(to_delete_row[0])
        c.execute('DELETE FROM next_action WHERE gtd_next_action_id = ?',
                  (to_delete_row[0],))
        message_list.append(board.name + ": Archived card " + to_delete_row[0])

    # Create any new cards
    for next_action_card in board.nextActionList:
        if next_action_card['id'] not in exclude_list:
            gtd_next_action_id = trello_create_card(board.name + " - "
                                                    + next_action_card['name'],
                                                    next_action_card['url'])
            c.execute('INSERT INTO next_action (project_board_id, '
                      'project_next_action_id, gtd_next_action_id) '
                      'VALUES (?, ?, ?)',
                      (board.id, next_action_card['id'], gtd_next_action_id))
            message_list.append(board.name + ": Created card "
                                + gtd_next_action_id)

    conn.commit()
    conn.close()

    return message_list


def reset():
    message_list = []

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute('SELECT gtd_next_action_id FROM next_action')
    next_action_list = c.fetchall()
    for next_action in next_action_list:
        trello_delete_card(next_action[0])
        c.execute('DELETE FROM next_action WHERE gtd_next_action_id = ?',
                  (next_action[0],))
        message_list.append("Archived card " + next_action[0])

    conn.commit()
    conn.close()

    return message_list


def trello_get_request(url):
    try:
        response = requests.get(url)
        return trello_handle_response(url, response)
    except Exception:
        print_error_and_exit("Failed API request to " + url)


def trello_post_request(url, data):
    try:
        response = requests.post(url, data)
        return trello_handle_response(url, response)
    except Exception:
        print_error_and_exit("Failed API request to " + url)


def trello_put_request(url, data):
    try:
        response = requests.put(url, data)
        return trello_handle_response(url, response)
    except Exception:
        print_error_and_exit("Failed API request to " + url)


def trello_handle_response(url, response):
    if response.status_code != 200:
        print_error_and_exit("HTTP " + str(response.status_code)
                             + " response from " + url)

    try:
        json = response.json()
    except Exception:
        print_error_and_exit("Could not parse JSON response from " + url)

    return json


def get_list_id(board_id, list_name):
    lists_on_board = trello_get_request('https://api.trello.com/1/boards/'
                                        + board_id + '/lists?cards=none'
                                        + '&key=' + application_key
                                        + '&token=' + auth_token)

    # Find the named list
    list_id = None
    for l in lists_on_board:
        if l['name'] == list_name:
            list_id = l['id']
            break

    if list_id is None:
        raise ValueError("No list with name '" + list_name + "' found")
    return list_id


def get_cards_in_list(board_id, list_name):
    list_id = get_list_id(board_id, list_name)

    # List the cards on that list
    cards_in_list = trello_get_request('https://api.trello.com/1/lists/'
                                       + list_id + '/cards'
                                       + '?key=' + application_key
                                       + '&token=' + auth_token)

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


def get_boards_with_owned_cards(trello):
    board_map = {}
    card_list = trello.getOwnedCards()

    for card in card_list:
        if card.board_id not in board_map:
            board_map[card.board_id] = trello.getBoardById(card.board_id)

        card_dict = {'id': card.id, 'name': card.name, 'url': "TODO"}
        board_map[card.board_id].nextActionList.append(card_dict)

    return board_map


def sync_next_actions(trello):
    message_list = []
    error_list = []

    board_map = get_boards_with_owned_cards(trello)

    per_project_list, per_project_error_list = get_next_action_per_project()
    error_list += per_project_error_list

    for project_card, next_action_card in per_project_list:
        board_id = next_action_card['idBoard']
        if board_id not in board_map:
            board_map[board_id] = Board(
                trello,
                {'id': board_id, 'name': project_card['name']})

        board_map[board_id].nextActionList.append(next_action_card)

    for board in board_map:
        message_list += sync_board(board_map[board])

    # There may be some "orphaned" cards for boards that have no more next
    # actions /  owned cards
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('SELECT project_board_id, gtd_next_action_id '
              'FROM next_action')
    all_cards_list = c.fetchall()
    for card in all_cards_list:
        if card[0] not in board_map:
            trello_delete_card(card[1])
            c.execute('DELETE FROM next_action WHERE gtd_next_action_id = ?',
                      (card[1],))
            message_list.append("Archived orphaned card " + card[1])

    conn.commit()
    conn.close()

    return message_list, error_list


def load_config(config_file):
    global application_key
    global auth_token
    global gtd_board_id

    config = Config()
    config.loadFromFile(config_file)

    gtd_board_id = config.get('board_id')
    application_key = config.get('application_key')
    auth_token = config.get('auth_token')

    return config


def print_list(name, card_list):
    print(name + ":")
    print()
    for c in card_list:
        print(" [ ] " + c)
    print()


def main():
    config_file = '.trellonextactions.json'
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

    try:
        setup_database()
    except Exception as e:
        print_error_and_exit("Error setting up DB: " + str(e))

    trello = Trello(config)

    if action == 'sync':
        message_list, error_list = sync_next_actions(trello)

        if len(message_list) > 0:
            print_list('Messages', message_list)
        if len(error_list) > 0:
            print_list('Errors', error_list)

    elif action == 'reset':
        message_list = reset()
        print_list("Reset", message_list)

    else:
        print_error_and_exit("Unrecognised action '" + action + "'")


if __name__ == '__main__':
    sys.exit(main())
