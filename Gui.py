import Tkinter as tk
import ttk
from threading import *
from client.FileSharingClient import Client
import os

# tree.insert(folder1, "end", text="photo1.png", values=("23-Jun-17 11:28","PNG file","2.6 KB"))
# tree.insert(folder1, "end", text="photo2.png", values=("23-Jun-17 11:29","PNG file","3.2 KB"))
# tree.insert(folder1, "end", text="photo3.png", values=("23-Jun-17 11:30","PNG file","3.1 KB"))
HOST = '127.0.0.1'
PORT = 1337
DATA_PORT = 1338


class App(Thread):
    def __init__(self, master):
        Thread.__init__(self)
        self.master = master
        self.tree=ttk.Treeview(master)
        self.text = 'initial text'

        self.tree["columns"]=("one","two","three")
        self.tree.column("#0", width=270, minwidth=270, stretch=tk.NO)
        self.tree.column("one", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("two", width=400, minwidth=200)
        self.tree.column("three", width=80, minwidth=50, stretch=tk.NO)

        self.tree.heading("#0",text="Name",anchor=tk.W)
        self.tree.heading("one", text="Date modified",anchor=tk.W)
        self.tree.heading("two", text="Type",anchor=tk.W)
        self.tree.heading("three", text="Size",anchor=tk.W)

        #Level 1
#         folder1 = self.tree.insert("", 1, iid="tes1", text="Folder 1", values=("23-Jun-17 11:05","File folder",""))
#         self.tree.insert("", 2,  iid="tes2", text="text_file.txt", values=("23-Jun-17 11:25","TXT file","1 KB"))
        self.tree.bind('<Double-1>', self.OnDoubleClick)
        self.tree.pack(side=tk.TOP,fill=tk.X)

    def OnDoubleClick(self, e):
        curItem = self.tree.focus()
        print self.tree.item(curItem)
        print 'after'
        print self.text
        if self.tree.item(curItem)['values'][1] == u"Directory":
            commands = {"cmd": "CD", "dir":self.tree.item(curItem)['text']}
            print(commands)
            self.fsc.GUIHandle(commands)

    def run(self):
        print 'in thread'
        print 'before'
        print self.text
        self.fsc = Client((HOST, PORT), DATA_PORT, self)
        self.fsc.start()

    def reconstruct_tree(self, files_dirs):
        num = 2
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        self.tree.insert("", 1, iid="..", text="..", values=(" ", "Directory", " "))
        for fd in files_dirs:
            print(fd)
            if fd['type'] == "file":
                extIndex = fd['name'].rfind('.')
                fileType = fd['name'][extIndex+1:]
                fileType = fileType.upper()
                self.tree.insert("", num, iid=fd['name'], text=fd['name'], values=("23-Jun-17 11:25", fileType, fd['size'] + " B"))
            elif fd['type'] == "dir":
                self.tree.insert("", num, iid=fd['name'], text=fd['name'], values=("23-Jun-17 11:25", "Directory", "1 KB"))
            else:
                self.tree.insert("", num, iid=fd['name'], text=fd['name'], values=("unknown", "UNKNOWN file", "1 KB"))
            num += 1