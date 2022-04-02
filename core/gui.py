#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

import functools
from threading import Thread
from tkinter import Misc
from typing import List, Tuple, Union

from ttkbootstrap import *
from ttkbootstrap.constants import *


class GUI(Window):

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

        super().__init__(title=title,
                         themename=themename,
                         iconphoto=iconphoto,
                         size=size,
                         position=position,
                         minsize=minsize,
                         maxsize=maxsize,
                         resizable=resizable,
                         hdpi=hdpi,
                         scaling=scaling,
                         transient=transient,
                         overrideredirect=overrideredirect,
                         alpha=alpha)

        self.withdraw()
        self.set_global_font(size=10)

        self.base_size = base_size
        self.add_widget()

        self.center_horizontally(self)

        self.deiconify()
        self.before_work()

        # self.bind('<Return>', self._start_work)
        self.protocol('WM_DELETE_WINDOW', self.after_work)

    def add_widget(self):
        """
        "-": means columnspan
        int n: means a blank Label, width = n
        """
        widgets_list = [[1] * 9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                if i >= j:
                    widgets_list[i][j] = Label(
                        self,
                        text=f'{j + 1}*{i + 1}={(i + 1) * (j + 1)}',
                        anchor=CENTER,
                        bootstyle=(SUCCESS, INVERSE))

        self.grid_widget(widgets_list, self, self.base_size)

    @staticmethod
    def grid_widget(widgets_list: List[List[Union[Misc, str, int]]],
                    master: Misc,
                    padding: Union[int, Tuple[int, int, int, int]] = 0,
                    anchor: ANCHOR = CENTER,
                    sticky=NSEW) -> None:

        master.grid_anchor(anchor)

        max_column = len(widgets_list[0])
        assert all([len(_widgets) == max_column for _widgets in widgets_list
                    ]), 'the elements of each row are not equal'

        if isinstance(padding, int):
            padx = pady = ipadx = ipady = padding
        elif isinstance(padding, tuple):
            padx, pady, ipadx, ipady = padding
        else:
            raise TypeError('wrong parameter type')

        for row, _widgets in enumerate(widgets_list):
            for column, widget in enumerate(_widgets):
                if widget != '-':
                    columnspan = 1
                    for i in range(column + 1, max_column):
                        if _widgets[i] != '-':
                            break
                        columnspan += 1

                    if isinstance(widget, int):
                        widget = Label(master, width=widget)

                    try:
                        widget.grid(row=row,
                                    column=column,
                                    columnspan=columnspan,
                                    padx=padx,
                                    pady=pady,
                                    ipadx=ipadx,
                                    ipady=ipady,
                                    sticky=sticky)
                    except AttributeError:
                        raise AttributeError(
                            f'''self.widgets_list can only contain "widget", "-" and int, got a "{widget}".'''
                        )

    def before_work(self):
        pass

    def start_work(self):
        pass

    def _start_work(self, _event):
        return self.start_work()

    def after_work(self):
        self.destroy()

    @staticmethod
    def multi_thread(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            thread = Thread(target=func, args=args, kwargs=kwargs)
            thread.setDaemon(True)
            thread.start()

        return wrapper

    @staticmethod
    def set_global_font(**font_options) -> None:
        default_font = font.nametofont('TkDefaultFont')
        text_font = font.nametofont('TkTextFont')
        fixed_font = font.nametofont('TkFixedFont')
        fonts = (default_font, text_font, fixed_font)

        for k, v in font_options.items():
            for _font in fonts:
                _font[k] = v

    def center_horizontally(self, _window: Union[Window, Toplevel]) -> None:
        _window.update()
        w_width = _window.winfo_width()
        w_height = _window.winfo_height()
        s_width = self.winfo_screenwidth()
        s_height = self.winfo_screenheight()
        xpos = (s_width - w_width) // 2
        ypos = int((s_height - w_height) * 0.382)
        _window.geometry(f'+{xpos}+{ypos}')


if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
