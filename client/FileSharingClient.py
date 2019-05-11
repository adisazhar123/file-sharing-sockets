import pickle
import socket as Socket
import traceback


class Client():
    def __init__(self, (host, port), data_port, gui_client):
        self.host = host
        self.port = port
        self.data_port = data_port
        self.server_address = (host, port)
        self.socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
        self.gui_client = gui_client

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

    def start_data_socket(self):
        try:
            self.data_socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
            self.data_socket.connect((self.host, self.data_port))
        except Exception as e:
            print 'Error ' + str(e)
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

    def LIST(self):
        try:
            # send command to server
            self.send_command("LIST")
            # receive conn response
            self.receive_conn_response()

            self.start_data_socket()
            dir_list = self.data_socket.recv(1024)
            dir_list = pickle.loads(dir_list)
            print " " + str(dir_list)

            self.gui_client.reconstruct_tree(dir_list)

        except Exception, e:
            print 'Error ' + str(e)
            traceback.print_exc()
        finally:
            self.data_socket.close()

    def MKDIR(self, dir_name):
        self.send_command("MKDIR", dir_name)
        self.receive_conn_response()
        self.LIST()

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
            else:
                self.gui_client.authenticated()
                print " " + str(auth)
        except Exception as e:
            print 'Error ' + str(e)
            traceback.print_exc()
        finally:
            self.data_socket.close()

    def start(self):
        self.start_socket()

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
                bytes = self.data_socket.recv(1024)
                print('data=%s', (bytes))
                if not bytes:
                    break
                f.write(bytes)
            f.close()
        except Exception as e:
            print 'Error ' + str(e)
            traceback.print_exc()
        finally:
            self.gui_client.to_download_zip = False
