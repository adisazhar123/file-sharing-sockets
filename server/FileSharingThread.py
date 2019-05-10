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

                conn_message = pickle.dumps({"message": "Connected to server."})
                self.client_socket.send(conn_message)

                if client_data["cmd"] == "LIST":
                    self.LIST()
                elif client_data["cmd"] == "MKDIR":
                    dir_name = client_data["params"]
                    self.MKDIR(dir_name)

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

    # create directory in current working directory
    def MKDIR(self, dir_name):
        full_path = self.working_dir + '/' + dir_name
        try:
            # check whether to be created dir exists
            if not os.path.exists(full_path):
                print 'making directory'
                os.makedirs(full_path)
        except Exception as e:
            print 'MKDIR ERROR ' + str(e)
            traceback.print_exc()

    # function used to check whether file or directory
    def check_type(self, files_dirs):
        file_dirs = []

        for fd in files_dirs:
            full_path = self.working_dir + '/' + str(fd)
            size = os.path.getsize(full_path)
            print full_path, str(size)

            if os.path.isdir(full_path):
                file_dirs.append({'name': fd, 'type': 'dir', 'size': size})
            elif os.path.isfile(full_path):
                file_dirs.append({'name': fd, 'type': 'file', 'size': size})
            else:
                print 'unknown file'
        return file_dirs
