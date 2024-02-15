"""
Author: Channing West
Changelog: 12/5/2019
"""

import tkinter as tk
from tkinter import ttk
from Pages.FFT import FFT
from Pages.IsolateSpectra import IsolateSpectra
from Pages.PickettWriter import PickettWriter
from Pages.RotConstPredictions import RotConstPredictions
from Pages.EnantiomericExcess import EnantiomericExcess
from Pages.MixtureAnalysis import MixtureAnalysis
from Pages.FinalFit import FinalFit
from Pages.PageFormat import PageFormat
from Pages.SpecExplorer import SpecExplorer
from Pages.Broadband_Controller.main_controller import BroadbandController


class Navigator(ttk.Frame):
    """ Generate landing page for Broadband MRR Toolbox. Navigate throughout modules. """
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master, width=1625, height=1010)
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.page_title = "Broadband Molecular Rotational Resonance Toolbox - Navigator"
        self.controller = controller
        page_title = ttk.Label(
            self.frame, text='Broadband Molecular Rotational Resonance Toolbox', justify=tk.CENTER,
            style='h20b.TLabel')
        authors = ttk.Label(
            self.frame, text='Author:  Channing West', justify=tk.CENTER, style='h14b.TLabel')
        spectra_explorer_button = ttk.Button(
            self.frame, text='Spectrum Explorer', width=195, style='h10b.TButton',
            command=lambda: controller.show_frame(SpecExplorer))
        FFT_button = ttk.Button(
            self.frame, text='Fast Fourier Transform', style='h10b.TButton',
            command=lambda: controller.show_frame(FFT))
        isolator_button = ttk.Button(
            self.frame, text='Isolate Spectra', style='h10b.TButton',
            command=lambda: controller.show_frame(IsolateSpectra))
        final_fit_button = ttk.Button(
            self.frame, text='Final Fit', style='h10b.TButton',
            command=lambda: controller.show_frame(FinalFit))
        ee_button = ttk.Button(
            self.frame, text='Enantiomeric Excess', style='h10b.TButton',
            command=lambda: controller.show_frame(EnantiomericExcess))
        SPCAT_button = ttk.Button(
            self.frame, text='Pickett Writer', style='h10b.TButton',
            command=lambda: controller.show_frame(PickettWriter))
        rc_predictions = ttk.Button(
            self.frame, text='Predict Rotational Constants', style='h10b.TButton',
            command=lambda: controller.show_frame(RotConstPredictions))
        mixture_button = ttk.Button(
            self.frame, text='Mixture Analysis', style='h10b.TButton',
            command=lambda: controller.show_frame(MixtureAnalysis))
        controller_button = ttk.Button(
            self.frame, text='Broadband Controller', style='h10b.TButton',
            command=lambda: controller.show_frame(BroadbandController))
        page_title.grid(row=0, column=0, pady=40)
        authors.grid(row=1, column=0, pady=40)
        spectra_explorer_button.grid(row=3, column=0, pady=10, padx=100, sticky='nsew')
        controller_button.grid(row=4, column=0, pady=10, padx=100, sticky='nsew')
        FFT_button.grid(row=5, column=0, pady=10, padx=100, sticky='nsew')
        isolator_button.grid(row=6, column=0, pady=10, padx=100, sticky='nsew')
        rc_predictions.grid(row=7, column=0, pady=10, padx=100, sticky='nsew')
        SPCAT_button.grid(row=8, column=0, pady=10, padx=100, sticky='nsew')
        final_fit_button.grid(row=9, column=0, pady=10, padx=100, sticky='nsew')
        ee_button.grid(row=10, column=0, pady=10, padx=100, sticky='nsew')
        mixture_button.grid(row=11, column=0, pady=10, padx=100, sticky='nsew')
