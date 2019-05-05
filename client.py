from client.FileSharingClient import Client

HOST = '127.0.0.1'
PORT = 1337
DATA_PORT = 1338

if __name__ == '__main__':
    fsc = Client((HOST, PORT), DATA_PORT)
    fsc.start()
