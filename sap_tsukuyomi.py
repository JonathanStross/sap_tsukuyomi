import argparse
import csv
import re

from tqdm import tqdm
from pyrfc import Connection
import pyrfc


parser = argparse.ArgumentParser(
    prog='Tsukuyomi',
    description='Reading clients and default users of SAP.',
    epilog='Text at the bottom of help'
)
#arguments
parser.add_argument('-t', '--target')
parser.add_argument('-v', '--verbose', action='store_true')


args = parser.parse_args()
target = ''
verbose = False
end = False


def checkClients():
    global activeClients
    # client detection
    with open('clients.csv') as clients_csv:
        csv_reader_clients = csv.reader(clients_csv, delimiter='\n')
        print('Testing 999 clients...')
        for client in tqdm(csv_reader_clients, unit=" Clients"):
            # for client in csv_reader_clients:
            connection_params = {
                'user': 'test123',
                'passwd': 'test123',
                'ashost': target,
                'sysnr': '00',
                'client': client[0]
            }
            try:
                conn = Connection(**connection_params)
                response = conn.call('RFC_SYSTEM_INFO')
                #print(response)
            except pyrfc.LogonError as ex:
                if ex.message == 'Name or password is incorrect (repeat logon)':
                    activeClients.append(client[0])
                    if args.verbose:
                        print('\nClient detected on: ', client[0])
                else:
                    if args.verbose:
                        print(ex.message)
                    else:
                        pass
    if len(activeClients) > 0:
        print("Active clients:")
        for cli in activeClients:
            print('Active client on: ', cli)
            storeActiveClients()
        return True
    else:
        return False

def checkStdUsers():
    global activeUsers
    global target
    global activeClients
    with open('standardusers.csv') as users_csv:
        csv_reader_users = csv.reader(users_csv, delimiter='\n')
        for rows in csv_reader_users:
            credentials = rows[0].split(';')
            client = credentials[2]
            #in case of * exists, check all mentioned and all active
            for cli in activeClients:
                connection_params = {
                    'user': credentials[0],
                    'passwd': credentials[1],
                    'ashost': cli['ip'],
                    'sysnr': '00',
                    'client': cli['client']
                    }
                try:
                    print("\n-------------------Trying logon-------------------")
                    print("Client: ", cli['client'])
                    print("User: ", credentials[0])
                    print("Password: ", credentials[1])
                    conn = Connection(**connection_params)
                    response = conn.call('RFC_SYSTEM_INFO')
                    print('\nUser/Password FOUND:\n', credentials[0], ":", credentials[1], "on client: ",
                              cli)
                    activeUsers.append(credentials[0] + "," + credentials[1] + "," + cli['client'])
                    print("\n-------------------------------------------------\n")
                except pyrfc.LogonError as ex:
                    if ex.message == 'Name or password is incorrect (repeat logon)':
                        print("Login NOT possible with: ", credentials[0], ", ", credentials[1], ", ", cli)


def lockUsers():
    pass

def storeActiveClients():
    global target
    global activeClients
    f = open('foundclients.csv', 'w+')
    writer = csv.writer(f)
    for client in activeClients:
        writer.writerow(target + ';' + client)
    f.close()

def listActiveClients():
    global activeClients
    print("IP:\tClient:")
    for client in activeClients:
        print(client['ip'], "\t", client['client'])

def loadActiveClients():
    global activeClients
    f = open('foundclients.csv', 'r')
    csvreader = csv.reader(f, delimiter=';')
    for row in csvreader:
        client = row[1]
        ip = row[0]
        client = {
            'ip': ip,
            'client': client
        }
        activeClients.append(client)
    f.close()


print("""  _____          _                                _ 
 |_   _|__ _   _| | ___   _ _   _  ___  _ __ ___ (_)
   | |/ __| | | | |/ / | | | | | |/ _ \| '_ ` _ \| |
   | |\__ \ |_| |   <| |_| | |_| | (_) | | | | | | |
   |_||___/\__,_|_|\_\\__,_|\__, |\___/|_| |_| |_|_|
                            |___/                   """)
print("Reading SAP Sysnr, SAP Clients and active SAP Standard Users.")
print("Target IP: ", args.target, "\t", "Verbose mode: ", str(args.verbose))

if args.target:
    target = args.target
else:
    print("No target defined. Please add target.")
    end = True

activeClients = []
activeUsers = []


#checkClients() #check
loadActiveClients() #check
listActiveClients() #check
checkStdUsers()
