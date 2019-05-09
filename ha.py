from Tkinter import *

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        self.labels = []
        self.download_buttons= []
        self.share_buttons = []
        self.files_folders = []

        master.title("File Sharing")

        m1 = PanedWindow(master)
        m1.grid(row=0, column=0)

        m2 = PanedWindow(master)
        m2.grid(row=0, column=2)
        m2.add(Label(text="HAHAH"))


        Label(m1, text="My Files").grid(row=0, column=0)

        for i in range(5):
            for j in range(4):
                self.files_folders.append(Button(m1, text="File", width=10, height=5).grid(row=i+1, column=j, padx=10, pady=10))

    def greet(self):
        print("Greetings!")

root = Tk()
root.wm_geometry("%dx%d+%d+%d" % (800, 600, 0, 0))
my_gui = MyFirstGUI(root)
root.mainloop()
