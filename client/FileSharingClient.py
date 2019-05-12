import pickle
import socket as Socket
import traceback


class Client():
    def __init__(self, (host, port), data_port, gui_client):
        """Constructor.
        Arguments:
            (host, port) -- tuple
            data_port -- port for data connection
        """
        self.host = host
        self.port = port
        self.data_port = data_port
        self.server_address = (host, port)
        self.socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)

        self.gui_client = gui_client
        self.gui_client.text = 'jdkfgdjfgnjdfg'

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
        self.data_socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
        self.data_socket.connect((self.host, self.data_port))

    def LIST(self):
        try:
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
    
    def CD(self):
        try:
            self.start_data_socket()
            print("1")
            dir_list = self.data_socket.recv(1024)
            print("2")
            dir_list = pickle.loads(dir_list)
            print " " + str(dir_list)

            self.gui_client.reconstruct_tree(dir_list)

        except Exception, e:
            print 'Error ' + str(e)
            traceback.print_exc()
        finally:
            self.data_socket.close()
    
    def run(self):
        self.start_socket()

        while True:
            cmd = raw_input("Enter command: ")
            if cmd == "LIST":
                commands = {"cmd": cmd}
                print(commands)
            elif cmd[:2] == "CD":
                commands = {"cmd": cmd[:2], "dir": cmd[3:]}
                print(commands)

            # send command to server
            self.socket.send(pickle.dumps(commands))
            # receive connection response
            conn_res = self.socket.recv(1024)
            conn_res = pickle.loads(conn_res)
            print conn_res["message"]

            if cmd == "LIST":
                self.LIST()
            if cmd[:2] == "CD":
                self.CD()

    def start(self):
        self.start_socket()
        
        while True:
            cmd = raw_input("Enter command: ")
            if cmd == "LIST":
                commands = {"cmd": cmd}
                print(commands)
            elif cmd[:2] == "CD":
                commands = {"cmd": cmd[:2], "dir": cmd[3:]}
                print(commands)

            # send command to server
            self.socket.send(pickle.dumps(commands))
            # receive connection response
            conn_res = self.socket.recv(1024)
            conn_res = pickle.loads(conn_res)
            print conn_res["message"]

            if cmd == "LIST":
                self.LIST()
            elif cmd[:2] == "CD":
                self.CD()
    
    def GUIHandle(self, commands):
        self.socket.send(pickle.dumps(commands))
        # receive connection response
        conn_res = self.socket.recv(1024)
        conn_res = pickle.loads(conn_res)
        print conn_res["message"]

        if commands["cmd"] == "LIST":
            self.LIST()
        elif commands["cmd"] == "CD":
            self.CD()
