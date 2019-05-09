import socket
import threading
import os
import pickle
import traceback


class ServerThread(threading.Thread):
    def __init__(self, client, data_port):
        self.client_socket = client[0]
        self.client_address = client[1]
        self.working_dir = os.getcwd() + '/core'
        self.data_address = ('127.0.0.1', data_port)

        threading.Thread.__init__(self)

    def start_data_socket(self):
        try:
            print('Opening data socket on ', self.data_address)
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.data_socket.bind(self.data_address)
            self.data_socket.listen(10)
            conn_message = pickle.dumps({"message": "Data Connection opened. Transfer starting."})
            self.client_socket.send(conn_message)
            print('Data socket has started. Listening on ', self.data_address)

            return self.data_socket.accept()
        except Exception as e:
            print('Error on data socket client ', self.client_address)
            print(e)
            self.close_data_socket()

    def close_data_socket(self):
        print('Closing data connection')
        try:
            self.data_socket.close()
        except:
            pass

    def run(self):
        try:
            while True:
                client_data = self.client_socket.recv(1024)
                client_data = pickle.loads(client_data)
                print client_data["cmd"]

                if client_data["cmd"] == "LIST":
                    self.LIST()

        except Exception as e:
            self.close_data_socket()
            self.client_socket.close()
            print('Closed client socket ', self.client_socket)
            quit()

    def LIST(self):
        try:
            client_data_socket, client_data_address = self.start_data_socket()
            entries = os.listdir(self.working_dir)
            entries = self.check_type(entries)

            entries = pickle.dumps(entries)
            client_data_socket.send(entries)

        except Exception as e:
            print 'LIST ERROR ' + str(e)
            traceback.print_exc()
        finally:
            self.close_data_socket()

    def check_type(self, files_dirs):
        file_dirs = []

        for fd in files_dirs:
            if os.path.isdir(self.working_dir + '/' + str(fd)):
                file_dirs.append({'name': fd, 'type': 'dir'})
            elif os.path.isfile(self.working_dir + '/' + str(fd)):
                file_dirs.append({'name': fd, 'type': 'file'})
            else:
                print 'unknown file'
        return file_dirs
