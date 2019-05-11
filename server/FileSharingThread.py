import socket
import threading
import os
import pickle
import traceback
import sqlite3



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
                elif client_data["cmd"] == "AUTHENTICATE":
                    username = client_data["params"]["username"]
                    password = client_data["params"]["password"]
                    self.AUTHENTICATE(username, password)
                elif client_data["cmd"] == "DOWNLOAD":
                    print 'in download .. while true'
                    # concat for full path
                    file_dir_name = self.working_dir + '/' + client_data["params"]["file_dir_name"]
                    self.DOWNLOAD(file_dir_name)

        except Exception as e:
            self.close_data_socket()
            self.client_socket.close()
            print('Closed client socket ', self.client_socket)
            traceback.print_exc()
            quit()

    def AUTHENTICATE(self, username, password):
        try:
            client_data_socket, client_data_address = self.start_data_socket()
            credentials = (username, password, )

            db_conn = sqlite3.connect('file_sharing_sockets.db')
            db = db_conn.cursor()
            db.execute('SELECT * FROM user where user_name=? AND password=?', credentials)
            auth = db.fetchone()
            if auth != None:
                self.working_dir = self.working_dir + '/' + auth[3]
            auth = pickle.dumps(auth)
            client_data_socket.send(auth)
        except Exception as e:
            print 'AUTH ERROR ' + str(e)
            traceback.print_exc()
        finally:
            self.close_data_socket()

    def DOWNLOAD(self, file_dir_name):
        print 'about to download', file_dir_name
        # check if pointer file_dir_name exists
        if not os.path.exists(file_dir_name):
            print 'NOT EXIST'
        else:
            print 'in else download'
            try:
                client_data_socket, client_data_address = self.start_data_socket()
                if os.path.isfile(file_dir_name):
                    f = open(file_dir_name, 'rb')
                    bytes = f.read(1024)
                    while(bytes):
                        client_data_socket.send(bytes)
                        bytes = f.read(1024)
                    f.close()
            except Exception as e:
                print 'DOWNLOAD ERROR ' + str(e)
                traceback.print_exc()
            finally:
                self.close_data_socket()

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
