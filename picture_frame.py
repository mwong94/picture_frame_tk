import tkinter as tk
import os
import random
from PIL import Image, ImageTk


file_extensions = ['png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG']


class PictureFrame(object):
    def __init__(self, img_folder_path='/Users/max/Documents/tk/PPGG Pictures'):
        self.app = tk.Tk()
        self.app.configure(background='black')
        self.app.attributes('-fullscreen', True)

        self.pause = False

        self.image_index = 0
        self.counter = 0
        self.counter_max = 3
        self._auto_next_pic()

        self.img_folder_path = img_folder_path
        self._update_image_list()

        ## create canvas to draw on

        ## create Photo Label, bind keys, place centered and focus
        self.image = Image.open(self.images[self.image_index])
        self.image_copy = self.image.copy()
        self.photo_label = tk.Label(self.app, image=ImageTk.PhotoImage(self.image), bd=0)
        self.photo_label.bind('<KeyRelease-Left>', self._prev_pic)
        self.photo_label.bind('<KeyRelease-Right>', self._next_pic)
        self.photo_label.bind('<space>', self._pause)
        self.photo_label.bind('<Configure>', self._resize_image)
        self.photo_label.pack(fill=tk.NONE, expand=tk.YES)
        self.photo_label.focus_set()

        ## create pause icon, don't place yet
        self.pause_image = Image.open('./pause.png')
        self.pause_label = tk.Label(self.app, image=ImageTk.PhotoImage(self.pause_image), bd=0)
        self.pause_label.place(x=0, y=0)

        ## preload next and previous
        self.image_index_next = (self.image_index+1)%len(self.images)
        self.image_index_prev = (self.image_index-1)%len(self.images)
        self.image_next = Image.open(self.images[self.image_index_next])
        self.image_prev = Image.open(self.images[self.image_index_prev])


    def _auto_next_pic(self):
        print('_auto_next_pic... ', end='')
        if not self.pause and self.counter >= self.counter_max-1: # change pic
            print('next pic')
            self._next_pic(event=None)
            self.counter = 0
        elif not self.pause: # increment and queue next check
            print('continue')
            self.counter += 1
        else:
            print('paused')
        self.app.after(1000, self._auto_next_pic)


    def _update_image_list(self):
        print('updating image list')
        self.images = os.listdir(self.img_folder_path)
        self.images = [f'{self.img_folder_path}/{x}' for x in self.images if x.split('.')[-1] in file_extensions]
        self.images.sort()
        self.app.after(60*1000, self._update_image_list)


    def _resize_image(self, event):
        max_width = self.app.winfo_width()
        max_height = self.app.winfo_height()

        orig_width = self.image_copy.width
        orig_height = self.image_copy.height

        if orig_width/orig_height > max_width/max_height: # if wide
            new_width = max_width
            new_height = int(max_width/orig_width*orig_height)
        elif orig_width/orig_height < max_width/max_height: # if tall
            new_height = max_height
            new_width = int(max_height/orig_height*orig_width)
        else:
            new_width = max_width
            new_height = max_height
        
        resized_image = self.image_copy.resize((new_width, new_height))
        resized_photo = ImageTk.PhotoImage(resized_image)
        self.photo_label.configure(image=resized_photo)
        self.photo_label.image = resized_photo
        self.image = resized_image


    def _update_pic(self, event, type):
        if type == 'next':
            new_photo = ImageTk.PhotoImage(self.image_next)
            self.photo_label.configure(image=new_photo)
            self.photo_label.image = new_photo

            self.image_prev = self.image
            self.image = self.image_next
            self.image_next = Image.open(self.images[self.image_index_next])
        elif type == 'prev':
            new_photo = ImageTk.PhotoImage(self.image_prev)
            self.photo_label.configure(image=new_photo)
            self.photo_label.image = new_photo

            self.image_next = self.image
            self.image = self.image_prev
            self.image_prev = Image.open(self.images[self.image_index_prev])

        self.image_copy = self.image.copy()
        self._resize_image(event)


    def _prev_pic(self, event):
        if event: self.counter = 0 # if actual keypress, reset counter
        self.image_index = (self.image_index-1)%len(self.images)
        self.image_index_next = (self.image_index+1)%len(self.images)
        self.image_index_prev = (self.image_index-1)%len(self.images)
                
        self._update_pic(event, 'prev')
    

    def _next_pic(self, event):
        if event: self.counter = 0 # if actual keypress, reset counter
        self.image_index = (self.image_index+1)%len(self.images)
        self.image_index_next = (self.image_index+1)%len(self.images)
        self.image_index_prev = (self.image_index-1)%len(self.images)

        self._update_pic(event, 'next')


    def _pause(self, event):
        self.pause = False if self.pause else True




    def loop(self):
        self.app.mainloop()


def main():
    app = PictureFrame()
    app.loop()


if __name__ == '__main__':
    main()