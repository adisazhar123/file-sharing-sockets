from client.FileSharingClient import Client
from Gui import App
import Tkinter as tk

HOST = '127.0.0.1'
PORT = 1337
DATA_PORT = 1338

if __name__ == '__main__':
    master = tk.Tk()
    app = App(master).start()
    master.mainloop()
