import tkinter as tk
import os
from PIL import Image, ImageTk
import json
from pathlib import Path


file_extensions = ['png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG']


class PictureFrame(object):
    def __init__(self, config_file=f'{Path.home()}/.picture_frame.json'):
        img_folder_path, self.image_index, self.counter, self.counter_max, font_size, pause_size, x, y = self._read_config_file(config_file)

        self.app = tk.Tk()
        self.app.attributes('-fullscreen', True)
        self.app.geometry(f'{x}x{y}')

        self.pause = False
        self._auto_next_pic()

        self.img_folder_path = img_folder_path
        self._update_image_list()

        ## create canvas to draw on
        self.canvas = tk.Canvas(
            self.app,
            bg='black',
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.update()

        ## create Photo Label, bind keys, place centered and focus
        self.image = Image.open(self.images[self.image_index])
        self.image_copy = self.image.copy()
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas_image = self.canvas.create_image(
            self.canvas.winfo_width()/2,
            self.canvas.winfo_height()/2,
            image=self.photo_image,
            anchor=tk.CENTER
        )
        self.canvas.bind('<KeyRelease-Left>', self._prev_pic)
        self.canvas.bind('<KeyRelease-Right>', self._next_pic)
        self.canvas.bind('<space>', self._pause)
        self.canvas.bind('<Configure>', self._resize)
        self.canvas.focus_set()
        self.first_resize = True

        ## create pause icon, don't place yet
        self.pause_image = ImageTk.PhotoImage(image=Image.open('./pause.png').resize((pause_size, pause_size)))
        self.canvas_pause = self.canvas.create_image(
            1000,1000,
            image=self.pause_image,
            state=tk.HIDDEN,
            anchor=tk.CENTER
        )

        ## photo number label
        self.number_label = self.canvas.create_text(
            0,
            0,
            text=f'{self.image_index}/{len(self.images)}',
            fill='white',
            font=('Helvetica', font_size, 'bold'),
            anchor=tk.SE
        )

        self._resize(event=None)

        ## preload next and previous
        self.image_index_next = (self.image_index+1)%len(self.images)
        self.image_index_prev = (self.image_index-1)%len(self.images)
        self.image_next = Image.open(self.images[self.image_index_next])
        self.image_prev = Image.open(self.images[self.image_index_prev])


    def _read_config_file(self, config_file):
        with open(config_file, 'r') as f:
            conf = json.load(f)
        img_folder_path = conf['img_folder_path']
        image_index = conf['image_index']
        counter = conf['counter']
        counter_max = conf['counter_max']
        font_size = conf['font_size']
        pause_size = conf['pause_size']
        x = conf['x']
        y = conf['y']

        return (img_folder_path, image_index, counter, counter_max, font_size, pause_size, x, y)


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


    def _resize(self, event):
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
        
        resized_image = self.image_copy.resize((new_width, new_height)) #, Image.ANTIALIAS)
        resized_photo = ImageTk.PhotoImage(resized_image)
        self.photo_image = resized_photo
        self.canvas.itemconfig(
            self.canvas_image,
            image=self.photo_image
        )

        ## move image
        img_x, img_y = self.canvas.coords(self.canvas_image)
        canvas_center_x = self.canvas.winfo_width()/2
        canvas_center_y = self.canvas.winfo_height()/2

        move_x = round((canvas_center_x - img_x) / 2, 2)
        move_y = round((canvas_center_y - img_y) / 2, 2)
        
        if not self.first_resize: self.canvas.move(self.canvas_image, move_x, move_y)
        self.first_resize = False

        ## move pause image
        pause_x, pause_y = self.canvas.coords(self.canvas_pause)
        target_x = 75
        target_y = self.canvas.winfo_height() - target_x
        
        move_x = round((target_x - pause_x), 2)
        move_y = round((target_y - pause_y), 2)

        self.canvas.move(self.canvas_pause, move_x, move_y)

        ## move numbers
        number_x, number_y = self.canvas.coords(self.number_label)
        target_x = self.canvas.winfo_width() - 20
        target_y = self.canvas.winfo_height() - 20
        
        move_x = round((target_x - number_x), 2)
        move_y = round((target_y - number_y), 2)

        self.canvas.move(self.number_label, move_x, move_y)


        self.image = resized_image


    def _update_pic(self, event, type):
        if type == 'next':
            new_photo = ImageTk.PhotoImage(self.image_next)

            self.image_prev = self.image_copy
            self.image = self.image_next
            self.image_next = Image.open(self.images[self.image_index_next])
        elif type == 'prev':
            new_photo = ImageTk.PhotoImage(self.image_prev)

            self.image_next = self.image_copy
            self.image = self.image_prev
            self.image_prev = Image.open(self.images[self.image_index_prev])

        self.canvas.itemconfig(
            self.canvas_image,
            image=new_photo
        )

        self.canvas.itemconfig(
            self.number_label,
            text=f'{self.image_index}/{len(self.images)}'
        )

        self.image_copy = self.image.copy()
        print('resizing???')
        self._resize(event)


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
        new_state = tk.NORMAL if self.pause else tk.HIDDEN
        self.canvas.itemconfigure(self.canvas_pause, state=new_state)



    def loop(self):
        self.app.mainloop()


def main():
    app = PictureFrame()
    app.loop()


if __name__ == '__main__':
    main()