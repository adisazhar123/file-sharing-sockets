import Tkinter as tk
import ttk
from threading import *
from client.FileSharingClient import Client
import os
from Tkinter import *
import tkSimpleDialog

# tree.insert(folder1, "end", text="photo1.png", values=("23-Jun-17 11:28","PNG file","2.6 KB"))
# tree.insert(folder1, "end", text="photo2.png", values=("23-Jun-17 11:29","PNG file","3.2 KB"))
# tree.insert(folder1, "end", text="photo3.png", values=("23-Jun-17 11:30","PNG file","3.1 KB"))
HOST = '127.0.0.1'
PORT = 1337
DATA_PORT = 1338


class App(Thread):
    def __init__(self, master):
        Thread.__init__(self)
        self.fsc = Client((HOST, PORT), DATA_PORT, self)

        self.master = master
        self.menubar = Menu(master)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Create Directory", command=self.MKDIR)
        self.filemenu.add_command(label="Refresh", command=self.LIST)
        self.filemenu.add_command(label="Save")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit")
        self.menubar.add_cascade(label="Actions", menu=self.filemenu)
        self.master.config(menu=self.menubar)

        self.tree = ttk.Treeview(master)

        self.text = 'initial text'

        self.tree["columns"] = ("one", "two", "three")
        self.tree.column("#0", width=270, minwidth=270, stretch=tk.NO)
        self.tree.column("one", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("two", width=400, minwidth=200)
        self.tree.column("three", width=80, minwidth=50, stretch=tk.NO)

        self.tree.heading("#0",text="Name",anchor=tk.W)
        self.tree.heading("one", text="Date modified",anchor=tk.W)
        self.tree.heading("two", text="Type",anchor=tk.W)
        self.tree.heading("three", text="Size",anchor=tk.W)

        self.tree.pack(side=tk.TOP,fill=tk.X)

    def hahaha(self, e):
        curItem = self.tree.focus()
        print self.tree.item(curItem)
        print 'after'
        print self.text

    def LIST(self):
        print 'in LIST CLICK'
        self.fsc.LIST()

    def MKDIR(self):
        print 'in MKDIR Gui'
        dir_name = tkSimpleDialog.askstring("Name of directory", "Enter directory name")
        self.fsc.MKDIR(dir_name)

    def run(self):
        print 'in thread'
        print 'before'
        print self.text
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