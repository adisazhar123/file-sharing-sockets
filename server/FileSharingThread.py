import socket
import threading
import os
import pickle
import time
import traceback
import sqlite3
import shutil


class ServerThread(threading.Thread):
    def __init__(self, client, data_port):
        self.client_socket = client[0]
        self.client_address = client[1]
        self.working_dir = os.getcwd() + '/core'
        self.server_root = os.getcwd()
        self.original_working_dir = os.getcwd() + '/core'
        self.data_address = ('127.0.0.1', data_port)
        threading.Thread.__init__(self)

    def start_data_socket(self):
        try:
            print('Opening data socket on ', self.data_address)
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.data_socket.bind(self.data_address)
            self.data_socket.settimeout(10)
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
                # match the commands given by client
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
                    full_file_dir_name = self.working_dir + '/' + client_data["params"]["file_dir_name"]
                    file_dir_name = client_data["params"]["file_dir_name"]
                    self.DOWNLOAD(full_file_dir_name, file_dir_name)
                elif client_data["cmd"] == "CD":
                    print("in CD")
                    self.CD(client_data["params"])
                elif client_data["cmd"] == "UPLOAD":
                    print("in UPLOAD ")
                    print(client_data["params"])
                    self.UPLOAD(client_data["params"]["file_dir_name"])
                elif client_data['cmd'] == "DELETE":
                    self.DELETE(client_data['params']['file_dir_name'])

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
            # found a matching credential
            if auth != None:
                self.working_dir = self.working_dir + '/' + auth[3]
            auth = pickle.dumps(auth)
            client_data_socket.send(auth)
        except Exception as e:
            print 'AUTH ERROR ' + str(e)
            traceback.print_exc()
        finally:
            self.close_data_socket()
            print("auth closed")

    def DOWNLOAD(self, full_file_dir_name, file_dir_name):
        print 'about to download', full_file_dir_name
        # check if pointer file_dir_name exists
        if not os.path.exists(full_file_dir_name):
            print 'NOT EXIST'
        else:
            print 'in else download'
            try:
                client_data_socket, client_data_address = self.start_data_socket()
                # given path is a file
                if os.path.isfile(full_file_dir_name):
                    f = open(full_file_dir_name, 'rb')
                    bytes = f.read(1024)
                    while(bytes):
                        client_data_socket.send(bytes)
                        bytes = f.read(1024)
                    f.close()
                #     given path is a directory -> zip the directory
                elif os.path.isdir(full_file_dir_name):
                    # zip temporarily to a folder
                    temp_zip_name = str(time.time())
                    shutil.make_archive(self.server_root + '/tmp/' + temp_zip_name, 'zip', full_file_dir_name)
                    # read the zipped file
                    f = open(self.server_root + '/tmp/' + temp_zip_name + '.zip', 'rb')
                    bytes = f.read(1024)
                    while(bytes):
                        client_data_socket.send(bytes)
                        bytes = f.read(1024)
                    f.close()
                    # remove the temp zipped file
                    os.remove(self.server_root + '/tmp/' + temp_zip_name + '.zip')
            except Exception as e:
                print 'DOWNLOAD ERROR ' + str(e)
                traceback.print_exc()
            finally:
                self.close_data_socket()
    
    def UPLOAD(self, fileName):
        print(fileName)
        if os.path.exists(self.working_dir + fileName):
            print("The file already exists!")
        else:
            print("in else upload")
            try:
                client_data_socket, client_data_address = self.start_data_socket()
                f = open(self.working_dir + '/' + fileName, "wb")
                while True:
                    ## RECV IS STILL HANGING IF A FILE > 1024 BYTES IS UPLOADED
                    bytes = client_data_socket.recv(1024)
                    print("data %s", (bytes))
                    if not bytes:
                        break
                    f.write(bytes)
                f.close()
                print("UPLOAD completed.")
            except Exception as e:
                print 'UPLOAD ERROR ' + str(e)
                traceback.print_exc()
            finally:
                self.data_socket.close()
                print("upload socket closed")
    def CD(self, dirName):
        if dirName == "..":
            if self.working_dir == self.original_working_dir:
                pass
            else:
                slashIndex = self.working_dir.rfind('/')
                self.working_dir = self.working_dir[:slashIndex]
        else:
            self.working_dir = self.working_dir + '/' + dirName
        
        print("Current working directory: " + self.working_dir)
    
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
            # TODO: alert/ warning for duplicated name
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

    def DELETE(self, file_dir):
        full_path = self.working_dir + '/' + file_dir
        if not os.path.exists(full_path):
            print 'Not exists!'
        else:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            # todo check file