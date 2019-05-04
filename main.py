from FileSharingServer import Server

if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 1337
    DATA_PORT = 1338
    server = Server((HOST, PORT), 1338)
    server.start()