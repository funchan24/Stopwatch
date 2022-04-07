#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

# Author: funchan
# CreateDate: 2022-01-26 23:20:06
# Description: 计时器

import re
import time
import platform

import simpleaudio as sa
from pynput import keyboard, mouse
from ttkbootstrap import *
from ttkbootstrap.constants import *

from dirs import *
from gui import GUI

time_start = 0


class App(GUI):

    def __init__(self,
                 title="ttkbootstrap",
                 base_size=8,
                 themename="litera",
                 iconphoto='',
                 size=None,
                 position=None,
                 minsize=None,
                 maxsize=None,
                 resizable=None,
                 hdpi=True,
                 scaling=None,
                 transient=None,
                 overrideredirect=False,
                 alpha=0.95):
        super().__init__(title, base_size, themename, iconphoto, size,
                         position, minsize, maxsize, resizable, hdpi, scaling,
                         transient, overrideredirect, alpha)

        self.to_top()
        self.attributes('-topmost', 1)
        self.hide_widget(0)

        self.bind_mouse()
        self.bind_key()
        self.time_text_label.bind('<ButtonPress-1>', self.start_move)
        self.time_text_label.bind('<ButtonRelease-1>', self.stop_move)
        self.time_text_label.bind('<B1-Motion>', self.on_motion)

        self.after(10, self.update_status)
        self.signal = 'ready'

    def add_widget(self):
        self.time_text_var = StringVar()
        self.time_text_var.set('00:00:00')
        self.time_number_var = IntVar()
        self.time_number_var.set(5)
        self.play_sound_var = BooleanVar()
        self.play_sound_var.set(False)
        self.count_down_var = BooleanVar()
        self.count_down_var.set(True)

        self.time_text_label = Label(
            self,
            textvariable=self.time_text_var,
            font=f'微软雅黑 {int(2.5 * self.base_size)} bold',
            width=int(0.75 * self.base_size),
            anchor=CENTER)
        self.time_number_scale = Scale(self,
                                       from_=1,
                                       to=60,
                                       variable=self.time_number_var)
        self.count_down_checkbutton = Checkbutton(self,
                                                  text='倒数',
                                                  variable=self.count_down_var)
        self.play_sound_checkbutton = Checkbutton(self,
                                                  text='声音',
                                                  variable=self.play_sound_var)
        self.start_button = Button(self, text='开始F5', command=self.start)
        self.reset_button = Button(self,
                                   text='重置F6',
                                   command=self._reset,
                                   bootstyle=SUCCESS)

        self.widgets_list = [[self.time_text_label, '-'],
                             [self.time_number_scale, '-'],
                             [
                                 self.count_down_checkbutton,
                                 self.play_sound_checkbutton
                             ], [self.start_button, self.reset_button]]

        self.grid_widget(self.widgets_list, self,
                         (self.base_size, self.base_size, 0, 0))

    def to_top(self) -> None:
        self.withdraw()
        self.update()
        w_width = self.winfo_width()
        s_width = self.winfo_screenwidth()
        pos_x = (s_width - w_width) // 2
        pos_y = 0
        self.geometry(f'+{pos_x}+{pos_y}')
        self.deiconify()

    @GUI.multi_thread
    def bind_mouse(self):

        def on_move(x, y):
            pos_str = self.geometry()
            w_width, w_height, pos_x, pos_y = [
                int(i) for i in re.split('[x+]', pos_str)
            ]

            if pos_x <= x <= pos_x + w_width and pos_y <= y <= pos_y + w_height:
                self.show_widget(0)
            else:
                self.hide_widget(0)

        def on_click(x, y, button, is_press):
            pass

        def on_scroll(x, y, dx, dy):
            pass

        with mouse.Listener(on_move=on_move,
                            on_click=on_click,
                            on_scroll=on_scroll) as listener:
            listener.join()

    @GUI.multi_thread
    def bind_key(self):

        def on_press(key):
            global time_start

            if self.shown:
                if key == keyboard.Key.alt:
                    time_start = time.time()
                if key == keyboard.Key.f4 and time.time() - time_start < 0.5:
                    self.quit()

        def on_release(key):
            if key == keyboard.Key.f5:
                self.start()
            if key == keyboard.Key.f6:
                self._reset()
            if self.shown:
                if key == keyboard.Key.esc:
                    self.quit()

        with keyboard.Listener(on_press=on_press,
                               on_release=on_release) as listener:
            listener.join()

    def show_widget(self, event):
        self.attributes('-alpha', 1)
        for _widgets in self.widgets_list[1:]:
            for w in _widgets:
                if isinstance(w, (TK_WIDGETS, TTK_WIDGETS)):
                    w.grid()
        self.shown = True

    def hide_widget(self, event):
        self.attributes('-alpha', 0.8)
        for _widgets in self.widgets_list[1:]:
            for w in _widgets:
                if isinstance(w, (TK_WIDGETS, TTK_WIDGETS)):
                    w.grid_remove()
        self.shown = False

    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def stop_move(self, event):
        self.start_x = None
        self.start_y = None

    def on_motion(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        x = max(self.winfo_x() + dx, 0)
        y = max(self.winfo_y() + dy, 0)
        w_width = self.winfo_width()
        w_height = self.winfo_width()
        s_width = self.winfo_screenwidth()
        s_height = self.winfo_screenheight()
        x = min(x, s_width - w_width)
        baseline = 1.33
        scaling = self.tk.call('tk', 'scaling')
        factor = scaling / baseline
        y = min(y, int(s_height - w_height - 50 * factor))
        self.geometry(f'+{x}+{y}')

    def update_status(self):
        if self.signal == 'ready':
            minutes = self.time_number_var.get()
            self.time_text_var.set(f'{str(minutes).zfill(2)}:00')
            self.total_count = self.time_number_var.get() * 60
            self.start_count = 0
            self.enable_widget()
        else:
            self.disable_widget()
        self.after(100, self.update_status)

    def enable_widget(self):
        self.time_number_scale.config(state=NORMAL)
        self.count_down_checkbutton.config(state=NORMAL)
        self.play_sound_checkbutton.config(state=NORMAL)

    def disable_widget(self):
        self.time_number_scale.config(state=DISABLED)
        self.count_down_checkbutton.config(state=DISABLED)
        self.play_sound_checkbutton.config(state=DISABLED)

    def start(self):
        if self.signal == 'start':
            self.signal = 'pause'
            self.start_button.config(text='开始F5', bootstyle=(DEFAULT, OUTLINE))
            self._pause()
        else:
            self.signal = 'start'
            self.start_button.config(text='暂停F5', bootstyle=(WARNING, OUTLINE))
            self._start()

    @staticmethod
    @GUI.multi_thread
    def beep():
        wave_path = str(res_dir / 'second.wav')
        wave_obj = sa.WaveObject.from_wave_file(wave_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def _start(self):
        mm = ss = 0
        if self.count_down_var.get():
            if self.total_count >= 0:
                mm = self.total_count // 60
                ss = self.total_count - mm * 60
                count_down = self.total_count

                if count_down < 10:
                    self.time_text_label.config(bootstyle=DANGER)
                    if self.play_sound_var.get():
                        self.beep()
                else:
                    self.time_text_label.config(bootstyle=DEFAULT)

                self.total_count -= 1
                self.time_text_var.set(f'{mm:02d}:{ss:02d}')
                self.after_id = self.after(1000, self._start)
            else:
                self._reset()

        else:
            if self.start_count <= self.total_count:
                mm = self.start_count // 60
                ss = self.start_count - mm * 60
                count_down = self.total_count - self.start_count

                if count_down < 10:
                    self.time_text_label.config(bootstyle=DANGER)
                    if self.play_sound_var.get():
                        self.beep()
                else:
                    self.time_text_label.config(bootstyle=DEFAULT)

                self.start_count += 1
                self.time_text_var.set(f'{mm:02d}:{ss:02d}')
                self.after_id = self.after(1000, self._start)
            else:
                self._reset()

    def _pause(self):
        self.after_cancel(self.after_id)

    def _reset(self):
        self.after_cancel(self.after_id)
        self.signal = 'ready'
        self.time_text_label.config(bootstyle=DEFAULT)
        self.start_button.config(text='开始F5', bootstyle=DEFAULT)


def main():
    if platform.system() == 'Windows':
        iconphoto = str(res_dir / 'main_32.png')
    if platform.system() == 'Linux':
        iconphoto = str(res_dir / 'main_256.gif')
    app = App(title='计时器',
              base_size=10,
              iconphoto=iconphoto,
              overrideredirect=True,
              alpha=1)
    app.mainloop()


if __name__ == '__main__':
    main()
