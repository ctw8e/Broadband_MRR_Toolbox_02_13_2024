"""
Author: Channing West
Changelog: 12/5/2019

"""

import numpy as np
from scipy.optimize import curve_fit
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
from Pages.PageFormat import PageFormat
import Pages.PageFormat as page_funcs
import Pickett
from Spectrum import Spectrum
from TkAgg_Plotting import PlotManager
import testing


class FinalFit(ttk.Frame):
    """
    Generate GUI. Fit broadband molecular rotational spectra using the Pickett suite.

    Buttons:
        PLOT NAVIGATION BAR
            See TkAgg_Plotting.PlotManager()
        SAVE, LOAD, DEFAULTS, BACK TO NAVIGATOR, EXIT APPLICATION
            See PageFormat.py
    Sections
        1.  Inputs
            Spectrum (tk.StringVar):
                File path to spectrum.
            Cat File (tk.StringVar):
                File path to *.cat file.
            Peak pick threshold (tk.DoubleVar):
                Transition intensity minimum. Used for experimental spectra. Use PLOT and ZOOM
                to find appropriate threshold.
                Units: mV
                Default: 0.001
            Freq. match (tk.DoubleVar):
                Maximum separation between predicted and experimental line position.
                Units: MHz
                Default: 0.04
            Freq. min. (tk.IntVar):
                Lower bound.
                Units: MHz
                Default: 2000
            Freq. max. (tk.IntVar):
                Upper bound.
                Units: MHz
                Default: 8000
            Ka max. (tk.IntVar):
                Prolate limit
                Default: 6
            Dynamic range (tk.IntVar):
                Dynamic intensity cutoff with respect to the strongest predicted signal. If 100 is
                given, predicted transitions do not pass the filter unless they are at least 1/100
                the intensity of the strongest predicted transition.
                Default: 100
            Max. obs.-calc. (tk.DoubleVar):
                Maximum allowed (observed_frequency - calculated_frequency).
                Units: MHz
                Default: 0.040
            Buttons:
                BROWSE
                    Browse files with accepted file extension.
                PLOT
                    Run plot_spectrum() with appropriate spectrum. Plot and remove all other series.
        2.  Distortion Constants
            -   Two modes of quartic distortion constants attempted during initial fit.
                1.  Specific Constants:
                    Manually select specific quartic distortion constants using checkbuttons.
                2.  Constants from *.par:
                    Only use the quartic distortion constants found in *.par file.
            -   Modes for fitting QDC
                1.  Floating:
                    Constants may change to optimize fit.
                2.  Fixed:
                    Constants fixed to initial values.
            -   Constants deemed 'bad constants' by Piform are removed regardless of mode.
        3.  Run
            Buttons:
                FIT
                    Run finalfit() with parameters from GUI.
        4.  Outputs
            A, B, C, DJ, DJK, DK, dJ, dK (tk.StringVar):
                Rotational constants
            RMS (tk.StringVar):
                Root mean square deviation of fitted spectrum.
            # transitions (tk.StringVar):
                Number of lines successfully fit.
            -   Entry boxes are populated with calculated values after fit completes.
        5.  Notes
            Enter any notes you have about the sample or clustering process that could help you in
            the future. Notes are saved when SAVE button is pressed. Notes are loaded from *.pickle
            file when LOAD is pressed and file selected. Info summarizing fit displayed in Notes
            after fit.
    """
    default = {'sel_freq': 'None Selected',
               'sel_int': 'None Selected',
               'spec_path': 'None',
               'cat_path': 'None',
               'freq_min': 2000,
               'freq_max': 18000,
               'freq_match': 0.04,
               'threshold': 0.001,
               'dyn_range': 100,
               'ka_max': 6,
               'max_error': 0.040,
               'DJ_fit': 1,
               'DJK_fit': 1,
               'DK_fit': 1,
               'dJ_fit': 1,
               'dK_fit': 1,
               'A': 'None',
               'B': 'None',
               'C': 'None',
               'DJ': 'None',
               'DJK': 'None',
               'DK': 'None',
               'dJ': 'None',
               'dK': 'None',
               'rms': 'None',
               'num_trans': 'None',
               'fix_or_float': 'float',
               'dc_selector': 'specific',
               'omitted_points': 'None'}

    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.controller = controller
        self.page_title = "Broadband MRR Toolbox - Final Fit"
        self.sel_freq = tk.StringVar()
        self.sel_int = tk.StringVar()
        self.sel_freq.set(FinalFit.default['sel_freq'])
        self.sel_int.set(FinalFit.default['sel_int'])
        self.spec_path = tk.StringVar()
        self.cat_path = tk.StringVar()
        self.freq_min = tk.IntVar()
        self.freq_max = tk.IntVar()
        self.freq_match = tk.DoubleVar()
        self.threshold = tk.DoubleVar()
        self.ka_max = tk.IntVar()
        self.dyn_range = tk.IntVar()
        self.max_error = tk.DoubleVar()
        self.spec_path.set(FinalFit.default['spec_path'])
        self.cat_path.set(FinalFit.default['cat_path'])
        self.freq_min.set(FinalFit.default['freq_min'])
        self.freq_max.set(FinalFit.default['freq_max'])
        self.freq_match.set(FinalFit.default['freq_match'])
        self.threshold.set(FinalFit.default['threshold'])
        self.ka_max.set(FinalFit.default['ka_max'])
        self.dyn_range.set(FinalFit.default['dyn_range'])
        self.max_error.set(FinalFit.default['max_error'])
        self.A = tk.StringVar()
        self.B = tk.StringVar()
        self.C = tk.StringVar()
        self.DJ = tk.StringVar()
        self.DJK = tk.StringVar()
        self.DK = tk.StringVar()
        self.dJ = tk.StringVar()
        self.dK = tk.StringVar()
        self.rms = tk.StringVar()
        self.num_trans = tk.StringVar()
        self.A.set(FinalFit.default['A'])
        self.B.set(FinalFit.default['B'])
        self.C.set(FinalFit.default['C'])
        self.DJ.set(FinalFit.default['DJ'])
        self.DJK.set(FinalFit.default['DJK'])
        self.DK.set(FinalFit.default['DK'])
        self.dJ.set(FinalFit.default['DJ'])
        self.dK.set(FinalFit.default['dK'])
        self.rms.set(FinalFit.default['rms'])
        self.num_trans.set(FinalFit.default['num_trans'])
        self.DJ_fit = tk.IntVar()
        self.DJK_fit = tk.IntVar()
        self.DK_fit = tk.IntVar()
        self.dJ_fit = tk.IntVar()
        self.dK_fit = tk.IntVar()
        self.DJ_fit.set(FinalFit.default['DJ_fit'])
        self.DJK_fit.set(FinalFit.default['DJK_fit'])
        self.DK_fit.set(FinalFit.default['DK_fit'])
        self.dJ_fit.set(FinalFit.default['dJ_fit'])
        self.dK_fit.set(FinalFit.default['dK_fit'])
        self.fix_or_float = tk.StringVar()
        self.dc_selector = tk.StringVar()
        self.fix_or_float.set(FinalFit.default['fix_or_float'])
        self.dc_selector.set(FinalFit.default['dc_selector'])
        self.tk_omitted_points = tk.StringVar()
        self.frame_plot = ttk.Frame(self.frame)
        self.frame_ins_outs = ttk.Frame(self.frame)
        block_1 = ttk.Frame(self.frame_ins_outs)
        block_2 = ttk.Frame(self.frame_ins_outs)
        block_3 = ttk.Frame(self.frame_ins_outs)
        block_4 = ttk.Frame(self.frame_ins_outs)
        block_5 = ttk.Frame(self.frame_ins_outs)

        c = tk.CENTER
        h8bL_r = {'style': 'h8b.TLabel', 'justify': tk.RIGHT}
        x2y7e = {'padx': 2, 'pady': 7, 'sticky': 'e'}
        x2y2w = {'padx': 2, 'pady': 2, 'sticky': 'w'}
        x2y2e = {'padx': 2, 'pady': 2, 'sticky': 'e'}
        x2y2ew = {'padx': 2, 'pady': 2, 'sticky': 'ew'}
        # ==========================================================================================
        #                                        Block 1
        # ==========================================================================================
        selected_point_L = ttk.Label(block_1, text='Selected Point', style='h14b.TLabel')
        sel_freq_L = ttk.Label(block_1, text='x', **h8bL_r)
        sel_int_L = ttk.Label(block_1, text='y', **h8bL_r)
        sel_freq_E = ttk.Entry(block_1, textvariable=self.sel_freq, justify=c)
        sel_int_E = ttk.Entry(block_1, textvariable=self.sel_int, justify=c)
        omit_button = ttk.Button(
            block_1, text='Omit from Fit', style='h8b.TButton',
            command=lambda: page_funcs.selected_point(
                'omit', self.tk_omitted_points, self.sel_freq))
        undo_button = ttk.Button(
            block_1, text='Allow in Fit', style='h8b.TButton',
            command=lambda: page_funcs.selected_point(
                'undo', self.tk_omitted_points, self.sel_freq))
        reset_button = ttk.Button(
            block_1, text='Reset Omissions', style='h8b.TButton',
            command=lambda: page_funcs.selected_point(
                'reset', self.tk_omitted_points, self.sel_freq))
        selected_point_L.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky='ew')
        sel_freq_L.grid(row=1, column=0, padx=2, pady=2)
        sel_int_L.grid(row=2, column=0, padx=2, pady=2)
        sel_freq_E.grid(row=1, column=1, **x2y2w)
        sel_int_E.grid(row=2, column=1, **x2y2w)
        omit_button.grid(row=3, column=0, columnspan=2, padx=5, pady=0, sticky='ew')
        undo_button.grid(row=4, column=0, columnspan=2, padx=5, pady=0, sticky='ew')
        reset_button.grid(row=5, column=0, columnspan=2, padx=5, pady=0, sticky='ew')
        # ==========================================================================================
        #                                        Block 2
        # ==========================================================================================
        input_L = ttk.Label(block_2, text='Inputs', justify=c, font="Helvetica 14 bold")
        spec_path_L = ttk.Label(block_2, text='Spectrum', **h8bL_r)
        cat_path_L = ttk.Label(block_2, text='Cat file', **h8bL_r)
        threshold_L = ttk.Label(block_2, text='Peak pick\nthreshold (mV)', **h8bL_r)
        freq_match_L = ttk.Label(block_2, text='\u03BD match (MHz)', **h8bL_r)
        freq_min_L = ttk.Label(block_2, text='\u03BD min. (MHz)', **h8bL_r)
        freq_max_L = ttk.Label(block_2, text='\u03BD max. (MHz)', **h8bL_r)
        ka_max_L = ttk.Label(block_2, text='Ka max', **h8bL_r)
        dyn_range_L = ttk.Label(block_2, text='Dynamic range', **h8bL_r)
        max_error_L = ttk.Label(block_2, text='Max. obs.-calc.\n(MHz)', **h8bL_r)
        spec_path_E = ttk.Entry(block_2, textvariable=self.spec_path, justify=c)
        cat_path_E = ttk.Entry(block_2, textvariable=self.cat_path, justify=c)
        threshold_E = ttk.Entry(block_2, textvariable=self.threshold, justify=c)
        freq_match_E = ttk.Entry(block_2, textvariable=self.freq_match, justify=c)
        freq_min_E = ttk.Entry(block_2, textvariable=self.freq_min, justify=c)
        freq_max_E = ttk.Entry(block_2, textvariable=self.freq_max, justify=c)
        ka_max_E = ttk.Entry(block_2, textvariable=self.ka_max, justify=c)
        dyn_range_E = ttk.Entry(block_2, textvariable=self.dyn_range, justify=c)
        max_error_E = ttk.Entry(block_2, textvariable=self.max_error, justify=c)

        spec_path_B = ttk.Button(
            block_2, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.spec_path, eb_var=spec_path_E, ftype='ft'))
        plot_spec_B = ttk.Button(
            block_2, text='Plot', style='h8b.TButton',
            command=lambda: self.plot_spectrum(self.spec_path.get()))
        cat_path_B = ttk.Button(
            block_2, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.cat_path, eb_var=cat_path_E, ftype='cat'))
        plot_cat_B = ttk.Button(
            block_2, text='Plot', style='h8b.TButton',
            command=lambda: self.plot_cat(self.cat_path.get()))
        input_L.grid(row=0, column=0, columnspan=4, padx=2, pady=2)
        spec_path_L.grid(row=1, column=0, **x2y7e)
        cat_path_L.grid(row=2, column=0, **x2y7e)
        threshold_L.grid(row=3, column=0, **x2y7e)
        freq_match_L.grid(row=4, column=0, **x2y7e)
        freq_min_L.grid(row=5, column=0, **x2y7e)
        freq_max_L.grid(row=6, column=0, **x2y7e)
        ka_max_L.grid(row=7, column=0, **x2y7e)
        dyn_range_L.grid(row=8, column=0, **x2y7e)
        max_error_L.grid(row=9, column=0, **x2y7e)
        spec_path_E.grid(row=1, column=1, **x2y2ew)
        cat_path_E.grid(row=2, column=1, **x2y2ew)
        threshold_E.grid(row=3, column=1, **x2y2ew)
        freq_match_E.grid(row=4, column=1, **x2y2ew)
        freq_min_E.grid(row=5, column=1, **x2y2ew)
        freq_max_E.grid(row=6, column=1, **x2y2ew)
        ka_max_E.grid(row=7, column=1, **x2y2ew)
        dyn_range_E.grid(row=8, column=1, **x2y2ew)
        max_error_E.grid(row=9, column=1, **x2y2ew)
        spec_path_B.grid(row=1, column=2, padx=2, pady=0, sticky='ew')
        plot_spec_B.grid(row=1, column=3, padx=2, pady=0, sticky='ew')
        cat_path_B.grid(row=2, column=2, padx=2, pady=0, sticky='ew')
        plot_cat_B.grid(row=2, column=3, padx=2, pady=0, sticky='ew')
        # ==========================================================================================
        #                                         Block 3
        # ==========================================================================================
        dc_L = ttk.Label(block_3, text='Distortion Constants', justify='right', style='h14b.TLabel')
        all_given_L = ttk.Label(block_3, text='Attempt:', style='h10b.TLabel', justify='right')
        specific_dc = ttk.Radiobutton(
            block_3, text='Specific Constants', variable=self.dc_selector, value='specific',
            style="h8.TRadiobutton")
        DJ_L = ttk.Label(block_3, text='\u0394J', **h8bL_r)
        DJK_L = ttk.Label(block_3, text='\u0394JK', **h8bL_r)
        DK_L = ttk.Label(block_3, text='\u0394K', **h8bL_r)
        dJ_L = ttk.Label(block_3, text='\u03B4J', **h8bL_r)
        dK_L = ttk.Label(block_3, text='\u03B4K', **h8bL_r)
        DJ_fit = ttk.Checkbutton(block_3, variable=self.DJ_fit)
        DJK_fit = ttk.Checkbutton(block_3, variable=self.DJK_fit)
        DK_fit = ttk.Checkbutton(block_3, variable=self.DK_fit)
        dJ_fit = ttk.Checkbutton(block_3, variable=self.dJ_fit)
        dK_fit = ttk.Checkbutton(block_3, variable=self.dK_fit)
        par_dc = ttk.Radiobutton(
            block_3, text='Constants from .par', variable=self.dc_selector, value='par',
            style="h8.TRadiobutton")
        float_dc = ttk.Radiobutton(
            block_3, text='Floating', variable=self.fix_or_float, value='float',
            style="h8.TRadiobutton")
        fix_dc = ttk.Radiobutton(
            block_3, text='Fixed', variable=self.fix_or_float, value='fix', style="h8.TRadiobutton")
        h1 = ttk.Separator(block_3, orient='horizontal')
        h2 = ttk.Separator(block_3, orient='horizontal')
        run_L = ttk.Label(block_3, text='Run', justify='right', style='h14b.TLabel')
        button_execute_fit = ttk.Button(
            block_3, text='Fit', style='h10b.TButton', command=self.finalfit)
        dc_L.grid(row=0, column=0, columnspan=4, padx=2, pady=2)
        all_given_L.grid(row=1, column=0, **x2y2w)
        specific_dc.grid(row=2, column=0, columnspan=2, **x2y2w)
        DJ_L.grid(row=3, column=1, **x2y2w)
        DJK_L.grid(row=4, column=1, **x2y2w)
        DK_L.grid(row=5, column=1, **x2y2w)
        dJ_L.grid(row=3, column=3, **x2y2w)
        dK_L.grid(row=4, column=3, **x2y2w)
        DJ_fit.grid(row=3, column=0, **x2y2e)
        DJK_fit.grid(row=4, column=0, **x2y2e)
        DK_fit.grid(row=5, column=0, **x2y2e)
        dJ_fit.grid(row=3, column=2, **x2y2e)
        dK_fit.grid(row=4, column=2, **x2y2e)
        par_dc.grid(row=6, column=0, columnspan=2, **x2y2w)
        h1.grid(row=7, column=0, columnspan=4, **x2y2ew)
        float_dc.grid(row=8, column=0, columnspan=2, **x2y2w)
        fix_dc.grid(row=8, column=2, columnspan=2, **x2y2w)
        h2.grid(row=9, column=0, columnspan=4, **x2y2ew)
        run_L.grid(row=14, column=0, columnspan=4, padx=2, pady=2)
        button_execute_fit.grid(row=15, column=0, columnspan=4, **x2y2ew)
        # ==========================================================================================
        #                                         Block 4
        # ==========================================================================================
        output_L = ttk.Label(block_4, text='Outputs', justify=c, style='h14b.TLabel')
        A_L = ttk.Label(block_4, text='A (MHz)', **h8bL_r)
        B_L = ttk.Label(block_4, text='B (MHz)', **h8bL_r)
        C_L = ttk.Label(block_4, text='C (MHz)', **h8bL_r)
        DJ_L = ttk.Label(block_4, text='\u0394J (MHz)', **h8bL_r)
        DJK_L = ttk.Label(block_4, text='\u0394JK (MHz)', **h8bL_r)
        DK_L = ttk.Label(block_4, text='\u0394K (MHz)', **h8bL_r)
        dJ_L = ttk.Label(block_4, text='\u03B4J (MHz)', **h8bL_r)
        dK_L = ttk.Label(block_4, text='\u03B4K (MHz)', **h8bL_r)
        rms_L = ttk.Label(block_4, text='RMS (MHz)', **h8bL_r)
        num_trans_L = ttk.Label(block_4, text='# transitions', **h8bL_r)
        A_E = ttk.Entry(block_4, textvariable=self.A, justify=c)
        B_E = ttk.Entry(block_4, textvariable=self.B, justify=c)
        C_E = ttk.Entry(block_4, textvariable=self.C, justify=c)
        DJ_E = ttk.Entry(block_4, textvariable=self.DJ, justify=c)
        DJK_E = ttk.Entry(block_4, textvariable=self.DJK, justify=c)
        DK_E = ttk.Entry(block_4, textvariable=self.DK, justify=c)
        dJ_E = ttk.Entry(block_4, textvariable=self.dJ, justify=c)
        dK_E = ttk.Entry(block_4, textvariable=self.dK, justify=c)
        rms_E = ttk.Entry(block_4, textvariable=self.rms, justify=c)
        num_trans_E = ttk.Entry(block_4, textvariable=self.num_trans, justify=c)
        output_L.grid(row=0, column=0, columnspan=2, padx=2, pady=2)
        A_L.grid(row=1, column=0, **x2y7e)
        B_L.grid(row=2, column=0, **x2y7e)
        C_L.grid(row=3, column=0, **x2y7e)
        DJ_L.grid(row=4, column=0, **x2y7e)
        DJK_L.grid(row=5, column=0, **x2y7e)
        DK_L.grid(row=6, column=0, **x2y7e)
        dJ_L.grid(row=7, column=0, **x2y7e)
        dK_L.grid(row=8, column=0, **x2y7e)
        rms_L.grid(row=9, column=0, **x2y7e)
        num_trans_L.grid(row=10, column=0, padx=7, pady=2, sticky='e')
        A_E.grid(row=1, column=1, **x2y2ew)
        B_E.grid(row=2, column=1, **x2y2ew)
        C_E.grid(row=3, column=1, **x2y2ew)
        DJ_E.grid(row=4, column=1, **x2y2ew)
        DJK_E.grid(row=5, column=1, **x2y2ew)
        DK_E.grid(row=6, column=1, **x2y2ew)
        dJ_E.grid(row=7, column=1, **x2y2ew)
        dK_E.grid(row=8, column=1, **x2y2ew)
        rms_E.grid(row=9, column=1, **x2y2ew)
        num_trans_E.grid(row=10, column=1, **x2y2ew)
        # ==========================================================================================
        #                                          Block 5
        # ==========================================================================================
        notes_L = ttk.Label(block_5, text='Notes', justify=c, style='h14b.TLabel')
        self.notes_textbox = tk.Text(
            block_5, height=14, width=50, relief='sunken', font='Helvetica 10', wrap=tk.WORD)
        notes_L.grid(row=0, column=0, padx=5, pady=10, sticky='w')
        self.notes_textbox.grid(row=1, column=0, rowspan=10, padx=2, pady=2, sticky='ns')
        self.notes_textbox.delete('1.0', tk.END)
        self.notes_textbox.insert('1.0', 'None')
        # ==========================================================================================
        #                                    Inputs/Outputs Frame
        # ==========================================================================================
        top = ttk.Separator(self.frame_ins_outs, orient='horizontal')
        bottom = ttk.Separator(self.frame_ins_outs, orient='horizontal')
        top.grid(row=0, column=0, columnspan=9, padx=2, pady=0, sticky='ew')
        bottom.grid(row=2, column=0, columnspan=9, padx=2, pady=5, sticky='ew')
        separator_1 = ttk.Separator(self.frame_ins_outs, orient='vertical')
        separator_2 = ttk.Separator(self.frame_ins_outs, orient='vertical')
        separator_3 = ttk.Separator(self.frame_ins_outs, orient='vertical')
        separator_4 = ttk.Separator(self.frame_ins_outs, orient='vertical')
        block_1.grid(row=1, column=0, padx=5, sticky='n')
        separator_1.grid(row=1, column=1, padx=20, pady=5, sticky='ns')
        block_2.grid(row=1, column=2, sticky='n')
        separator_2.grid(row=1, column=3, padx=20, pady=5, sticky='ns')
        block_3.grid(row=1, column=4, sticky='ns')
        separator_3.grid(row=1, column=5, padx=20, pady=5, sticky='ns')
        block_4.grid(row=1, column=6, sticky='n')
        separator_4.grid(row=1, column=7, padx=20, pady=5, sticky='ns')
        block_5.grid(row=1, column=8, padx=5, sticky='n')
        self.frame_ins_outs.grid(row=1, column=0)
        self.text_box_dict = {'notes': self.notes_textbox}
        # ==========================================================================================
        #                                        Plot Frame
        # ==========================================================================================
        self.plot = PlotManager(
            frame=self.frame_plot, figsize=(16, 8), dpi=100, subplotshape=111,
            plot_title='Final Fit', xlabel='Frequency / MHz', ylabel='Intensity / mV', x_min='Auto',
            x_max='Auto', y_min='Auto', y_max='Auto', legend_show=True, legend_font=10,
            legend_loc=0, left=0.05, right=0.98, top=0.95, bottom=0.09, row=0, column=0,
            columnspan=2, toolbar=True, toolrow=1, toolcol=0, toolpady=2, toolsticky='w')
        self.plot.canvas.mpl_connect(
            'pick_event', lambda event: page_funcs.mpl_click(event, self.sel_freq, self.sel_int))
        buttons_frame = ttk.Frame(self.frame_plot)
        save = ttk.Button(
            buttons_frame, text='Save', style='h10b.TButton', width=20,
            command=lambda: page_funcs.save_page(self.attr_dict, self.text_box_dict))
        eb_lst = [spec_path_E, cat_path_E]
        load = ttk.Button(
            buttons_frame, text='Load', style='h10b.TButton', width=20,
            command=lambda: page_funcs.load_page(
                self.attr_dict, tb_dict=self.text_box_dict, eb_var=eb_lst))
        clear = ttk.Button(
            buttons_frame, text='Defaults', style='h10b.TButton', width=20,
            command=lambda: page_funcs.clear_page(
                FinalFit.default, self.attr_dict, self.plot, textbox_dict=self.text_box_dict))
        save.grid(row=0, column=0, padx=2, pady=2, sticky='nsew')
        load.grid(row=0, column=1, padx=2, pady=2, sticky='nsew')
        clear.grid(row=0, column=2, padx=2, pady=2, sticky='nsew')
        buttons_frame.grid(row=1, column=1, columnspan=1, rowspan=1, pady=2, sticky='e')
        self.frame_plot.grid(row=0, column=0, padx=2, pady=2)

        self.page.enter_textbox(self.notes_textbox)
        self.page.exit_textbox(self.notes_textbox)
        self.page.left_click()
        self.attr_dict = {'sel_freq': self.sel_freq,
                          'sel_int': self.sel_int,
                          'spec_path': self.spec_path,
                          'cat_path': self.cat_path,
                          'freq_min': self.freq_min,
                          'freq_max': self.freq_max,
                          'freq_match': self.freq_match,
                          'threshold': self.threshold,
                          'ka_max': self.ka_max,
                          'dyn_range': self.dyn_range,
                          'max_error': self.max_error,
                          'A': self.A,
                          'B': self.B,
                          'C': self.C,
                          'DJ': self.DJ,
                          'DJK': self.DJK,
                          'DK': self.DK,
                          'dJ': self.dJ,
                          'dK': self.dK,
                          'DJ_fit': self.DJ_fit,
                          'DJK_fit': self.DJK_fit,
                          'DK_fit': self.DK_fit,
                          'dJ_fit': self.dJ_fit,
                          'dK_fit': self.dK_fit,
                          'fix_or_float': self.fix_or_float,
                          'dc_selector': self.dc_selector,
                          'rms': self.rms,
                          'num_trans': self.num_trans,
                          'omitted_points': self.tk_omitted_points}

    def qdc_mode(self):
        """
        Return distortion constants selected by checkbuttons if 'specific constants'
        radiobutton is selected.
        """
        qdc_mode = self.dc_selector.get()
        if qdc_mode == 'specific':
            specific_constants = []
            dc_checkboxes = [(self.DJ_fit, 'DJ'), (self.DJK_fit, 'DJK'), (self.DK_fit, 'DK'),
                             (self.dJ_fit, 'dJ'), (self.dK_fit, 'dK')]
            for dc, label in dc_checkboxes:
                if dc.get() == 1:
                    specific_constants.append(label)
        else:
            specific_constants = None
        return specific_constants

    def plot_results(self, centers, max_intens):
        """
        Plot results after fit is performed.

        Plot spectrum upright and predicted spectrum inverted beneath. Assigned transitions are
        marked as well as omitted transitions. Plot dashed line through each transition center
        determined by fit to gaussian lineshape.

        Parameters:
            centers (list of floats):
                Frequencies of centered transitions.
                Units: MHz
            max_intens (list of floats):
                Maximum intensity of gaussian fit for each transition.
                Units: mV
        """
        cat_path = self.cat_path.get()
        fname = Pickett.Cat(cat_path).fname
        freq_max = self.freq_max.get()
        freq_min = self.freq_min.get()
        ka_max = self.ka_max.get()
        dyn_range = self.dyn_range.get()
        omit = page_funcs.format_omitted_points(self.tk_omitted_points)

        self.plot.ax.cla()
        for x in range(len(centers)):
            f = centers[x]
            i = max_intens[x]
            self.plot.plot_line([f, f], [0, i], color='green', linestyle='dashed')
        spectrum = Spectrum(self.spec_path.get())
        lnlst = list(Pickett.Lin('%s.lin' % fname).dict.keys())

        cat = Pickett.Cat(cat_path)
        cat_filtered = cat.filter(
            freq_min=freq_min, freq_max=freq_max, Ka_max=ka_max, dyn_range=dyn_range)
        cat_filt_lnlst = cat.line_list(dictionary=cat_filtered)
        scale = cat.scale_to_spectrum(spectrum, lnlst, dictionary=cat_filtered, thresh=0.010)
        sim = cat.simulate(cat_filt_lnlst, freq_min=spectrum.freq_min, freq_max=spectrum.freq_max)
        sim = np.column_stack((sim[:, 0], sim[:, 1] * scale))

        lin_row_nums = [
            int(round((row - spectrum.freq_min) / spectrum.point_spacing)) for row in lnlst]
        omitted_row_nums = [
            int(round((row - spectrum.freq_min) / spectrum.point_spacing)) for row in omit]

        spec = spectrum.spectrum
        self.plot.plot_line(
            spec[:, 0], spec[:, 1], weight=1.5, color='black', label='Spectrum',
            picker=self.controller.picker)
        self.plot.plot_line(
            sim[:, 0], sim[:, 1], invert=1, weight=1.5, color='red', label='Simulation',
            picker=self.controller.picker)
        self.plot.plot_line(
            spec[lin_row_nums, 0], spec[lin_row_nums, 1], weight=0, color='red', marker='.',
            label='Assigned')
        try:
            self.plot.plot_line(
                spec[omitted_row_nums, 0], spec[omitted_row_nums, 1], weight=0, marker='x',
                color='green', label='Omitted')
        except IndexError:
            pass
        self.plot.set_labels()
        self.plot.zoom()
        self.plot.canvas.draw()

    def relay_outputs(self, initqdc, qdc_rejects, freq_rejects, omit):
        """
        Fill entry boxes in Results section.

        Fill Notes text box with information summarizing the fit:
            - Initial set of distortion constants
            - Rejected distortion constants
            - Transitions rejected by the program
            - Transitions omitted by the user

        Parameters:
            initqdc (list of str):
                Quartic distortion constants attempted in initial fit. (Ex. DJ, DK, etc.)
            qdc_rejects (list of str):
                Quartic distortion constants removed from fit. (Ex. DJ, DK, etc.)
            freq_rejects (list of floats):
                Frequencies where transitions were removed from fit.
                Units: MHz
            omit (list):
                Frequencies. Transitions at these frequencies not used in fit.
                Units: MHz
        """
        cat_path = self.cat_path.get()
        fname = Pickett.Cat(cat_path).fname
        piform = Pickett.Piform('%s.pi' % fname)
        lin = [row for row in open('%s.lin' % fname)]
        self.fill_output_entry(piform, len(lin))
        notes = []
        initqdc = 'Initial QDC:    ' + str(initqdc) + '\n\n'
        qdc_rejects = 'Rejected QDC:    ' + str(qdc_rejects) + '\n\n'
        freq_rejects = 'Manually removed:    ' + str(omit) + '\n\n' \
                       + 'Automatically removed:    ' + str(freq_rejects) + '\n\n'
        tb = self.notes_textbox.get("1.0", "end-1c")
        tb = tb.split('\n')
        for line in tb:
            if line != ' Results__________________________________________':
                notes.append(line + '\n')
            else:
                break
        notes = ''.join(notes)
        notes = notes + ' Results__________________________________________\n\n' \
                + initqdc + qdc_rejects + freq_rejects
        self.notes_textbox.delete('1.0', tk.END)
        self.notes_textbox.insert('1.0', notes)

    @testing.collect_garbage
    def finalfit(self):
        """
        Run finalfit() using inputs from GUI. Relay results to GUI.

        Results include:
            - Rotational constants
            - RMS
            - Number of transitions fit
            - Initial set of distortion constants
            - Rejected distortion constants
            - Transitions rejected by the program
            - Transitions omitted by the user
            - Transition frequencies
            - Peak intensity of each gaussian fit

        Experimental spectrum plotted upright and calculated spectrum plotted inverted beneath.
        Fitted transitions are marked on spectrum. Omitted transitions are also marked.
        """
        cat_path = self.cat_path.get()
        fname = Pickett.Cat(cat_path).fname
        spec_path = self.spec_path.get()
        pp_thresh = self.threshold.get()
        max_err = self.max_error.get()
        qdc_mode = self.dc_selector.get()
        floating = self.fix_or_float.get()
        freq_match = self.freq_match.get()
        freq_max = self.freq_max.get()
        freq_min = self.freq_min.get()
        ka_max = self.ka_max.get()
        dyn_range = self.dyn_range.get()
        omit = page_funcs.format_omitted_points(self.tk_omitted_points)
        specific_constants = self.qdc_mode()

        if floating == 'fix':
            floating = False
        else:
            floating = True
        # Pickett.copy_spfit_spcat_piform(self.controller.pickett_dir, cat_path)
        initqdc, qdc_rejects, iter, freq_rejects, centers, max_intens = finalfit(
            spec_path, cat_path, self.controller.pickett_dir, pp_thresh, max_error=max_err, qdc_mode=qdc_mode, floating=floating,
            specific_constants=specific_constants, freq_match=freq_match, freq_min=freq_min,
            freq_max=freq_max, ka_max=ka_max, dyn_range=dyn_range, omit=omit)
        self.plot_results(centers, max_intens)
        piform = '%s.pi' % fname
        lin = '%s.lin' % fname
        num_trans = len(Pickett.Lin(lin).lin)
        self.fill_output_entry(Pickett.Piform(piform), num_trans)
        self.relay_outputs(initqdc, qdc_rejects, freq_rejects, omit)

    def fill_output_entry(self, piform, num_trans):
        """
        Format and display results from Piform in GUI.

        Parameters:
            piform (piform object):
            num_trans (int):
                Number of transitions fit.
        """
        a = str(piform.dict['a']) + '(' + str(piform.dict['a_err']) + ')'
        b = str(piform.dict['b']) + '(' + str(piform.dict['b_err']) + ')'
        c = str(piform.dict['c']) + '(' + str(piform.dict['c_err']) + ')'
        try:
            if list(str(piform.dict['DJ']))[0] == '[':
                DJ = str(piform.dict['DJ'])
            else:
                DJ = str(piform.dict['DJ']) + '(' + str(piform.dict['DJ_err']) + ')'
        except KeyError:
            DJ = '[0.]'
        try:
            if piform.dict['DJK'] is None:
                DJK = 'None'
            elif list(str(piform.dict['DJK']))[0] == '[':
                DJK = str(piform.dict['DJK'])
            else:
                DJK = str(piform.dict['DJK']) + '(' + str(piform.dict['DJK_err']) + ')'
        except KeyError:
            DJK = '[0.]'
        try:
            if piform.dict['DK'] is None:
                DK = 'None'
            elif list(str(piform.dict['DK']))[0] == '[':
                DK = str(piform.dict['DK'])
            else:
                DK = str(piform.dict['DK']) + '(' + str(piform.dict['DK_err']) + ')'
        except KeyError:
            DK = '[0.]'
        try:
            if piform.dict['dJ'] is None:
                dJ = 'None'
            elif list(str(piform.dict['dJ']))[0] == '[':
                dJ = str(piform.dict['dJ'])
            else:
                dJ = str(piform.dict['dJ']) + '(' + str(piform.dict['dJ_err']) + ')'
        except KeyError:
            dJ = '[0.]'
        try:
            if piform.dict['dK'] is None:
                dK = 'None'
            elif list(str(piform.dict['dK']))[0] == '[':
                dK = str(piform.dict['dK'])
            else:
                dK = str(piform.dict['dK']) + '(' + str(piform.dict['dK_err']) + ')'
        except KeyError:
            dK = '[0.]'
        rms = piform.dict['rms']
        self.A.set(a)
        self.B.set(b)
        self.C.set(c)
        self.DJ.set(DJ)
        self.DJK.set(DJK)
        self.DK.set(DK)
        self.dJ.set(dJ)
        self.dK.set(dK)
        self.rms.set(rms)
        self.num_trans.set(num_trans)

    def plot_spectrum(self, spec_path):
        """ Plot spec_path """
        spectrum = Spectrum(spec_path).spectrum
        self.plot.ax.cla()
        self.plot.plot_line(
            spectrum[:, 0], spectrum[:, 1], color='black', weight=1, picker=self.controller.picker)
        self.plot.set_labels()
        self.plot.zoom()
        self.plot.canvas.draw()

    def plot_cat(self, cat_path):
        """ Plot simulation of cat_path """
        c = cat_path
        cat = Pickett.Cat(cat_path)
        sim = cat.simulate()
        self.plot.ax.cla()
        self.plot.plot_line(
            sim[:, 0], sim[:, 1], color='black', weight=1, picker=self.controller.picker)
        self.plot.set_labels()
        self.plot.zoom()
        self.plot.canvas.draw()


def initial_line_match(cat, pp, freq_match=None, freq_max=None, freq_min=None, ka_max=None,
                       dyn_range=None, omit=None):
    """
    Generate *.lin file using line matches between predicted spectrum and experimental peak pick.

    Frequencies from peak pick combined with quantum numbers from *.cat file to generate *.lin file.
    Ignore transitions at frequencies listed in omit.

    Parameters:
        cat (Pickett.Cat object):
        pp (array):
            col[0] -> freq.
            col[1] -> intensity.
        freq_match (float):
            Max abs(calc. - exp.) for line match.
            Default: None
        freq_max (float):
            Upper bound frequency.
            Units: MHz
            Default: None
        freq_min (float):
            Lower bound frequency.
            Units: MHz
            Default: None
        ka_max (int):
            Prolate limit upper bound.
            Default: None
        dyn_range (float):
            Dynamic range with respect to the strongest peak.
            Default: None
        omit (list):
            Frequencies. Transitions at these frequencies not used in fit.
            Units: MHz.
            Default: None
    """
    fname = cat.fname
    cat_filtered = cat.filter(
        freq_min=freq_min, freq_max=freq_max, Ka_max=ka_max, dyn_range=dyn_range)
    cat_freq_matches, spec_freq_matches = cat.spectrum_matches(
        pp, dictionary=cat_filtered, thresh=freq_match)
    omitted_points = omit
    if omitted_points:
        indices = []
        for x in range(len(spec_freq_matches)):
            for y in range(len(omitted_points)):
                if spec_freq_matches[x] == omitted_points[y]:
                    indices.append(x)
        indices = sorted(indices, reverse=True)
        for index in indices:
            del cat_freq_matches[index]
            del spec_freq_matches[index]
    cat_transitions = [cat.dict[freq] for freq in cat_freq_matches]
    exp_freq, J1, Ka1, Kc1, J0, Ka0, Kc0 = [], [], [], [], [], [], []
    for x, l in enumerate(cat_transitions):
        for dictionary in l:
            exp_freq.append(spec_freq_matches[x])
            J1.append(dictionary['N1'])
            Ka1.append(dictionary['Ka1'])
            Kc1.append(dictionary['Kc1'])
            J0.append(dictionary['N0'])
            Ka0.append(dictionary['Ka0'])
            Kc0.append(dictionary['Kc0'])
    for x in range(len(exp_freq)):
        if exp_freq[x] in omitted_points:
            del exp_freq[x]
            del J1[x]
            del Ka1[x]
            del Kc1[x]
            del J0[x]
            del Ka0[x]
            del Kc0[x]
    lin = Pickett.Lin()
    lin.assign_transition(freq=exp_freq, J1=J1, Ka1=Ka1, Kc1=Kc1, J0=J0, Ka0=Ka0, Kc0=Kc0)
    lin.save(fname=fname)


def qdc_selector(fname, mode='par', floating=True, specific_constants=None):
    """
    Generate *.par file with the set of quartic distortion constants requested by self.dc_selector.

    If mode == 'specific', checkmarked distortion constants are added to *.par file.
    If requested constant is not found in *.par file, an initial value of zero is used.
    If mode == 'par', only distortion constants found in the initial *.par file are used.

    Parameters:
        fname (str):
            Name of file without extension
        mode (str):
            'par' or 'specific'
            Default: par
        floating (bool):
            If true, qdc can change to accomplish the best fit. If false, qdc is fixed.
            Default: True
        specific_constants (list of str):
            Quartic distortion constants to fit: 'DJ', 'DJK', 'DK', 'dJ', 'dK'
            Default: None
    Returns:
        initial_qdcs (list):
            Quartic distortion constants initially attempted in fit.
    """
    try:
        par = Pickett.Par_Var('%s.par' % fname)
    except FileNotFoundError:
        try:
            par = Pickett.Par_Var('%s.var' % fname)
        except FileNotFoundError:
            showerror("File Not Found", "*.par or *.var file must be in same directory as *.cat")
            return
    par.attributes['nline'] = 1000
    par.attributes['npar'] = 8
    if specific_constants is None:
        specific_constants = []
    initial_qdcs = []
    if mode == 'specific':
        dcs = ['DJ', 'DJK', 'DK', 'dJ', 'dK']
        for constant in dcs:
            if constant in specific_constants:
                initial_qdcs.append(constant)
                if par.attributes[constant] is None:
                    if not floating:
                        msg = constant + ' not found in .par file. QDCs must be found in .par ' \
                                         'file to fix their value.'
                        showerror('Insufficient Information', message=msg)
                        raise AttributeError(constant + ' not found in .par file.')
                        return
                    else:
                        par.attributes[constant] = 0.0
                        par.set_stdev(constant, floating=True)
                else:
                    par.set_stdev(constant, floating=floating)
            else:
                par.attributes[constant] = None
                par.attributes[constant + '_err'] = None
    elif mode == 'par':
        qdcs = ['DJ', 'DJK', 'DK', 'dJ', 'dK']
        for qdc in par.given_constants:
            if qdc in qdcs:
                initial_qdcs.append(qdc)
        if floating:
            par.float_given_qdc()
        elif not floating:
            par.fix_given_qdc()
    par.save(fname=fname, extension='.par')
    # Pickett.spfit_run(fname)
    return initial_qdcs


def piform_bad_qdc(fname, floating=True):
    """
    If floating=True, determine distortion constants with greater than 20% error.

    If any constants are found to have more than 20% error, onstants removed from *.par.
    Run SPFIT with new set of constants. When no more constants are found to have more than 20%
    error, run SPCAT.

    Parameters:
        fname (str):
            File name without extension.
        floating (bool):
            If true, qdc can change to accomplish the best fit. If false, qdc is fixed.
            Default: True
    Returns:
        rejected_qdcs (list):
            List of constants.
    """
    rejected_qdcs = []
    if floating:
        while True:
            piform = Pickett.Piform('%s.pi' % fname)
            par = Pickett.Par_Var('%s.par' % fname)
            bad_constants = piform.dict['bad_constants']
            if bad_constants is not None:
                for x in reversed(bad_constants):
                    if x not in ['10000', '20000', '30000']:
                        rejected_qdcs.append(Pickett.key_dict[x])
                        par.attributes['npar'] = int(par.attributes['npar']) - 1
                        par.attributes[Pickett.key_dict[x]] = None
                        par.attributes[Pickett.key_dict[x] + '_err'] = None
                par.save(fname=fname, extension='.par')
                Pickett.spfit_run(fname)
            else:
                Pickett.spcat_run(fname)
                break
    return rejected_qdcs


def qdc_large_uncertainty(fname, floating=True):
    """
    If floating=True, determine distortion constants with magnitude less than relative uncertainty.

    Constants removed from *.par. Run SPFIT with new set of constants.

    Parameters:
        fname (str):
            File name without extension.
        floating (bool):
            If true, qdc can change to accomplish the best fit. If false, qdc is fixed.
            Default: True
    Returns:
        rejected (list):
            List of constants removed from fit.
    """
    rejected = []
    if floating:
        while True:
            piform = Pickett.Piform('%s.pi' % fname)
            par = Pickett.Par_Var('%s.par' % fname)
            rejected_qdcs = piform.qdc_check()
            if rejected_qdcs:
                for qdc in rejected_qdcs:
                    rejected.append(qdc)
                    par.attributes['npar'] = int(par.attributes['npar']) - 1
                    # par.set_npar(int(par.attributes['npar']) - 1)
                    par.attributes[qdc] = None
                    par.attributes[qdc + '_err'] = None
                par.save(fname=fname, extension='.par')
                Pickett.spfit_run(fname)
            else:
                break
    return rejected


def filter_transitions(fname, max_error):
    """
    Iteratively remove transitions with error greater than self.max_error.

    Parameters:
        fname (str):
            File name without extension
        max_error (float):
            Maximum transition (obs. - calc.)
            Units: MHz
    Returns:
        freqs_rejected (list):
            List of frequencies where transitions were removed from fit.
            Units: MHz
        iterations (int):
            Number of iterations before all transitions had error less than self.max_error.
    """
    freqs_rejected = []
    iterations = 1
    while True:
        piform = Pickett.Piform('%s.pi' % fname)
        par = Pickett.Par_Var('%s.par' % fname)
        worst_line = piform.worst_line
        lin = Pickett.Lin('%s.lin' % fname)
        par.attributes['nline'] = int(len(lin.lin)) + 1
        par.save(fname=fname, extension='.par')
        if abs(float(worst_line[8])) < max_error:
            break
        else:
            iterations += 1
            freqs_rejected.append(abs(float(worst_line[7])))
            try:
                transition_row = worst_line[0].split(':')
                transition_row = int(transition_row[0]) - 1
            except ValueError:
                transition_row = worst_line[0].split('/')
                transition_row = int(transition_row[0]) - 1
            lin.delete_array_row(transition_row)
            lin.save(fname)
            Pickett.spfit_run(fname)
            Pickett.spcat_run(fname)
    return freqs_rejected, iterations


def fit_peak_center(fname, spectrum):
    """
    Fit transitions from Piform file to gaussian line shape. Update *.lin. Run SPFIT and SPCAT.

    Parameters:
        fname (str):
            Piform file name without extension
        spectrum (Spectrum object):
    Return:
        centered (list):
            Center frequencies of Gaussian fits.
            Units: MHz
        max_intensity (list):
            Maximum intensity of gaussian fit.
            Units: mV
    """
    piform = Pickett.Piform('%s.pi' % fname)
    qns, uncentered, oc = piform.line_list_split(3)
    centered = []
    max_intensity = []
    for x in uncentered:
        row_num = spectrum.freq_to_row(float(x))
        row_min = row_num - 2
        row_max = row_num + 3
        region_to_fit = spectrum.spectrum[row_min:row_max, :]
        xmin = region_to_fit[0, 0]
        xmax = region_to_fit[-1, 0]
        try:
            pars, cov = curve_fit(
                f=gaussian, xdata=region_to_fit[:, 0], ydata=region_to_fit[:, 1],
                p0=[spectrum.spectrum[row_num, 1], region_to_fit[0, 0], 0.06],
                bounds=(-np.inf, np.inf))
            pre_exponential = pars[0]
            mu = pars[1]
            sigma = pars[2]
            x_space = np.linspace(xmin, xmax, 50)
            y = gaussian(x_space, pre_exponential, mu, sigma)
            intensity_max = np.max(y)
            center_freq = x_space[np.where(y == np.max(y))]
            centered.append(round(float(center_freq), 4))
            max_intensity.append(intensity_max)
        except RuntimeError:
            center_freq = x
            print('err:  ', center_freq)
            centered.append(round(float(center_freq), 4))
    lin = Pickett.Lin('%s.lin' % fname)
    J1 = lin.lin[:, 0]
    Ka1 = lin.lin[:, 1]
    Kc1 = lin.lin[:, 2]
    J0 = lin.lin[:, 3]
    Ka0 = lin.lin[:, 4]
    Kc0 = lin.lin[:, 5]
    lin = Pickett.Lin()
    lin.assign_transition(freq=centered, J1=J1, Ka1=Ka1, Kc1=Kc1, J0=J0, Ka0=Ka0, Kc0=Kc0)
    lin.save(fname=fname)
    Pickett.spfit_run(fname)
    Pickett.spcat_run(fname)
    return centered, max_intensity


def finalfit(spec_path, cat_path, pickett_dir, pp_threshold, max_error=None, qdc_mode=None, floating=None,
             specific_constants=None, freq_match=None, freq_min=None, freq_max=None, ka_max=None,
             dyn_range=None, omit=None):
    """
    Fit spectrum automatically using Pickett suite.

    Not akin to AUTOFIT. Function requires initial spectral prediction (*.cat file)
    to be close to the refined fit. For example, a *.cat file generated using a JB95 fit with
    reasonable care taken when selecting transition centers.

    Parameters:
        spec_path (str):
            File path to spectrum.
        cat_path (str):
            File path to *.cat file.
        pp_threshold (float):
            Peak pick threshold (mV).
            Units: mV
        max_error (float):
            Maximum transition (obs. - calc.)
            Units: MHz
            Default: 0.040
        qdc_mode (str):
            'par' or 'specific'
            'par' uses only the qdc that are given in initial *.par.
            'specific' uses specific_constants list. If not in initial
            *.par, start at 0.
            Default: par
        floating (bool):
            If True, allows qdc to vary to accomplish the best fit.
            Default: True
        specific_constants (list of str):
            Quartic distortion constants to fit: 'DJ', 'DJK', 'DK', 'dJ', 'dK'
            Default: None
        freq_match (float):
            Max abs(calc. - exp.) for line match.
            Units: MHz
            Default: 0.020
        freq_max (float):
            Upper bound frequency.
            Units: MHz.
            Default: 18000
        freq_min (float):
            Lower bound frequency.
            Units: MHz.
            Default: 2000
        ka_max (int):
            Prolate limit upper bound.
            Default: 10
        dyn_range (float):
            Dynamic range with respect to the strongest peak.
            Default: 100
        omit (list):
            Frequencies. Transitions at these frequencies not used in fit.
            Units: MHz.
            Default: []
    Returns:
        initial_qdc (list):
            Quartic distortion constants initially attempted in fit.
        qdc_rejects (list):
           Quartic distortion constants rejected in the fitting process.
        iterations (int):
            Number of iterations before satisfactory fit was achieved.
        freq_rejects(list):
            Frequencies where transitions were removed from fit.
            Units: MHz
        center_freqs (list):
            Frequencies of centered transitions.
            Units: MHz
        max_intens (list):
            Maximum intensity of gaussian fit for each transition.
            Units: mV
    """
    if max_error is None:
        max_error = 0.040
    if qdc_mode is None:
        qdc_mode = 'par'
    if floating is None:
        floating = True
    if freq_match is None:
        freq_match = 0.020
    if freq_min is None:
        freq_min = 2000
    if freq_max is None:
        freq_max = 18000
    if ka_max is None:
        ka_max = 10
    if dyn_range is None:
        dyn_range = 100
    if omit is None:
        omit = []

    cat_dir = os.path.dirname(cat_path)
    os.chdir(cat_dir)
    Pickett.copy_spfit_spcat_piform(pickett_dir, cat_dir)
    cat = Pickett.Cat(cat_path)
    fname = cat.fname
    spectrum = Spectrum(spec_path)
    peak_pick = spectrum.peak_pick(thresh=pp_threshold, sort=True)
    initial_line_match(
        cat, peak_pick, freq_match=freq_match, freq_max=freq_max, freq_min=freq_min,
        ka_max=ka_max, dyn_range=dyn_range, omit=omit)
    initial_qdc = qdc_selector(
        fname, mode=qdc_mode, floating=floating, specific_constants=specific_constants)
    Pickett.spfit_run(fname)
    rejects1 = piform_bad_qdc(fname, floating=floating)
    rejects2 = qdc_large_uncertainty(fname, floating=floating)
    qdc_rejects = []
    for x in rejects1:
        qdc_rejects.append(x)
    for x in rejects2:
        qdc_rejects.append(x)
    freq_rejects, iterations = filter_transitions(fname, max_error)
    center_freqs, max_intens = fit_peak_center(fname, spectrum)
    return initial_qdc, qdc_rejects, iterations, freq_rejects, center_freqs, max_intens


def gaussian(x, pre_exp, mu, sigma):
    """
    Return value of a Guassian function with the given pre-exponential factor, center,
    and width at position x.

    Parameters:
        x (float):
            Position.
        pre_exp (float):
            Pre-exponential factor
        mu (float):
            Line center.
        sigma (float):
            Line width.
    Return:
        Value along Gaussian curve at position x (float).
    """
    return pre_exp * np.exp(-np.log(2) * ((x - mu) / (sigma / 2)) ** 2)
