# pylint: disable=maybe-no-member
import datetime
import requests
import crayons
import webbrowser
import json
import sys

def log(content: str, debug=False, raw=False):
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    to_print = f'{crayons.green(f"[{timestamp}]")} {content}'

    if debug == True:
        if '--debug' in sys.argv:
            to_print = f'{crayons.green(f"[{timestamp}]")} {crayons.yellow("[DEBUG]")} {content}'
        else:
            return None

    if raw == True:
        return to_print

    print(to_print)

clientsdata = {
        "AndroidGameClient": {
            "client_id": "3f69e56c7649492c8cc29f1af08a8a12",
            "secret": "b51ee9cb12234f50a69efa67ef53812e",
            "encoded": "M2Y2OWU1NmM3NjQ5NDkyYzhjYzI5ZjFhZjA4YThhMTI6YjUxZWU5Y2IxMjIzNGY1MGE2OWVmYTY3ZWY1MzgxMmU="
        },
        "IOSGameClient": {
            "client_id": "3446cd72694c4a4485d81b77adbb2141",
            "secret": "9209d4a5e25a457fb9b07489d313b41a",
            "encoded": "MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="
        },
        "SwitchGameClient": {
            "client_id": "5229dcd3ac3845208b496649092f251b",
            "secret": "e3bd2d3e-bf8c-4857-9e7d-f3d947d220c7",
            "encoded": "NTIyOWRjZDNhYzM4NDUyMDhiNDk2NjQ5MDkyZjI1MWI6ZTNiZDJkM2UtYmY4Yy00ODU3LTllN2QtZjNkOTQ3ZDIyMGM3"
        },
    }

def generate_with_device_code(client: str):

    selected_client_data = clientsdata[client]

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"basic {selected_client_data['encoded']}"
    }
    params = {
        "grant_type": "client_credentials"
    }

    log('Requesting client credentials...', True)

    response = requests.post('https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token', headers=headers, data=params)

    if response.status_code == 200:
        client_credentials = response.json()

        log(f'Success: {client_credentials}', True)

        headers = {
            "Authorization": f"bearer {client_credentials['access_token']}"
        }

        log('Requesting device_code session...', True)
        response = requests.post('https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization?prompt=login', headers=headers, data={})

        if response.status_code == 200:
            device_code_session = response.json()
            log(f'Success: {device_code_session}', True)

            while True:
                log('Opening web browser...', True)
                webbrowser.open(device_code_session["verification_uri_complete"])
                ready_check = input(log(f'Login with the required account and click "Confirm". Then type "ready": ', raw=True))
                ready_check.strip(' ')
                log('Waiting for user confirmation...', True)
                if ready_check.lower() == 'ready':

                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": f"basic {selected_client_data['encoded']}"
                    }
                    params = {
                        "grant_type": "device_code",
                        "device_code": device_code_session['device_code']
                    }
                    response = requests.post('https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token', headers=headers, data=params)

                    if response.status_code != 200:
                        log(crayons.red('You did\'nt clicked "Confirm" button yet'))
                        continue
                    else:
                        auth_session = response.json()
                        log(f'Success: {auth_session}', True)
                        break

            log(f'Generating device auths...', True)
            headers = {
                "Authorization": f"bearer {auth_session['access_token']}"
            }
            response = requests.post(f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{auth_session["account_id"]}/deviceAuth', headers=headers)

            account_info = requests.get(f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{auth_session["account_id"]}', headers=headers, data={})

            if response.status_code == 200:

                device_auths = response.json()
                accInfo = account_info.json()
                filename = accInfo["email"].split('@')[0]
                log(f'Success! {device_auths}', True)

                newdata = {
                    "device_id": device_auths['deviceId'],
                    "account_id": device_auths['accountId'],
                    "secret": device_auths['secret']
                }
                print('')
                save_selections = ['device_auths.json', f'{filename}.json']
                listcls = []
                count = 0
                for selection in save_selections:
                    count += 1
                    listcls.append(count)
                    log(f'{crayons.red("-")} {count}. {selection}')
            

                while True:
                    save_selection = input(log(f'Select the output file: ', raw=True))
                    try:
                        save_selection.strip(' ')
                        if int(save_selection) not in listcls:
                            log(crayons.red('Invalid selection\n'))
                            continue

                    except:
                        log(crayons.red('Please enter a valid number\n'))
                        continue

                    final_save_selection = int(save_selection) -1
                    break

                kill_token(auth_session)

                if save_selections[final_save_selection] == 'device_auths.json':
                    prev_file = json.load(open('output/device_auths.json', 'r', encoding='utf-8'))
                    prev_file[accInfo["email"]] = newdata

                    with open('output/device_auths.json', 'w', encoding='utf-8') as f:
                        json.dump(prev_file, f, indent=4)
                        return newdata
                else:
                    with open(f'output/{save_selections[final_save_selection]}', 'w', encoding='utf-8') as f:
                        json.dump({accInfo["email"]: newdata}, f, indent=4)
                        return newdata

            else:
                log(f'Failed while generating device auths: {crayons.red(response.json())}')
                return False

        else:
            log(f'Failed while requesting device_code session: {crayons.red(response.json())}')
            return False

    else:
        log(f'Failed while fetching client credentials: {crayons.red(response.json())}')
        return False


def generate_with_auth_code(client: str):

    selected_client_data = clientsdata[client]
    log('Web browser opened...', True)
    webbrowser.open(f'https://www.epicgames.com/id/logout?redirectUrl=https%3A//www.epicgames.com/id/login%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253D{selected_client_data["client_id"]}%2526responseType%253Dcode')
    log('Waiting for code from the user...', True)
    code = input(log('Login with the required account and paste the code here: ', raw=True))
    code.strip(' ')

    log('Trying to auth with entered code...', True)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"basic {selected_client_data['encoded']}"
    }
    params = {
        "grant_type": "authorization_code",
        "code": code
    }
    response = requests.post('https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token', headers=headers, data=params)

    if response.status_code == 200:
        auth_session = response.json()
        log(f'Success: {auth_session}', True)

        headers = {
            "Authorization": f"bearer {auth_session['access_token']}"
        }
        log(f'Generating device auths...', True)
        response = requests.post(f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{auth_session["account_id"]}/deviceAuth', headers=headers)

        account_info = requests.get(f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{auth_session["account_id"]}', headers=headers, data={})

        if response.status_code == 200:
            device_auths = response.json()
            accInfo = account_info.json()
            filename = accInfo["email"].split('@')[0]
            log(f'Success: {device_auths}', True)

            newdata = {
                "device_id": device_auths['deviceId'],
                "account_id": device_auths['accountId'],
                "secret": device_auths['secret']
            }

            print('')
            save_selections = ['device_auths.json', f'{filename}.json']
            listcls = []
            count = 0
            for selection in save_selections:
                count += 1
                listcls.append(count)
                log(f'{crayons.red("-")} {count}. {selection}')
        

            while True:
                save_selection = input(log(f'Select the output file: ', raw=True))
                try:
                    save_selection.strip(' ')
                    if int(save_selection) not in listcls:
                        log(crayons.red('Invalid selection\n'))
                        continue

                except:
                    log(crayons.red('Please enter a valid number\n'))
                    continue

                final_save_selection = int(save_selection) -1
                break

            accInfo = account_info.json()
            kill_token(auth_session)

            if save_selections[final_save_selection] == 'device_auths.json':
                prev_file = json.load(open('output/device_auths.json', 'r', encoding='utf-8'))
                prev_file[accInfo["email"]] = newdata

                with open('output/device_auths.json', 'w', encoding='utf-8') as f:
                    json.dump(prev_file, f, indent=4)
                    return newdata
            else:
                with open(f'output/{save_selections[final_save_selection]}', 'w', encoding='utf-8') as f:
                    json.dump({accInfo["email"]: newdata}, f, indent=4)
                    return newdata

        else:
            log(f'Failed while trying to generate device auths: {crayons.red(response.json())}')
            return False
    else:
        log(f'Failed while trying to authenticate with authorization code: {crayons.red(response.json())}')
        return False


def kill_token(auth_session: dict):

    log('Killing generated auth session of user...', True)
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"bearer {auth_session['access_token']}"
    }
    response = requests.delete(f'https://account-public-service-prod.ol.epicgames.com/account/api/oauth/sessions/kill/{auth_session["access_token"]}', headers=headers)
    if response.ok:
        log('Killed!', True)