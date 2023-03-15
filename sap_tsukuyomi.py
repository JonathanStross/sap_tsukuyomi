import argparse
import csv
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
                print(response)
            except pyrfc.LogonError as ex:
                if ex.message == 'Name or password is incorrect (repeat logon)':
                    activeClients.append(client[0])
                    if args.verbose:
                        print('Client detected on: ', client[0])
                else:
                    if args.verbose:
                        print(ex.message)
                    else:
                        pass
    if len(activeClients) > 0:
        print("Active clients:")
        for cli in activeClients:
            print('Active client on: ', cli)
        return True
    else:
        return False

def checkStdUsers():
    global target
    global activeClients
    with open('standardusers.csv') as users_csv:
        csv_reader_users = csv.reader(users_csv, delimiter='\n')
        for rows in csv_reader_users:
            credentials = rows[0].split(';')
            clients = credentials[2].split(',')

            #in case of * exists, check all mentioned and all active
            if '*' in clients:
                for cli in activeClients:
                    pass
            #check only active clients
            for cli in clients:
                connection_params = {
                    'user': credentials[0],
                    'passwd': credentials[1],
                    'ashost': target,
                    'client': cli,
                    'sysnr': '00'
                }

print('Tsukuyomi')

if args.target:
    target = args.target
else:
    print("No target defined. Please add target.")
    end = True

activeClients = []

checkClients()
#if not end:
#    if checkClients():
#        checkStdUsers()

#checkStdUsers()