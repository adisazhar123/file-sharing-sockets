import os
import pickle
import shutil
import socket as Socket
import time
import traceback


class Client():
    def __init__(self, (host, port), data_port, gui_client):
        self.host = host
        self.port = port
        self.data_port = data_port
        self.server_address = (host, port)
        self.socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
        self.gui_client = gui_client

    # start socket connection
    def start_socket(self):
        print 'Starting connection to ' + str(self.host) + ':' + str(self.port)
        try:
            self.socket.connect(self.server_address)
            print 'Connected to ' + str(self.server_address)
        except Exception as e:
            print 'Connection to ' + str(self.server_address) + ' failed\n.'
            print e.message
            traceback.print_exc()
            self.socket.close()
            quit()

    # start data socket connection, on a different port
    def start_data_socket(self):
        try:
            self.data_socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
            self.data_socket.settimeout(10)
            self.data_socket.connect((self.host, self.data_port))
        except Exception as e:
            print 'Error ' + str(e)
            self.gui_client.popup_thread(str(e), "Please try again.")
            traceback.print_exc()

    # this function is used to send command to server using COMMAND PORT
    # cmd is the command
    # params is optional
    def send_command(self, cmd, params = None):
        commands = {"cmd": cmd, "params": params}
        self.socket.send(pickle.dumps(commands))

    # this function is called every time will call function send_command
    # get the response connection from server -> to make sure our command is received by server
    def receive_conn_response(self):
        conn_res = self.socket.recv(1024)
        conn_res = pickle.loads(conn_res)
        print conn_res["message"] + ' in message'

    # list files and dirs in current working dir
    def LIST(self):
        try:
            # send command to server
            self.send_command("LIST")
            # receive conn response
            self.receive_conn_response()
            # open data socket
            self.start_data_socket()
            # receive file and dirs
            dir_list = self.data_socket.recv(1024)
            dir_list = pickle.loads(dir_list)
            print " " + str(dir_list)
            # reconstruct GUI tree view
            self.gui_client.reconstruct_tree(dir_list)

        except Exception, e:
            print 'Error ' + str(e)
            traceback.print_exc()
        finally:
            self.data_socket.close()
    
    def CD(self, folder_name):
        self.send_command("CD", folder_name)
        self.receive_conn_response()
        self.LIST()
    
    # make directory
    def MKDIR(self, dir_name):
        self.send_command("MKDIR", dir_name)
        self.receive_conn_response()
        self.LIST()

    # login with credentials
    # TODO: add warning/ alert for wrong credentials
    def AUTHENTICATE(self, username, password):
        print username, password
        params = {'username': username, 'password': password}
        try:
            self.send_command("AUTHENTICATE", params)
            self.receive_conn_response()

            self.start_data_socket()
            auth = self.data_socket.recv(1024)
            auth = pickle.loads(auth)
            if auth == None:
                print 'NO credentials found'
                self.gui_client.popup_thread("Failed Authentication", "Authentication failed.\nPlease try again.")
            else:
                self.gui_client.authenticated()
                print " " + str(auth)
                self.data_socket.close()
                self.LIST()
        except Exception as e:
            print 'Error ' + str(e)
            traceback.print_exc()
        finally:
            print("auth closed")

    def start(self):
        self.start_socket()

    # Download folder or file
    # folders will be zipped
    def DOWNLOAD(self, file_dir_name):
        params = {'file_dir_name': file_dir_name}
        try:
            self.send_command('DOWNLOAD', params)
            self.receive_conn_response()

            self.start_data_socket()

            zip_extension = ''
            # if download file is zip, add .zip as extension
            if self.gui_client.to_download_zip:
                zip_extension = '.zip'

            f = open(self.gui_client.download_location + '/' + self.gui_client.to_download + zip_extension, 'wb')
            while True:
                ## RECV IS STILL HANGING IF A FILE > 1024 BYTES IS UPLOADED
                bytes = self.data_socket.recv(1024)
                print('data=%s', (bytes))
                if not bytes:
                    break
                f.write(bytes)
            f.close()
            self.gui_client.popup_thread("Success", "Download success")
        except Exception as e:
            print 'Error ' + str(e)
            traceback.print_exc()
        finally:
            self.gui_client.to_download_zip = False

    # upload a file
    def UPLOAD(self, file_dir_name):
        indx = file_dir_name.rfind('/')
        fileName = file_dir_name[indx+1:]
        params = {'file_dir_name': fileName}
        try:
            self.send_command('UPLOAD', params)
            self.receive_conn_response()
            
            self.start_data_socket()
            f = open(file_dir_name, 'rb')
            bytes = f.read(1024)
            while True:
                self.data_socket.send(bytes)
                bytes = f.read(1024)
                print("data: %s", (bytes))
                
                if not bytes:
                    break
            f.close()
            print("UPLOAD completed.")
            self.gui_client.popup_thread("Success", "Upload success")
        except Exception as e:
            print 'Error ' + str(e)
            self.gui_client.popup_thread("Error", str(e))
            traceback.print_exc()
        finally:
            self.data_socket.close()
            print("upload socket closed")
            self.LIST()

    # upload dir
    def UPLOAD_DIR(self, dir_name):
        if os.path.isdir(dir_name):
            try:
                print 'is a directory.. zipping ' + dir_name
                # zip temporarily to a folder
                temp_zip_name = str(time.time())
                shutil.make_archive(temp_zip_name, 'zip', dir_name)
                print 'zipped'
                print 'preparing to send to server'
                original_name = os.path.basename(dir_name)
                params = {'zip_name': temp_zip_name + '.zip', 'original_dir_name': original_name}
                self.send_command('UPLOAD_DIR', params)
                self.receive_conn_response()

                self.start_data_socket()
                # read the zipped file
                f = open(temp_zip_name + '.zip', 'rb')
                bytes = f.read(1024)
                while (bytes):
                    self.data_socket.send(bytes)
                    bytes = f.read(1024)
                f.close()
                # remove the temp zipped file
                os.remove(temp_zip_name + '.zip')
            except Exception as e:
                print "Error " + str(e)
                self.gui_client.popup_thread("Error", str(e))
                traceback.print_exc()
            finally:
                self.data_socket.close()
                print("upload dir data socket closed")
                self.LIST()

    # TODO: check if deleted is folder/ file
    def DELETE(self, to_delete):
        params = {'file_dir_name': to_delete}
        try:
            self.send_command('DELETE', params)
            self.receive_conn_response()
            self.gui_client.popup_thread("Success", "Delete success")
        except Exception as e:
            print 'Error ' + str(e)
            self.gui_client.popup_thread("Error", str(e))
            traceback.print_exc()
        finally:
            self.LIST()

    def SHARE(self, share_to, to_share):
        params = {'shared_to': share_to, 'file_dir_name': to_share}
        try:
            self.send_command("SHARE", params)
            self.receive_conn_response()
            self.gui_client.popup_thread("Success", "Share success")
        except Exception as e:
            print 'Error ' + str(e)
            self.gui_client.popup_thread("Error", str(e))
            traceback.print_exc()
        finally:
            self.LIST()

    def REGISTER(self, username, password):
        print username, password
        params = {'username': username, 'password': password}
        try:
            self.send_command("REGISTER", params)
            self.receive_conn_response()

            self.start_data_socket()
            register = self.data_socket.recv(1024)
            register = pickle.loads(register)
            self.gui_client.popup_thread("Registration", register)
        except Exception as e:
            print 'Error ' + str(e)
            self.gui_client.popup_thread("Error", str(e))
            traceback.print_exc()
        finally:
            self.data_socket.close()
            print("register closed")

    def EXIT(self):
        exit()
