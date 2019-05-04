import socket
import threading
import os
import pickle

class ServerThread(threading.Thread):
    def __init__(self, (client_socket, client_address), data_port):
        self.client_socket = client_socket
        self.client_address = client_address
        self.working_dir = os.getcwd() + '/core'
        self.data_address = ('127.0.0.1', data_port)
        threading.Thread.__init__(self)

    def close_datasocket(self):
        print('Closing data connection')
        try:
            self.datasock.close()
        except:
            pass

    def start_socket(self):
        try:
            print('Opening data socket on ', self.data_address)
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.data_socket.bind(self.data_address)
            self.data_socket.listen(10)
            print('Data socket has started. Listening on ', self.data_address)

            return self.data_socket.accept()
        except Exception, e:
            print('Error on data socket client ', self.client_address)
            self.close_datasocket()

    def run(self):
        try:
            while True:
                client_data = self.client_socket.recv(1024)
                client_data = pickle.loads(client_data)
                print(client_data)
        except Exception, e:
            print('Error ', e.message)
