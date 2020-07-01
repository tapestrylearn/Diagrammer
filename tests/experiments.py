from tkinter import *

root = Tk()
root.geometry('500x500')

c = Canvas(root, height = 500, width = 500)

l = c.create_line(5, 5, 200, 20)
o = c.create_oval(20, 20, 100, 100)

c.pack()

root.mainloop()
