"""
Author: Channing West
Changelog: 3/18/2019
"""

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import os
from Pages.EnantiomericExcess import EnantiomericExcess
from Pages.FFT import FFT
from Pages.FinalFit import FinalFit
from Pages.IsolateSpectra import IsolateSpectra
from Pages.PickettWriter import PickettWriter
from Pages.RotConstPredictions import RotConstPredictions
from Pages.SpecExplorer import SpecExplorer
from Pages.MixtureAnalysis import MixtureAnalysis
from Pages.Broadband_Controller.main_controller import BroadbandController
from Pages.Help.GeneralHelp import GeneralHelp
from Pages.Help.SettingsHelp import SettingsHelp
from Pages.Help.EnantiomericExcess import eeHelp
from Pages.Help.FFT import fftHelp
from Pages.Help.FinalFit import finalFitHelp
from Pages.Help.IsolateSpectra import isolateHelp
from Pages.Help.MixtureAnalysis import maHelp
from Pages.Help.PickettWriter import pickettWriterHelp
from Pages.Help.RotConstPredictions import rcpHelp
from Pages.Help.SpecExplorer import specExplorerHelp
from Pages.Settings import Settings
from Pages.Settings import save as settings_save
from Pages.Settings import load as settings_load
from Navigator import Navigator
import testing
# import time
# import numpy as np
import sv_ttk
import temp.t as r


class RotSpec(tk.Tk):
    """
    Run Broadband MRR Toolbox GUI.

    Methods:
        show_frame(cont)
          Raise cont tk.Frame to top of the deck, making it the visible frame.
        show_nav()
          Raise Navigator frame to the top of the deck.
        client_exit()
            Close the program
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_title("Broadband MRR Toolbox")
        self.root.protocol("WM_DELETE_WINDOW", self.client_exit)
        self.dir = os.getcwd()
        style = ThemedStyle(self.root)
        style.set_theme('radiance')
        try:
            settings = settings_load()
            self.width = settings['width']
            self.height = settings['height']
            self.pickett_dir = settings['pickett_dir']
            self.picker = settings['picker']
        except FileNotFoundError:
            self.width = 1625
            self.height = 1010
            self.pickett_dir = 'C:\\ROT'
            self.picker = 3
            d = {'width': self.width, 'height': self.height,
                 'pickett_dir': self.pickett_dir, 'picker': 3}
            settings_save(d)
        self.container = ttk.Frame(self.root, width=self.width, height=self.height, borderwidth=0)
        self.container.grid(row=0, column=0)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.frames = {}
        self.top_frame = None
        self.help_str = tk.StringVar()
        self.help_str.set("Help")
        root = r.root(self.dir)
        if root:
            # for F in [Navigator, Settings, MixtureAnalysis, SpecExplorer]:
            for F in [Navigator, Settings, SpecExplorer, BroadbandController, FFT,
                      PickettWriter,
                      IsolateSpectra, FinalFit, EnantiomericExcess, MixtureAnalysis,
                      RotConstPredictions, eeHelp, fftHelp, finalFitHelp, isolateHelp, maHelp,
                      pickettWriterHelp, rcpHelp, specExplorerHelp, GeneralHelp, SettingsHelp]:
                frame = F(self.container, self)
                self.frames[F] = frame
                frame.grid(row=0, column=0, sticky='nsew')
            self.show_frame(Navigator)

    @testing.collect_garbage
    def show_frame(self, cont):
        """
        Raise cont tk.Frame to the top of the deck, making it the visible frame.

        Parameters:
            cont (tk.Frame):
                GUI page accessible through the Navigator.
        """
        frame = self.frames[cont]
        frame.tkraise()
        frame.page.scroll_canvas()
        self.root.wm_title(frame.page_title)
        self.top_frame = cont

    def show_nav(self):
        """ Raise Navigator frame to the top of the deck. """
        frame = self.frames[Navigator]
        frame.tkraise()
        frame.page.scroll_canvas()
        self.root.wm_title(frame.page_title)
        self.top_frame = Navigator

    def show_settings(self):
        """ Raise Navigator frame to the top of the deck. """
        frame = self.frames[Settings]
        frame.tkraise()
        frame.page.scroll_canvas()
        self.root.wm_title(frame.page_title)
        self.top_frame = Settings

    def show_help(self):
        """ Raise module specific help frame to the top of the deck. """
        help_dict = {
            EnantiomericExcess: eeHelp, FFT: fftHelp, FinalFit: finalFitHelp,
            IsolateSpectra: isolateHelp, MixtureAnalysis: maHelp, PickettWriter: pickettWriterHelp,
            RotConstPredictions: rcpHelp, SpecExplorer: specExplorerHelp,
            eeHelp: EnantiomericExcess, fftHelp: FFT, finalFitHelp: FinalFit,
            isolateHelp: IsolateSpectra, maHelp: MixtureAnalysis, pickettWriterHelp: PickettWriter,
            rcpHelp: RotConstPredictions, specExplorerHelp: SpecExplorer, GeneralHelp: Navigator,
            Navigator: GeneralHelp, Settings: SettingsHelp, SettingsHelp: Settings}
        help_str_dict = {
            EnantiomericExcess: "Help",
            FFT: "Help",
            FinalFit: "Help",
            IsolateSpectra: "Help",
            MixtureAnalysis: "Help",
            PickettWriter: "Help",
            RotConstPredictions: "Help",
            SpecExplorer: "Help",
            eeHelp: "Return to Enantiomeric Excess",
            fftHelp: "Return to FFT",
            finalFitHelp: "Return to Final Fit",
            isolateHelp: "Return to Isolate Spectra",
            maHelp: "Return to Mixture Analysis",
            pickettWriterHelp: "Return to Pickett Writer",
            rcpHelp: "Return to Predict Rotational Constants",
            specExplorerHelp: "Return to Spectrum Explorer",
            GeneralHelp: "Return to Navigator",
            Navigator: "Help",
            Settings: "Help",
            SettingsHelp: "Return to Settings"}
        frame = self.frames[help_dict[self.top_frame]]
        frame.tkraise()
        frame.page.scroll_canvas()
        self.root.wm_title(frame.page_title)
        self.top_frame = help_dict[self.top_frame]
        self.help_str.set(help_str_dict[self.top_frame])

    def client_exit(self):
        """ Close program. """
        self.frames[Settings].save()
        self.root.destroy()


# @testing.profile_func
def main():
    app = RotSpec()
    app.root.mainloop()
    # app.client_exit()


if __name__ == "__main__":
    main()
