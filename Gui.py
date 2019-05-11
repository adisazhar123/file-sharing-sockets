import Tkinter as tk
import ttk
from threading import *
from client.FileSharingClient import Client
from Tkinter import *
import tkSimpleDialog
import tkFileDialog

HOST = '127.0.0.1'
PORT = 1337
DATA_PORT = 1338


class App(Thread):
    def __init__(self, master):
        Thread.__init__(self)
        self.fsc = Client((HOST, PORT), DATA_PORT, self)

        self.master = master
        self.master.title('File Sharing Sockets')
        self.frame = Frame(master)
        self.frame.pack()

        self.construct_top_menu()
        self.construct_tree(self.master)

        self.menubar.entryconfig("Actions", state="disabled")

        self.popup = Menu(self.master, tearoff=0)
        self.popup.add_command(label="Download", command=self.browse_directory)
        self.popup.add_command(label="Share")
        self.popup.add_separator()

        # variable to hold download directory location
        self.download_location = ''
        # variable to hold the file/ dir to be downloaded
        self.to_download = ''

    def construct_top_menu(self):
        self.menubar = Menu(self.frame)

        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Create Directory", command=self.MKDIR)
        self.filemenu.add_command(label="Refresh", command=self.LIST)
        self.filemenu.add_command(label="Save")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit")

        self.filemenu2 = Menu(self.menubar, tearoff=0)
        self.filemenu2.add_command(label="Login", command=self.AUTHENTICATE)

        self.menubar.add_cascade(label="Actions", menu=self.filemenu)
        self.menubar.add_cascade(label="Account", menu=self.filemenu2)
        self.master.config(menu=self.menubar)

    def construct_tree(self, master):
        self.tree = ttk.Treeview(master)
        self.tree["columns"] = ("one", "two", "three")
        self.tree.column("#0", width=270, minwidth=270, stretch=tk.YES)
        self.tree.column("one", width=150, minwidth=150, stretch=tk.YES)
        self.tree.column("two", width=150, minwidth=150)
        self.tree.column("three", width=80, minwidth=50, stretch=tk.YES)

        self.tree.heading("#0", text="Name", anchor=tk.W)
        self.tree.heading("one", text="Date modified", anchor=tk.W)
        self.tree.heading("two", text="Type", anchor=tk.W)
        self.tree.heading("three", text="Size", anchor=tk.W)
        self.tree.pack(side=tk.TOP, fill=tk.X)

        self.tree.bind("<Button-3>", self.do_popup)

    def do_popup(self, event):
        iid = self.tree.identify_row(event.y)
        try:
            if iid:
                self.tree.selection_set(iid)
                self.popup.tk_popup(event.x_root + 50, event.y_root, 0)
                selected_item = self.tree.item(iid)
                self.to_download = selected_item['text']
                print 'clicked on', self.tree.item(iid)
        finally:
            self.popup.grab_release()

    # opens a browser directory to save download folder/file
    def browse_directory(self):
        dir_name = tkFileDialog.askdirectory()
        if dir_name:
            self.download_location = dir_name
            self.DOWNLOAD(self.to_download)
            print dir_name

    def AUTHENTICATE(self):
        username = tkSimpleDialog.askstring("Username", "Enter username")
        password = tkSimpleDialog.askstring("Password", "Enter password")
        self.fsc.AUTHENTICATE(username, password)

    def authenticated(self):
        self.menubar.entryconfig("Actions", state="normal")

    def LIST(self):
        print 'in LIST CLICK'
        self.fsc.LIST()

    def MKDIR(self):
        print 'in MKDIR Gui'
        dir_name = tkSimpleDialog.askstring("Name of directory", "Enter directory name")
        if dir_name:
            self.fsc.MKDIR(dir_name)

    def DOWNLOAD(self, file_dir_name):
        print file_dir_name
        self.fsc.DOWNLOAD(file_dir_name)

    def run(self):
        self.fsc.start()

    def reconstruct_tree(self, files_dirs):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fd in files_dirs:
            fd_size = str(fd["size"]) + " Bytes"
            if fd["type"] == 'dir':
                self.tree.insert("", 2, iid=fd['name'], text=fd['name'], values=("23-Jun-17 11:25", "Directory", fd_size))
            else:
                self.tree.insert("", 2, iid=fd['name'], text=fd['name'], values=("23-Jun-17 11:25", "File", fd_size))
