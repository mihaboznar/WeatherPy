import tkinter as tk
#import requests

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Weather App")
        self.master.geometry("300x300")
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        #self.hi_there = tk.Button(self)
        #self.hi_there["text"] = "Hello World\n(click me)"
        #self.hi_there["command"] = self.say_hi
        #self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="CLOSE", fg="black",
                              command=self.master.destroy)
        self.quit.pack(side="bottom", pady=10, padx=10, anchor="se")

    def say_hi(self):
        print("it works!")

root = tk.Tk()
app = Application(master=root)
app.mainloop()