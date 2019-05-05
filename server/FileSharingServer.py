from server.FileSharingThread import ServerThread
import socket
import traceback


class Server:
    # Constructor receives host & port as tuple,
    # data port for data connection
    def __init__(self, connection, data_port):
        self.host = connection[0]
        self.port = connection[1]
        self.data_port = data_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start_socket(self):
        server_address = (self.host, self.port)

        try:
            print('Creating server socket ', server_address)
            self.socket.bind(server_address)
            self.socket.listen(10)
            print('Server is listening on ', server_address)
        except Exception as e:
            print('Failed to create server on ', server_address, ' because ', str(e.message))
            quit()

    def start(self):
        self.start_socket()

        try:
            while True:
                print('Waiting for connection')
                # pass in current accepted socket
                connection = self.socket.accept()
                thread = ServerThread(connection, self.data_port)
                thread.daemon = True
                thread.start()
                # print('New socket connection ', connection)
        except KeyboardInterrupt:
            print('Closing socket connection')
            traceback.print_exc()
            self.socket.close()
            quit()
