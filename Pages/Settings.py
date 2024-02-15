"""
Author: Channing West
Changelog: 8/22/2022
"""
import pickle
import tkinter as tk
import tkinter.ttk as ttk
from Pages.PageFormat import PageFormat
import Pages.PageFormat as page_funcs


class Settings(ttk.Frame):
    """
    Generate GUI. Program settings.
    """
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Settings"
        self.controller = controller
        l = tk.LEFT
        c = tk.CENTER
        h14bL = 'h14b.TLabel'
        h8bL = 'h8b.TLabel'
        x2y2w = {'padx': 2, 'pady': 2, 'sticky': 'w'}
        x2y2e = {'padx': 2, 'pady': 2, 'sticky': 'e'}
        x2y2ew = {'padx': 2, 'pady': 2, 'sticky': 'ew'}
        f1 = ttk.Frame(self.frame)
        f1.grid(row=0, column=0)

        self.width = tk.IntVar()
        self.height = tk.IntVar()
        self.pickett_dir = tk.StringVar()
        self.picker = tk.IntVar()
        settings_L = ttk.Label(f1, justify=l, style=h14bL, text='Settings')
        width_L = ttk.Label(f1, justify=l, style=h8bL, text='Width (pixels):  ')
        height_L = ttk.Label(f1, justify=l, style=h8bL, text='Height (pixels):  ')
        dir_L = ttk.Label(f1, justify=l, style=h8bL, text='Pickett Directory:  ')
        picker_L = ttk.Label(
            f1, justify=l, style=h8bL, text='Plot Selection Sensitivity (pixels):  ')
        width_E = ttk.Entry(f1, textvariable=self.width, justify=c)
        height_E = ttk.Entry(f1, textvariable=self.height, justify=c)
        dir_E = ttk.Entry(f1, textvariable=self.pickett_dir, justify=c)
        picker_E = ttk.Entry(f1, textvariable=self.picker, justify=c)
        browse_B = ttk.Button(
            f1, text="Browse", style='h8b.TButton',
            command=lambda: page_funcs.write_directory(dir_E))
        settings_L.grid(row=0, column=0, **x2y2w)
        width_L.grid(row=1, column=0, **x2y2e)
        height_L.grid(row=2, column=0, **x2y2e)
        dir_L.grid(row=3, column=0, **x2y2e)
        picker_L.grid(row=4, column=0, **x2y2e)
        width_E.grid(row=1, column=1, **x2y2ew)
        height_E.grid(row=2, column=1, **x2y2ew)
        dir_E.grid(row=3, column=1, **x2y2ew)
        browse_B.grid(row=3, column=2, **x2y2ew)
        picker_E.grid(row=4, column=1, **x2y2ew)
        self.attr_dict = {
            'width': self.width.get(),
            'height': self.height.get(),
            'pickett_dir': self.pickett_dir.get(),
            'picker': self.picker.get()}
        self.load()

    def width_(self, w=None):
        """GUI width."""
        if w is None:
            w = self.width.get()
            return w
        else:
            self.width.set(w)

    def height_(self, h=None):
        """GUI height."""
        if h is None:
            h = self.height.get()
            return h
        else:
            self.height.set(h)

    def pickett_dir_(self, d=None):
        """Location of SPCAT, SPFIT, and PIFORM."""
        if d is None:
            d = self.pickett_dir.get()
            return d
        else:
            self.pickett_dir.set(d)

    def picker_(self, p=None):
        """Matplotlib data point selection sensitivity (pixels)."""
        if p is None:
            p = self.picker.get()
            return p
        else:
            self.picker.set(p)

    def save(self):
        """Save settings in *.pickle"""
        d = {'width': self.width.get(), 'height': self.height.get(),
             'pickett_dir': self.pickett_dir.get(), 'picker': self.picker.get()}
        with open('settings.pickle', 'wb') as f:
            pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        """Load settings from *.pickle"""
        with open('settings.pickle', 'rb') as f:
            d = pickle.load(f, encoding='bytes')
        self.width_(w=d['width'])
        self.height_(h=d['height'])
        self.pickett_dir_(d=d['pickett_dir'])
        self.picker_(p=d['picker'])


def load():
    """Load settings from *.pickle"""
    with open('settings.pickle', 'rb') as f:
        d = pickle.load(f, encoding='bytes')
    return d


def save(d):
    """Save settings in *.pickle"""
    with open('settings.pickle', 'wb') as f:
        pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)
