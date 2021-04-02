# pylint: disable=maybe-no-member
from util import log, config, generate_with_device_code, generate_with_auth_code
import requests
import crayons
import time
import json
import os
import sys

if config()['output_type'] not in [0, 1]:
    log(f'{crayons.red("[ERROR]")} The selected output type in config.json are invalid. Make sure is one of these: "1" "0"')
    exit()

def init():
    os.system(f'{"clear" if sys.platform != "win32" else "cls"}')
    log(f'{crayons.cyan("Device Auth Tool", bold=True)} {crayons.magenta("-", bold=True)} {crayons.cyan("By Bay#8172", bold=True)}\n')

    clients = ['SwitchGameClient', 'IOSGameClient', 'AndroidGameClient']
    listcls = []
    count = 0
    for client in clients:
        count += 1
        listcls.append(count)
        log(f'{crayons.red("-")} {count}. {client}')

    while True:
        selected_client = input(log(f'Select the client to use: ', raw=True))

        try:
            selected_client.strip(' ')
            if int(selected_client) not in listcls:
                log(crayons.red('Invalid selection\n'))
                continue

        except:
            log(crayons.red('Please enter a valid number\n'))
            continue

        final_client_selection = int(selected_client) -1
        log(f'Using {crayons.magenta(clients[final_client_selection])}...\n')
        break

    grant_types = ['Authorization Code', 'Device Code']
    listcls = []
    count = 0
    for grant in grant_types:
        count += 1
        listcls.append(count)
        log(f'{crayons.red("-")} {count}. {grant}')

    while True:
        selected_grant = input(log(f'Select the grant type to use: ', raw=True))

        try:
            selected_grant.strip(' ')
            if int(selected_grant) not in listcls:
                log(crayons.red('Invalid selection\n'))
                continue

        except:
            log(crayons.red('Please enter a valid number\n'))
            continue

        final_grant_selection = int(selected_grant) -1
        log(f'Using {crayons.magenta(grant_types[final_grant_selection])}...\n')
        break

    if grant_types[final_grant_selection] == 'Device Code':
        data = generate_with_device_code(clients[final_client_selection])
        if data == False:
            log('Failed device auth generation.')
        else:
            log('Generated device auths successfully!')

    elif grant_types[final_grant_selection] == 'Authorization Code':
        data = generate_with_auth_code(clients[final_client_selection])
        if data == False:
            log('Failed device auth generation.')
        else:
            log('Generated device auths successfully!')

    time.sleep(7.5)

if __name__ == '__main__':
    while True:
        init()