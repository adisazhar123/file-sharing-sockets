import socket
import threading
import os
import pickle
import time
import traceback
import sqlite3
import shutil
import zipfile

class ServerThread(threading.Thread):
    def __init__(self, client, data_port):
        self.client_socket = client[0]
        self.client_address = client[1]
        self.working_dir = os.getcwd() + '/core'
        self.server_root = os.getcwd()
        self.original_working_dir = os.getcwd() + '/core'
        self.data_address = ('0.0.0.0', data_port)
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
                elif client_data['cmd'] == "UPLOAD_DIR":
                    print 'in upload dir'
                    self.UPLOAD_DIR(client_data["params"]["zip_name"], client_data['params']['original_dir_name'])
                elif client_data['cmd'] == "DELETE":
                    self.DELETE(client_data['params']['file_dir_name'])
                elif client_data["cmd"] == "SHARE":
                    share_to = client_data["params"]['shared_to']
                    to_share = client_data["params"]['file_dir_name']
                    self.SHARE(share_to, to_share)
                elif client_data["cmd"] == "REGISTER":
                    username = client_data["params"]["username"]
                    password = client_data["params"]["password"]
                    self.REGISTER(username, password)

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
                self.original_working_dir = self.working_dir
                print self.original_working_dir
            auth = pickle.dumps(auth)
            client_data_socket.send(auth)
        except Exception as e:
            print 'AUTH ERROR ' + str(e)
            traceback.print_exc()
        finally:
            self.close_data_socket()
            print("auth closed")

    def REGISTER(self, username, password):
        try:
            client_data_socket, client_data_address = self.start_data_socket()
            credentials = (username, password, )

            db_conn = sqlite3.connect('file_sharing_sockets.db')
            db = db_conn.cursor()
            db.execute('SELECT * FROM user where user_name=? AND password=?', credentials)
            auth = db.fetchone()
            # already an account with given username
            if auth != None:
                message = 'Already an account with the provided username. Please use a different username.'
            else:
                db.execute('INSERT INTO user (user_name, password, core_dir) values(?, ?, ?)', (username, password, username))
                db_conn.commit()
                os.makedirs(os.getcwd() + '/core/' +  username)
                message = 'Account created.'
            auth = pickle.dumps(message)
            client_data_socket.send(auth)
        except Exception as e:
            print 'REGIS ERROR ' + str(e)
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

    def UPLOAD_DIR(self, zip_name, original_dir_name):
        try:
            client_data_socket, client_data_address = self.start_data_socket()
            f = open(self.working_dir + '/' + zip_name, 'wb')
            while True:
                bytes = client_data_socket.recv(1024)
                print("data %s", (bytes))
                if not bytes:
                    break
                f.write(bytes)
            f.close()
            print 'upload zip completed'
        #     extract the zip file
            print 'extracting the zip file'
            new_dir = self.working_dir + '/' + original_dir_name
            # check if dir exists
            if not os.path.exists(new_dir):
                print 'making directory'
                os.makedirs(new_dir)
            else:
                print 'making directory, adding unique value to it'
                unique = time.time()
                os.makedirs(new_dir + "_" + str(int(unique)))

            zip_ref = zipfile.ZipFile(self.working_dir + '/' + zip_name, 'r')
            zip_ref.extractall(new_dir + '/' + original_dir_name)
            zip_ref.close()

            print 'zip file extracted'
            # delete the zip file
            print 'deleting zip file'
            os.remove(self.working_dir + '/' + zip_name)
            print 'zip file deleted'
        except Exception as e:
            print 'Error ' + str(e)
        finally:
            self.data_socket.close()

    def CD(self, dirName):
        try:
            if dirName == "..":
                if self.working_dir == self.original_working_dir:
                    pass
                # go to root after going back from "[Shared To] - ..." folder
                elif self.working_dir.rfind('/[Shared To] - ') > 0:
                    self.working_dir = self.original_working_dir
                else:
                    slashIndex = self.working_dir.rfind('/')
                    self.working_dir = self.working_dir[:slashIndex]
            # redirect to "[Shared To] - ..." when go to "[Shared From] - ..."
            elif dirName[:16] == "[Shared From] - ":
                self.working_dir = self.working_dir + '/' + dirName

                sharedToIndex = self.working_dir.rfind('/core') + 6
                sharedTo = self.working_dir.rfind('/[Shared From] - ')
                sharedToPerson = self.working_dir[sharedToIndex:sharedTo]
                print 'shared to ' + sharedToPerson
                sharedFrom = self.working_dir.rfind('/[Shared From] - ') + 17
                sharedFromPerson = self.working_dir[sharedFrom:]
                print 'shared from ' + sharedFromPerson

                coreIndex = self.working_dir.rfind('/core')
                self.working_dir = self.working_dir[:coreIndex] + '/core/' + sharedFromPerson + '/[Shared To] - ' + sharedToPerson
            else:
                self.working_dir = self.working_dir + '/' + dirName
        except Exception as e:
            print 'CD ERROR ' + str(e)
            traceback.print_exc()
        print("Current working directory: " + self.working_dir)
    
    def LIST(self):
        try:
            client_data_socket, client_data_address = self.start_data_socket()
            entries = os.listdir(self.working_dir)
            entries = self.check_type(entries)
            entries = pickle.dumps(entries)
            # time.sleep(0.5)
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
            else:
                print 'making directory, adding unique value to it'
                unique = time.time()
                os.makedirs(full_path + "_" + str(int(unique)))
        except Exception as e:
            print 'MKDIR ERROR ' + str(e)
            traceback.print_exc()

    # function used to check whether file or directory
    def check_type(self, files_dirs):
        file_dirs = []

        for fd in files_dirs:
            full_path = self.working_dir + '/' + str(fd)
            size = os.path.getsize(full_path)
            mtime = time.ctime(os.path.getmtime(full_path))
            print full_path, str(size)

            if os.path.isdir(full_path):
                file_dirs.append({'name': fd, 'type': 'dir', 'size': size, 'mtime': mtime})
            elif os.path.isfile(full_path):
                file_dirs.append({'name': fd, 'type': 'file', 'size': size, 'mtime': mtime})
            else:
                print 'unknown file'
        return file_dirs

    def DELETE(self, file_dir):
        full_path = self.working_dir + '/' + file_dir
        try:
            if not os.path.exists(full_path):
                print 'Not exists!'
            else:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                elif os.path.isfile(full_path):
                    os.remove(full_path)
        except Exception as e:
            print 'DELETE ERROR ' + str(e)
            traceback.print_exc()

    def SHARE(self, share_to, to_share):
        copy_dir = self.working_dir
        coreIndex = self.original_working_dir.rfind('/core') + 5
        share_from = self.original_working_dir[(coreIndex+1):]
        
        print share_from
        share_to_path = self.original_working_dir[:coreIndex] + '/' + share_to

        if not os.path.exists(share_to_path):
            print 'User not found'
        else:
            print 'User found'
            self.working_dir = share_to_path
            self.MKDIR('[Shared From] - ' + share_from)
            self.working_dir = self.original_working_dir
            self.MKDIR('[Shared To] - ' + share_to)
            shutil.copyfile(copy_dir + '/' + to_share, self.working_dir + '/[Shared To] - ' + share_to + '/' + to_share)
