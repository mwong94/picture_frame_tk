# import tkinter as tk
# from PIL import Image, ImageTk

# app = tk.Tk()

# app.configure(background='blue')
# app.geometry('500x500')

# image = Image.open('black.png')
# photo = ImageTk.PhotoImage(image)
# photo_label = tk.Label(app, image=photo, bd=0)
# photo_label.pack(fill=tk.NONE, expand=tk.YES)

# app.mainloop()

from tkinter import Tk, Frame, Canvas
from PIL import ImageTk

t = Tk()
t.title("Transparency")

canvas = Canvas(t, bg="blue", width=500, height=500)
canvas.pack()

img = ImageTk.PhotoImage(file='PPGG Pictures/210304231711998783.png')
canvas.create_image(0,0,image=img)

pause = ImageTk.PhotoImage(file="pause.png")
canvas.create_image(150, 150, image=pause)

t.mainloop()