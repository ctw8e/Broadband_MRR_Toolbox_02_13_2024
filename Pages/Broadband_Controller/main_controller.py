"""
Author: Channing West
Changelog: 11/14/2020

"""

import tkinter.ttk as ttk
from Pages.PageFormat import PageFormat
from Pages.Broadband_Controller.Scope_Controller import ScopeController as scopecont
from Pages.Broadband_Controller.AWG_Controller import AWGController as awgcont
from Pages.Broadband_Controller.Temp_Controller import TempController as tempcont
from Pages.Broadband_Controller.Auto_Controller import AutoController as autocont


class BroadbandController(ttk.Frame):
    """
    Generate GUI to control the 2-8 GHz and 6-18 GHz broadband spectrometer in the Pate lab at UVA.

    GUI consists of 5 sections:
        1.  Tektronix DPO 73304B
        2.  Tektronix AWG 7133
        3.  Omega CN7XX temperature controllers
        4.  Write linear frequency sweeps for the AWG.
        5.  Automating spectral collection using DPO, AWG, and temperature controllers.

        Sections 1, 2, 3, and 4 can be used idependently to control a single instrument component. 
        Section 5 requires all 1, 2, and 3 individual components must be discoverable. Program 
        will not function if unable to connect to any component, and program will break if a 
        connection error is experienced during spectral collection. I aim to fix this problem in 
        a future version.

    Whenever possible, this program suite runs calculations and hardware monitoring processes 
    on dedicated threads so the main thread is reserved for GUI operations like navigating between 
    windows and allowing the user to press other buttons. Without threading, the program
    becomes unresponsive until the process is complete. Monitoring different components of the
    broadband instrument simultaneously requires either each component be on a dedicated thread, 
    or each component be contacted serially, with the connection terminated after each query.

    Parameters:
        master (ttk.Frame):
            master frame
        controller (RotSpec()):
    """

    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.page.left_click()

        v = 'vertical'
        h = 'horizontal'
        x5y3ns_rspan6 = {'rowspan':6, 'sticky':'ns', 'padx':5, 'pady':3}
        h14bL_l = {'justify':'left', 'style':'h14b.TLabel'}

        self.page_title = "Broadband MRR Toolbox - Broadband Controller"

        header = ttk.Label(self.frame, text='Broadband Controller', **h14bL_l)
        header.grid(row=0, column=1, columnspan=1, sticky='ew', padx=4, pady=3)

        ttk.Separator(self.frame, orient=v).grid(row=1, column=2, **x5y3ns_rspan6)
        ttk.Separator(self.frame, orient=h).grid(row=2, column=3, sticky='ew', padx=4, pady=10)
        ttk.Separator(self.frame, orient=h).grid(row=4, column=3, sticky='ew', padx=4, pady=3)
        self.col_1_F = ttk.Frame(self.frame)
        self.col_1_F.grid(row=3, column=1, padx=4, pady=3, sticky='n')
        ttk.Separator(self.col_1_F, orient=h).grid(row=1, column=0, sticky='ew', padx=4, pady=15)
        self.scope_ = scopecont(self.col_1_F)
        self.temp_ = tempcont(self.col_1_F)

        ttk.Separator(self.frame, orient=v).grid(row=1, column=0, **x5y3ns_rspan6)
        ttk.Separator(self.frame, orient=h).grid(row=2, column=1, sticky='ew', padx=4, pady=10)
        ttk.Separator(self.frame, orient=h).grid(row=4, column=1, sticky='ew', padx=4, pady=3)
        self.col_2_F = ttk.Frame(self.frame)
        self.col_2_F.grid(row=3, column=3, padx=4, pady=3, sticky='n')
        self.awg_ = awgcont(self.col_2_F)

        ttk.Separator(self.frame, orient=v).grid(row=1, column=4, **x5y3ns_rspan6)
        ttk.Separator(self.frame, orient=h).grid(row=2, column=5, sticky='ew', padx=4, pady=10)
        ttk.Separator(self.frame, orient=h).grid(row=4, column=5, sticky='ew', padx=4, pady=3)
        self.col_3_F = ttk.Frame(self.frame)
        self.col_3_F.grid(row=3, column=5, padx=4, pady=3, sticky='n')
        ttk.Separator(self.frame, orient='vertical').grid(row=1, column=6, **x5y3ns_rspan6)
        self.auto_ = autocont(self.col_3_F, self.scope_, self.awg_, self.temp_)

    # def canvas_focus(self, event):
    #     self.page.canvas.bind_all("<MouseWheel>", self.canvas_mousewheel)
    #
    # def canvas_mousewheel(self, event):
    #     self.page.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
