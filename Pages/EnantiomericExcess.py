"""
Author: Channing West
Changelog: 12/5/2019
"""

import numpy as np
import pandas as pd
import os
import tkinter as tk
import tkinter.ttk as ttk
import Pages.PageFormat as page_funcs
from Pages.PageFormat import PageFormat
from Spectrum import Spectrum
from Pickett import Cat
from TkAgg_Plotting import PlotManager
from tkinter.messagebox import showerror
import testing


class EnantiomericExcess(ttk.Frame):
    """
    Generate GUI. Calculate enantiomeric excess using broadband molecular rotational spectra.

    BUTTONS
        PLOT NAVIGATION BAR
            See TkAgg_Plotting.PlotManager()
        SAVE, LOAD, DEFAULTS, BACK TO NAVIGATOR, EXIT APPLICATION
            See PageFormat.py

    1.  Upload files
        -   Upload racemic spectrum and enantioenriched spectrum.
        -   (Optional) Upload *.cat file for each diastereomer complex. Provide *.cat files for
            better diastereomer distinction. Results in better filtering. Omitting species1_cat and
            species2_cat places more importance on peak pick threshold because species1 and species2
            are distinguished by peaks from spec2_pp that are not in spec1_pp. For an EE
            calculation, can be problematic if sample is not of high enantiopurity.
        Buttons:
            BROWSE
                Browse files with accepted file extension.
            PLOT
                Run plot_spectrum() with the appropriate spectrum. Plot spec on plot and remove all
                other series.
    2.  Peak pick
        -   Enter cutoff threshold (mV). Use PLOT button and NAV BAR zoom to find threshold.
        -   Perform peak pick on racemic and enantioenriched spectra. Threshold does not have 
            to be the same between the two spectra.
        -   Identified peaks are marked on the spectrum and displayed in the top plot.
        -   For a peak to be used in the ee calculation, frequency of the peak must be in the
            racemic peak pick.
        -   If *.cat files are not provided, threshold is very important. Set the threshold of the
            racemic spectrum low, so the spectra of both diastereomers are captured. Set the
            threshold of the enantioenriched so that the spectrum of one enantiomer is captured and
            the spectrum of the other enantiomer is missed.
        Buttons:
            RACEMIC
                Run peak_pick() with racemic spectrum. Locate peaks in spec, save temporary file,
                mark peaks on spec.
            ENRICHED
                Run peak_pick() with enriched spectrum. Locate peaks in spec, save temporary file,
                mark peaks on spec.
    3.  Filter transitions
        -   Filter only works if *.cat files for each diastereomer are provided.
        -   Filter parameters include frequency minimum, frequency maximum, frequency match 
            threshold (see below), dynamic range (see below), J max, and Ka max.
        -   Frequency match threshold refers to the maximum difference between the predicted 
            line position and the experimental line position. If 0.020 MHz is given, a predicted 
            transition does not pass unless a peak in the racemic peak pick is within 0.020 MHz.
        -   Dynamic range refers to the minimum accepted intensity with respect to the strongest 
            signal. If 100, a predicted transition does not pass unless it is
            at least 1/100 the intensity of the strongest predicted transition.
        -   Enter desired filter conditions and press 'Calculate Transition Ratios' button. 
            The *.cat files are filtered and transition_scale_factor() is executed to
            find scale factors for each transition between the two spectra.
        -   A histogram of scale factors for each diastereomer is generated below.
        Buttons:
            CALCULATE TRANSITION RATIOS
                Run transition_scale_factor() with enriched spectrum and racemic spectrum.
                Calculate [spec1 intensity / spec2 intensity] using 'peak_pick_racemic.npy' and
                'peak_pick_enriched.npy'. Save data in temporary files 'diastereomer_1_analysis.npy'
                and 'diastereomer_2_analysis.npy' Histograms displayed in plots below.
    4.  Filter by Intensity Ratio
        -   Filter transitions by scale factors.
        -   Two methods:
            1.  3 sigma filter
                Filter transitions with scale factor more than 3 standard deviations away from
                the mean. Can be used multiple times. Histogram updated after each press.
            2.  Manual
                Manually set minimum and maximum scale factors.
        -   If using 3 sigma filter achieves suitable data set, make sure minimum and maximum
            values for each diastereomer do not further filter the data when ee calculation
            is executed.
        3SIGMA FILTER
            Run filter_dominant() with appropriate file, i.e. 'diastereomer_1_analysis.npy' or
            'diastereomer_2_analysis.npy' and save updated version.
            Filter transitions that produce R value more than 3 s.d. away from mean. Update plot.
            Set appropriate filter boundaries after running 3-sigma filter.

    5.  Histogram Parameters
        top N:
            Number of transitions from each diastereomer used to calculate EE. If set to 25, 25
            transitions of each diastereomer used, resulting in 625 total EE calculations.
        tag ee:
            ee of the chiral tag. Between 0 and 1. If tag ee is unknown, leave at 1.
            CalculatedEE = analyteEE * tagEE
        Number of Bins:
            Number of histogram bins.
        Color:
            Bin color.
        Border:
            Apply black border around each bin.
        Stats. Label:
            Display label with statistical information about the histogram. Contents of the label
            include all the values from the Results section. The checkbuttons beside each result
            allow you to display certain stats and omit others.
        Plot Mean:
            Plot a dashed line through the mean of the histogram.
        Buttons:
            CALCULATE EE
                Run self.calc_ee(). Calculate EE using 'diastereomer_1_analysis.npy' and
                'diastereomer_2_analysis.npy'
    5.5 Refining Calculation (with 'Selected Point' section)
        -   After ee is calculated, the plot at the top of the page displays the
            enantioenriched spectrum with all transitions used to calculate ee marked.
            Diastereomers distinguishable by unique markers.
        -   Zoom on transitions and omit if you find a problem.
        -   To omit a transition, left-click the point on the plot and press 'Omit From EE Calc.'
            button. The point is selected if the frequency populates the entry field beside the 'x'
            label. It is okay if neighboring frequencies populate this field.
        -   The list of omitted transitions can be reset using the 'Reset Omits' button.
        OMIT FROM EE CALC.
            Omit a transition from ee calculation. After point(s) have been omitted,
            rerun CALCULATE EE.
    6.  Results
        -   Display statistics on ee histogram, including: mean, standard deviation,
            standard error, max, min. Label displaying stats can be added to plot.
        -   (Optional) Save summary files:
        SAVE OUTPUTS
            Run save_results().
            Provide 'base_name' shared by all summary files.
                '{base_name}_summary.txt'
                    Contains information from entry boxes.
                '{base_name}_dominant_diastereomer.csv'
                    Diastereomer 1 characterization
                    col[0] -> transition frequency
                    col[1] -> intensity in racemic spectrum
                    col[2] -> intensity in enriched spectrum
                    col[3] -> col[2]/col[1]
                '{base_name}_minor_diastereomer.csv'
                    Diastereomer 2 characterization
                    col[0] -> transition frequency
                    col[1] -> intensity in racemic spectrum
                    col[2] -> intensity in enriched spectrum
                    col[3] -> col[2]/col[1]
                '{base_name}_ee_calculations.csv'
                    Individual ee values.
    7.  Adjust Axes
        -   Update certain aspects of ee histogram without recalculating, including: bin color,
            border, stats label, plot mean.
        UPDATE HISTOGRAM
            Run plot_ee(). Handles histogram, including mean line, color, labels, etc.
    """
    default = {'sel_freq': 'None Selected',
               'sel_int': 'None Selected',
               'rs_pp_lock': 0,
               'enriched_pp_lock': 0,
               'calc_ratios_lock': 0,
               'calc_ee_lock': 0,
               'dom_cat': 'None',
               'species2_cat': 'None',
               'rs_spec': 'None',
               'spec1': 'None',
               'pp_thresh': '0.001',
               'freq_min': 2000,
               'freq_max': 18000,
               'freq_match': 0.020,
               'dyn_range': 100,
               'j_max': 30,
               'ka_max': 6,
               'dom_min': 1.0,
               'dom_max': 2.0,
               'minor_min': 0.0,
               'minor_max': 1.0,
               'topN': 25,
               'tag_ee': 1.0,
               'num_bins': 20,
               'color': 'blue',
               'border': 1,
               'mean_ee': 'None',
               'stdev_ee': 'None',
               'stderr_ee': 'None',
               'max_ee': 'None',
               'min_ee': 'None',
               'legend': 1,
               'mean_line': 1,
               'legend_mean_ee': 1,
               'legend_stdev_ee': 1,
               'legend_stderr_ee': 1,
               'legend_max_ee': 1,
               'legend_min_ee': 1,
               'plot_title': 'Enantiomeric Excess',
               'x_title': 'ee',
               'y_title': 'Number of Occurrences',
               'xmin': 'Auto',
               'xmax': 'Auto',
               'ymin': 'Auto',
               'ymax': 'Auto',
               'omitted_points': 'None'}

    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.controller = controller
        self.page_title = "Broadband MRR Toolbox - Enantiomeric Excess"
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.frame.bind("<Button-1>", lambda event: self.page.scroll_canvas())

        self.sel_freq = tk.StringVar()
        self.sel_int = tk.StringVar()
        self.sel_freq.set(EnantiomericExcess.default['sel_freq'])
        self.sel_int.set(EnantiomericExcess.default['sel_int'])
        self.rs_pp_lock = tk.IntVar()
        self.enriched_pp_lock = tk.IntVar()
        self.calc_ratios_lock = tk.IntVar()
        self.calc_ee_lock = tk.IntVar()
        self.rs_pp_lock.set(EnantiomericExcess.default['rs_pp_lock'])
        self.enriched_pp_lock.set(EnantiomericExcess.default['enriched_pp_lock'])
        self.calc_ratios_lock.set(EnantiomericExcess.default['calc_ratios_lock'])
        self.calc_ee_lock.set(EnantiomericExcess.default['calc_ee_lock'])
        self.tk_omitted_points = tk.StringVar()
        self.dom_cat = tk.StringVar()
        self.minor_cat = tk.StringVar()
        self.rs_spec = tk.StringVar()
        self.enriched_spec = tk.StringVar()
        self.dom_cat.set(EnantiomericExcess.default['dom_cat'])
        self.minor_cat.set(EnantiomericExcess.default['species2_cat'])
        self.rs_spec.set(EnantiomericExcess.default['rs_spec'])
        self.enriched_spec.set(EnantiomericExcess.default['spec1'])
        self.pp_thresh = tk.StringVar()
        self.pp_thresh.set(EnantiomericExcess.default['pp_thresh'])
        self.freq_min = tk.IntVar()
        self.freq_max = tk.IntVar()
        self.freq_match = tk.DoubleVar()
        self.dyn_range = tk.IntVar()
        self.j_max = tk.IntVar()
        self.ka_max = tk.IntVar()
        self.freq_min.set(EnantiomericExcess.default['freq_min'])
        self.freq_max.set(EnantiomericExcess.default['freq_max'])
        self.freq_match.set(EnantiomericExcess.default['freq_match'])
        self.dyn_range.set(EnantiomericExcess.default['dyn_range'])
        self.j_max.set(EnantiomericExcess.default['j_max'])
        self.ka_max.set(EnantiomericExcess.default['ka_max'])
        self.dom = []
        self.minor = []
        self.dom_min = tk.DoubleVar()
        self.dom_max = tk.DoubleVar()
        self.minor_min = tk.DoubleVar()
        self.minor_max = tk.DoubleVar()
        self.dom_min.set(EnantiomericExcess.default['dom_min'])
        self.dom_max.set(EnantiomericExcess.default['dom_max'])
        self.minor_min.set(EnantiomericExcess.default['minor_min'])
        self.minor_max.set(EnantiomericExcess.default['minor_max'])
        self.topN = tk.IntVar()
        self.tag_ee = tk.DoubleVar()
        self.num_bins = tk.IntVar()
        self.color = tk.StringVar()
        self.border = tk.IntVar()
        self.label = tk.IntVar()
        self.mean_line = tk.IntVar()
        self.topN.set(EnantiomericExcess.default['topN'])
        self.tag_ee.set(EnantiomericExcess.default['tag_ee'])
        self.num_bins.set(EnantiomericExcess.default['num_bins'])
        self.color.set(EnantiomericExcess.default['color'])
        self.border.set(EnantiomericExcess.default['border'])
        self.label.set(EnantiomericExcess.default['legend'])
        self.mean_line.set(EnantiomericExcess.default['mean_line'])
        self.mean_ee = tk.StringVar()
        self.stdev_ee = tk.StringVar()
        self.stderr_ee = tk.StringVar()
        self.max_ee = tk.StringVar()
        self.min_ee = tk.StringVar()
        self.legend_mean_ee = tk.IntVar()
        self.legend_stdev_ee = tk.IntVar()
        self.legend_stderr_ee = tk.IntVar()
        self.legend_max_ee = tk.IntVar()
        self.legend_min_ee = tk.IntVar()
        self.mean_ee.set(EnantiomericExcess.default['mean_ee'])
        self.stdev_ee.set(EnantiomericExcess.default['stdev_ee'])
        self.stderr_ee.set(EnantiomericExcess.default['stderr_ee'])
        self.max_ee.set(EnantiomericExcess.default['max_ee'])
        self.min_ee.set(EnantiomericExcess.default['min_ee'])
        self.legend_mean_ee.set(EnantiomericExcess.default['legend_mean_ee'])
        self.legend_stdev_ee.set(EnantiomericExcess.default['legend_stdev_ee'])
        self.legend_stderr_ee.set(EnantiomericExcess.default['legend_stderr_ee'])
        self.legend_max_ee.set(EnantiomericExcess.default['legend_max_ee'])
        self.legend_min_ee.set(EnantiomericExcess.default['legend_min_ee'])
        self.plot_title = tk.StringVar()
        self.xlabel = tk.StringVar()
        self.ylabel = tk.StringVar()
        self.xmin = tk.StringVar()
        self.xmax = tk.StringVar()
        self.ymin = tk.StringVar()
        self.ymax = tk.StringVar()
        self.plot_title.set(EnantiomericExcess.default['plot_title'])
        self.xlabel.set(EnantiomericExcess.default['x_title'])
        self.ylabel.set(EnantiomericExcess.default['y_title'])
        self.xmin.set(EnantiomericExcess.default['xmin'])
        self.xmax.set(EnantiomericExcess.default['xmax'])
        self.ymin.set(EnantiomericExcess.default['ymin'])
        self.ymax.set(EnantiomericExcess.default['ymax'])
        figure_1 = ttk.Frame(self.frame)
        figure_2 = ttk.Frame(self.frame)
        figure_3 = ttk.Frame(self.frame)
        block_1 = ttk.Frame(self.frame)
        block_2 = ttk.Frame(self.frame)
        block_3 = ttk.Frame(self.frame)
        # ==========================================================================================
        #                                Figure One and Block One
        # ==========================================================================================
        self.spec_pm = PlotManager(
            frame=figure_1, figsize=(16, 8), dpi=100, subplotshape=111, zoom_mode=0,
            plot_title='Spectrum', xlabel='Frequency / MHz', ylabel='Intensity / mV', x_min='Auto',
            x_max='Auto', y_min='Auto', y_max='Auto', legend_show=True, legend_font=10,
            legend_loc=0, left=0.06, right=0.98, top=0.94, bottom=0.08, row=0, column=0,
            columnspan=2, toolbar=True, toolrow=1, toolcol=0, toolpady=2, toolsticky='w')
        self.spec_pm.canvas.mpl_connect(
            'pick_event', lambda event: page_funcs.mpl_click(event, self.sel_freq, self.sel_int))
        buttons_frame = ttk.Frame(figure_1)
        v = 'vertical'
        h = 'horizontal'
        c = tk.CENTER
        center = {'justify': c}
        r = tk.RIGHT
        h10 = 'Helvetica 10'
        h14bL = 'h14b.TLabel'
        h8bL = 'h8b.TLabel'
        h10bB = 'h10b.TButton'
        h8bB = 'h8b.TButton'
        x5y2e = {'padx': 5, 'pady': 2, 'sticky': 'e'}
        x5y2ew = {'padx': 5, 'pady': 2, 'sticky': 'ew'}
        x2y2 = {'padx': 2, 'pady': 2}
        x5y10 = {'padx': 5, 'pady': 10}
        x2y15 = {'padx': 2, 'pady': 15}
        x2y2e = {'padx': 2, 'pady': 2, 'sticky': 'e'}
        x2y2ew = {'padx': 2, 'pady': 2, 'sticky': 'ew'}
        h8bL_r = {'style': h8bL, 'justify': r}
        h14bL_c = {'style': h14bL, 'justify': c}
        x2y5ew = {'padx': 2, 'pady': 5, 'sticky': 'ew'}
        x30y5ns = {'padx': 30, 'pady': 5, 'sticky': 'ns'}
        x5y5nsew = {'padx': 5, 'pady': 5, 'sticky': 'nsew'}
        h8bL_c = {'style': h8bL, 'justify': c}
        save = ttk.Button(
            buttons_frame, text='Save', width=20, style=h10bB,
            command=lambda: page_funcs.save_page(self.attr_dict, self.text_box_dict))
        clear_page = ttk.Button(
            buttons_frame, text='Defaults', width=20, style=h10bB,
            command=lambda: page_funcs.clear_page(
                EnantiomericExcess.default, self.attr_dict, self.spec_pm, self.dom_pm,
                self.minor_pm, self.ee_pm, textbox_dict=self.text_box_dict))
        save.grid(row=0, column=0, **x2y2, sticky='nsew')
        clear_page.grid(row=0, column=2, **x2y2, sticky='nsew')
        buttons_frame.grid(row=1, column=1, rowspan=1, pady=2, sticky='e')
        figure_1.grid(row=1, column=0, **x2y2)

        sel_point_L = ttk.Label(block_1, text='Selected Point', style='h14b.TLabel')
        sel_freq_L = ttk.Label(block_1, text='x', **h8bL_r)
        sel_int_L = ttk.Label(block_1, text='y', **h8bL_r)
        sel_freq_E = ttk.Entry(block_1, textvariable=self.sel_freq, **center)
        sel_int_E = ttk.Entry(block_1, textvariable=self.sel_int, **center)

        omit_B = ttk.Button(
            block_1, text='Omit From EE Calc.', style=h8bB,
            command=lambda: page_funcs.selected_point(
                'omit', self.tk_omitted_points, self.sel_freq))
        reset_B = ttk.Button(
            block_1, text='Reset Omits', style=h8bB,
            command=lambda: page_funcs.selected_point(
                'reset', self.tk_omitted_points, self.sel_freq))

        upload_header = ttk.Label(block_1, text='1. Upload Files', **h14bL_c)
        rs_spec_L = ttk.Label(block_1, text='Racemic\nSpectrum', **h8bL_r)
        rs_spec_E = ttk.Entry(block_1, textvariable=self.rs_spec, **center)
        rs_browse = ttk.Button(
            block_1, text='Browse', style=h8bB,
            command=lambda: page_funcs.write_path(self.rs_spec, eb_var=rs_spec_E, ftype='ft'))
        dom_cat_L = ttk.Label(block_1, text='Dominant\nCat', **h8bL_r)
        dom_cat_E = ttk.Entry(block_1, textvariable=self.dom_cat, **center)
        dom_browse = ttk.Button(
            block_1, text='Browse', style=h8bB,
            command=lambda: page_funcs.write_path(self.dom_cat, eb_var=dom_cat_E, ftype='cat'))
        enriched_spec_L = ttk.Label(block_1, text='Enriched\nSpectrum', **h8bL_r)
        enriched_spec_E = ttk.Entry(block_1, textvariable=self.enriched_spec, **center)
        enriched_browse = ttk.Button(
            block_1, text='Browse', style=h8bB,
            command=lambda: page_funcs.write_path(
                self.enriched_spec, eb_var=enriched_spec_E, ftype='ft'))
        minor_cat_L = ttk.Label(block_1, text='Minor\nCat', **h8bL_r)
        minor_cat_E = ttk.Entry(block_1, textvariable=self.minor_cat, **center)
        minor_browse = ttk.Button(
            block_1, text='Browse', style=h8bB,
            command=lambda: page_funcs.write_path(self.minor_cat, eb_var=minor_cat_E, ftype='cat'))

        eb_lst = [rs_spec_E, enriched_spec_E, dom_cat_E, minor_cat_E]
        load = ttk.Button(
            buttons_frame, text='Load', width=20, style=h10bB,
            command=lambda: page_funcs.load_page(
                self.attr_dict, self.rs_pp_lock, self.enriched_pp_lock, self.calc_ratios_lock,
                self.calc_ee_lock, tb_dict=self.text_box_dict, eb_var=eb_lst))
        load.grid(row=0, column=1, **x2y2, sticky='nsew')

        pp_header = ttk.Label(block_1, text='2. Peak Pick Spectra', **h14bL_c)
        pp_L = ttk.Label(block_1, text='Pick\nThreshold', **h8bL_r)
        pp_E = ttk.Entry(block_1, textvariable=self.pp_thresh, **center)
        pp_RS_B = ttk.Button(
            block_1, text='Racemic', style=h10bB, command=lambda: self.peak_pick(spec='rs'))
        pp_enriched_B = ttk.Button(
            block_1, text='Enriched', style=h10bB, command=lambda: self.peak_pick(spec='enriched'))
        plot_rs_B = ttk.Button(
            block_1, text='Plot', style=h8bB, command=lambda: self.plot_spectrum('rs'))
        plot_enriched_B = ttk.Button(
            block_1, text='Plot', style=h8bB, command=lambda: self.plot_spectrum('s'))
        calc_ratios_B = ttk.Button(
            block_1, text='Calculate Transition Ratios', style=h10bB,
            command=self.transition_scale_factor)

        filter_header = ttk.Label(block_1, text='3. Filter Peaks', **h14bL_c)
        freq_min_L = ttk.Label(block_1, text='Freq. Min.\n(MHz)', **h8bL_r)
        freq_max_L = ttk.Label(block_1, text='Freq. Max\n(MHz)', **h8bL_r)
        freq_match_L = ttk.Label(block_1, text='Freq. Match\n(MHz)', **h8bL_r)
        dyn_range_L = ttk.Label(block_1, text='Dynamic\nRange', **h8bL_r)
        j_max_L = ttk.Label(block_1, text='J max', **h8bL_r)
        ka_max_L = ttk.Label(block_1, text='Ka max', **h8bL_r)
        freq_min_E = ttk.Entry(block_1, textvariable=self.freq_min, **center)
        freq_max_E = ttk.Entry(block_1, textvariable=self.freq_max, **center)
        freq_match_E = ttk.Entry(block_1, textvariable=self.freq_match, **center)
        dyn_range_E = ttk.Entry(block_1, textvariable=self.dyn_range, **center)
        j_max_E = ttk.Entry(block_1, textvariable=self.j_max, **center)
        ka_max_E = ttk.Entry(block_1, textvariable=self.ka_max, **center)
        # ==========================================================================================
        sel_point_L.grid(row=1, column=0, columnspan=2, padx=5, pady=2)
        sel_freq_L.grid(row=2, column=0, **x5y2e)
        sel_int_L.grid(row=3, column=0, **x5y2e)
        sel_freq_E.grid(row=2, column=0 + 1, **x5y2ew)
        sel_int_E.grid(row=3, column=0 + 1, **x5y2ew)
        omit_B.grid(row=4, column=0, columnspan=2, **x5y2ew)
        reset_B.grid(row=5, column=0, columnspan=2, **x5y2ew)
        ttk.Separator(block_1, orient=v).grid(row=1, column=0 + 2, rowspan=5, **x30y5ns)
        ttk.Separator(block_1, orient=h).grid(row=0, column=0, columnspan=18, sticky='ew', padx=2)
        ttk.Separator(block_1, orient=h).grid(row=6, column=0, columnspan=18, **x2y5ew)
        # ==========================================================================================
        upload_header.grid(row=1, column=3, columnspan=4, padx=5, pady=15)
        rs_spec_L.grid(row=2, column=3, **x5y2e)
        rs_spec_E.grid(row=2, column=4, **x5y2ew)
        rs_browse.grid(row=2, column=5, **x5y2ew)
        plot_rs_B.grid(row=2, column=6, **x5y2ew)
        enriched_spec_L.grid(row=3, column=3, **x5y2e)
        enriched_spec_E.grid(row=3, column=4, **x5y2ew)
        enriched_browse.grid(row=3, column=5, **x5y2ew)
        plot_enriched_B.grid(row=3, column=6, **x5y2ew)
        dom_cat_L.grid(row=4, column=3, **x5y2e)
        dom_cat_E.grid(row=4, column=4, **x5y2ew)
        dom_browse.grid(row=4, column=5, **x5y2ew)
        minor_cat_L.grid(row=5, column=3, **x5y2e)
        minor_cat_E.grid(row=5, column=4, **x5y2ew)
        minor_browse.grid(row=5, column=5, **x5y2ew)
        ttk.Separator(block_1, orient=v).grid(row=1, column=7, rowspan=5, **x30y5ns)
        # ==========================================================================================
        pp_header.grid(row=1, column=8, columnspan=2, padx=5, pady=15, sticky='e')
        pp_L.grid(row=2, column=8, **x5y2e)
        pp_E.grid(row=2, column=9, **x5y2ew)
        pp_RS_B.grid(row=4, column=9, **x5y2ew)
        pp_enriched_B.grid(row=5, column=9, **x5y2ew)
        ttk.Separator(block_1, orient=v).grid(row=1, column=10, rowspan=5, **x30y5ns)
        # ==========================================================================================
        filter_header.grid(row=1, column=11, columnspan=4, padx=5, pady=15)
        freq_min_L.grid(row=2, column=11, **x5y2e)
        freq_max_L.grid(row=3, column=11, **x5y2e)
        freq_match_L.grid(row=4, column=11, **x5y2e)
        dyn_range_L.grid(row=2, column=13, **x5y2e)
        j_max_L.grid(row=3, column=13, **x5y2e)
        ka_max_L.grid(row=4, column=13, **x5y2e)
        calc_ratios_B.grid(row=5, column=11, columnspan=4, **x5y2ew)
        freq_min_E.grid(row=2, column=12, **x5y2ew)
        freq_max_E.grid(row=3, column=12, **x5y2ew)
        freq_match_E.grid(row=4, column=12, **x5y2ew)
        dyn_range_E.grid(row=2, column=14, **x5y2ew)
        j_max_E.grid(row=3, column=14, **x5y2ew)
        ka_max_E.grid(row=4, column=14, **x5y2ew)
        block_1.grid(row=3, column=0, padx=30, pady=20)
        # ==========================================================================================
        #                              Intensity Ratio Histograms and Block 2
        # ==========================================================================================
        self.dom_pm = PlotManager(
            frame=figure_2, figsize=(8, 5), dpi=100, subplotshape=111, zoom_mode=0,
            plot_title='Dominant Analysis', xlabel='R', ylabel='Number of Occurrences',
            x_min='Auto', x_max='Auto', y_min='Auto', y_max='Auto', legend_show=False, left=0.1,
            right=0.98, top=0.92, bottom=0.1, row=0, column=0, sticky='ew', toolbar=True, toolrow=1,
            toolcol=0, toolpady=2, toolsticky='w')

        self.minor_pm = PlotManager(
            frame=figure_2, figsize=(8, 5), dpi=100, subplotshape=111, zoom_mode=0,
            plot_title='Minor Analysis', xlabel='R', ylabel='Number of Occurrences', x_min='Auto',
            x_max='Auto', y_min='Auto', y_max='Auto', legend_show=False, left=0.1, right=0.98,
            top=0.92, bottom=0.1, row=0, column=1, sticky='ew', toolbar=True, toolrow=1, toolcol=1,
            toolpady=2, toolsticky='w')
        figure_2.grid(row=4, column=0, rowspan=1, pady=0)

        filter_hists_L = ttk.Label(block_2, text='4. Filter by Intensity Ratio', **h14bL_c)
        dom_min_L = ttk.Label(block_2, text='Dominant\nMinimum', **h8bL_r)
        dom_max_L = ttk.Label(block_2, text='Dominant\nMaximum', **h8bL_r)
        minor_min_L = ttk.Label(block_2, text='Minor\nMinimum', **h8bL_r)
        minor_max_L = ttk.Label(block_2, text='Minor\nMaximum', **h8bL_r)
        dom_min_E = ttk.Entry(block_2, textvariable=self.dom_min, **center)
        dom_max_E = ttk.Entry(block_2, textvariable=self.dom_max, **center)
        minor_min_E = ttk.Entry(block_2, textvariable=self.minor_min, **center)
        minor_max_E = ttk.Entry(block_2, textvariable=self.minor_max, **center)
        rough_filter_dom = ttk.Button(
            block_2, text='3\u03C3 Filter', style=h10bB, command=self.filter_dominant)
        rough_filter_min = ttk.Button(
            block_2, text='3\u03C3 Filter', style=h10bB, command=self.filter_minor)
        filter_hists_L.grid(row=1, column=5, pady=15)
        rough_filter_dom.grid(row=2, column=0, padx=20, pady=2)
        dom_min_L.grid(row=2, column=1, **x2y2)
        dom_min_E.grid(row=2, column=2, **x2y2)
        dom_max_L.grid(row=2, column=3, **x2y2)
        dom_max_E.grid(row=2, column=4, **x2y2)
        rough_filter_min.grid(row=2, column=6, padx=20, pady=2)
        minor_min_L.grid(row=2, column=7, **x2y2)
        minor_min_E.grid(row=2, column=8, **x2y2)
        minor_max_L.grid(row=2, column=9, **x2y2)
        minor_max_E.grid(row=2, column=10, **x2y2)
        ttk.Separator(block_2, orient=h).grid(row=0, column=0, columnspan=11, sticky='ew', padx=2)
        ttk.Separator(block_2, orient=h).grid(row=4, column=0, columnspan=11, **x2y5ew)
        block_2.grid(row=5, column=0, pady=20)
        # ==========================================================================================
        #                          Enantiomeric Excess Histogram and Block 3
        # ==========================================================================================
        hist_params_L = ttk.Label(block_3, text='5. Histogram Parameters', **h14bL_c)
        topN_L = ttk.Label(block_3, text='Top N', **h8bL_r)
        topN_E = ttk.Entry(block_3, textvariable=self.topN, **center)
        tag_ee_L = ttk.Label(block_3, text='Tag ee', **h8bL_r)
        tag_ee_E = ttk.Entry(block_3, textvariable=self.tag_ee, **center)
        bins_L = ttk.Label(block_3, text='Number\nof Bins', **h8bL_r)
        num_bins_E = ttk.Entry(block_3, textvariable=self.num_bins, **center)
        color_L = ttk.Label(block_3, text='Color', **h8bL_r)
        color_E = ttk.OptionMenu(
            block_3, self.color, 'blue', 'black', 'red', 'green', 'cyan', 'purple', 'lime', 'gold',
            'teal', 'salmon', 'darkblue', 'sienna', style="TMenubutton")
        border_L = ttk.Label(block_3, text='Border', **h8bL_r)
        border_checkbox = ttk.Checkbutton(block_3, variable=self.border)
        legend_L = ttk.Label(block_3, text='Stats. Label', **h8bL_r)
        legend_checkbox = ttk.Checkbutton(block_3, variable=self.label)
        mean_line_L = ttk.Label(block_3, text='Plot Mean', **h8bL_r)
        mean_line_checkbox = ttk.Checkbutton(block_3, variable=self.mean_line)
        calc_ee_B = ttk.Button(block_3, text='Calculate EE', style=h10bB, command=self.calc_ee)

        results_L = ttk.Label(block_3, text='6. Results', **h14bL_c)
        value_L = ttk.Label(block_3, text='Output Value', **h8bL_c)
        stats_L = ttk.Label(block_3, text='Label', **h8bL_c)
        mean_ee_L = ttk.Label(block_3, text='e\u0305e\u0305', **h8bL_r)
        mean_ee_E = ttk.Entry(block_3, textvariable=self.mean_ee, **center)
        legend_mean_ee_checkbox = ttk.Checkbutton(block_3, variable=self.legend_mean_ee)
        stdev_ee_L = ttk.Label(block_3, text='\u03C3\u00B2\u2091\u2091', **h8bL_r)
        stdev_ee_E = ttk.Entry(block_3, textvariable=self.stdev_ee, **center)
        legend_stdev_ee_checkbox = ttk.Checkbutton(block_3, variable=self.legend_stdev_ee)
        stderr_ee_L = ttk.Label(block_3, text='\u03C3\u00B2 / \u221A(top N)', **h8bL_r)
        stderr_ee_E = ttk.Entry(block_3, textvariable=self.stderr_ee, **center)
        legend_stderr_ee_checkbox = ttk.Checkbutton(block_3, variable=self.legend_stderr_ee)
        max_ee_L = ttk.Label(block_3, text='Max ee', **h8bL_r)
        max_ee_E = ttk.Entry(block_3, textvariable=self.max_ee, **center)
        legend_max_ee_checkbox = ttk.Checkbutton(block_3, variable=self.legend_max_ee)
        min_ee_L = ttk.Label(block_3, text='Min ee', **h8bL_r)
        min_ee_E = ttk.Entry(block_3, textvariable=self.min_ee, **center)
        legend_min_ee_checkbox = ttk.Checkbutton(block_3, variable=self.legend_min_ee)
        save_output_B = ttk.Button(
            block_3, text='Save Outputs', style=h10bB, command=self.save_results)
        adjust_axes_L = ttk.Label(block_3, text='7. Adjust Axes', **h14bL_c)
        plot_title_L = ttk.Label(block_3, text='Plot Title', **h8bL_r)
        plot_title_E = ttk.Entry(block_3, textvariable=self.plot_title, **center)
        x_title_L = ttk.Label(block_3, text='X Title', **h8bL_r)
        x_title_E = ttk.Entry(block_3, textvariable=self.xlabel, **center)
        y_title_L = ttk.Label(block_3, text='Y Title', **h8bL_r)
        y_title_E = ttk.Entry(block_3, textvariable=self.ylabel, **center)
        xmin_L = ttk.Label(block_3, text='X Min', **h8bL_r)
        xmin_E = ttk.Entry(block_3, textvariable=self.xmin, **center)
        xmax_L = ttk.Label(block_3, text='X Max', **h8bL_r)
        xmax_E = ttk.Entry(block_3, textvariable=self.xmax, **center)
        ymin_L = ttk.Label(block_3, text='Y Min', **h8bL_r)
        ymin_E = ttk.Entry(block_3, textvariable=self.ymin, **center)
        ymax_L = ttk.Label(block_3, text='Y Max', **h8bL_r)
        ymax_E = ttk.Entry(block_3, textvariable=self.ymax, **center)
        update_hist_B = ttk.Button(
            block_3, text='Update Histogram', style=h10bB, command=self.plot_ee)
        self.ee_pm = PlotManager(
            frame=figure_3, figsize=(16, 6), dpi=100, subplotshape=111,
            plot_title=self.plot_title.get(), xlabel=self.xlabel.get(), ylabel=self.ylabel.get(),
            x_min=self.xmin.get(), x_max=self.xmax.get(), y_min=self.ymin.get(),
            y_max=self.ymax.get(), legend_show=False, legend_font=10, legend_loc=1, label_show=True,
            label_list=[], left=0.15, right=0.85, top=0.94, bottom=0.08, row=0, column=0,
            toolbar=True, toolrow=1, toolcol=0, toolpady=5, toolsticky='w')
        figure_3.grid(row=6, column=0)
        ttk.Separator(block_3, orient=h).grid(row=0, column=0, columnspan=11, **x2y5ew)
        # ==========================================================================================
        hist_params_L.grid(row=1, column=0, columnspan=2, **x5y10)
        topN_L.grid(row=2, column=0, **x2y2e)
        tag_ee_L.grid(row=3, column=0, **x2y2e)
        bins_L.grid(row=4, column=0, **x2y2e)
        color_L.grid(row=5, column=0, **x2y2e)
        border_L.grid(row=6, column=0, **x2y2e)
        legend_L.grid(row=7, column=0, **x2y2e)
        mean_line_L.grid(row=8, column=0, **x2y2e)
        topN_E.grid(row=2, column=1, **x2y2ew)
        tag_ee_E.grid(row=3, column=1, **x2y2ew)
        num_bins_E.grid(row=4, column=1, **x2y2ew)
        color_E.grid(row=5, column=1, **x2y2ew)
        border_checkbox.grid(row=6, column=1, **x2y2)
        legend_checkbox.grid(row=7, column=1, **x2y2)
        mean_line_checkbox.grid(row=8, column=1, **x2y2)
        calc_ee_B.grid(row=9, column=0, rowspan=2, columnspan=2, **x5y5nsew)
        ttk.Separator(block_3, orient=v).grid(row=1, column=2, rowspan=10, **x30y5ns)
        # ==========================================================================================
        results_L.grid(row=1, column=3, columnspan=3, **x5y10)
        value_L.grid(row=2, column=4, padx=5)
        stats_L.grid(row=2, column=5, padx=2)
        mean_ee_L.grid(row=3, column=3, **x2y2e)
        stdev_ee_L.grid(row=4, column=3, **x2y2e)
        stderr_ee_L.grid(row=5, column=3, **x2y2e)
        max_ee_L.grid(row=6, column=3, **x2y2e)
        min_ee_L.grid(row=7, column=3, **x2y2e)
        mean_ee_E.grid(row=3, column=4, **x2y2ew)
        stdev_ee_E.grid(row=4, column=4, **x2y2ew)
        stderr_ee_E.grid(row=5, column=4, **x2y2ew)
        max_ee_E.grid(row=6, column=4, **x2y2ew)
        min_ee_E.grid(row=7, column=4, **x2y2ew)
        legend_mean_ee_checkbox.grid(row=3, column=5, **x2y2)
        legend_stdev_ee_checkbox.grid(row=4, column=5, **x2y2)
        legend_stderr_ee_checkbox.grid(row=5, column=5, **x2y2)
        legend_max_ee_checkbox.grid(row=6, column=5, **x2y2)
        legend_min_ee_checkbox.grid(row=7, column=5, **x2y2)
        save_output_B.grid(row=9, column=3, rowspan=2, columnspan=3, **x5y5nsew)
        ttk.Separator(block_3, orient=v).grid(row=1, column=6, rowspan=10, **x30y5ns)
        # ==========================================================================================
        adjust_axes_L.grid(row=1, column=7, columnspan=2, **x2y2)
        plot_title_L.grid(row=2, column=7, **x2y2e)
        x_title_L.grid(row=3, column=7, **x2y2e)
        y_title_L.grid(row=4, column=7, **x2y2e)
        xmin_L.grid(row=5, column=7, **x2y2e)
        xmax_L.grid(row=6, column=7, **x2y2e)
        ymin_L.grid(row=7, column=7, **x2y2e)
        ymax_L.grid(row=8, column=7, **x2y2e)
        plot_title_E.grid(row=2, column=8, **x2y2e)
        x_title_E.grid(row=3, column=8, **x2y2e)
        y_title_E.grid(row=4, column=8, **x2y2e)
        xmin_E.grid(row=5, column=8, **x2y2ew)
        xmax_E.grid(row=6, column=8, **x2y2ew)
        ymin_E.grid(row=7, column=8, **x2y2ew)
        ymax_E.grid(row=8, column=8, **x2y2ew)
        update_hist_B.grid(row=9, column=7, rowspan=2, columnspan=2, **x5y5nsew)
        ttk.Separator(block_3, orient=v).grid(row=1, column=9, rowspan=10, **x30y5ns)
        # ==========================================================================================
        notes_L = ttk.Label(block_3, text='Notes', **h14bL_c)
        self.notes_textbox = tk.Text(block_3, height=8, relief='sunken', font=h10, wrap=tk.WORD)
        notes_L.grid(row=1, column=10, **x5y10, sticky='w')
        self.notes_textbox.grid(row=2, column=10, rowspan=7, padx=2, pady=2, sticky='nsew')
        self.notes_textbox.delete('1.0', tk.END)
        self.notes_textbox.insert('1.0', 'None')
        ttk.Separator(block_3, orient=h).grid(row=11, column=0, columnspan=11, sticky='ew', **x2y15)
        block_3.grid(row=7, column=0)
        self.attr_dict = {
            'sel_freq': self.sel_freq, 'sel_int': self.sel_int, 'dom_cat': self.dom_cat,
            'species2_cat': self.minor_cat, 'rs_spec': self.rs_spec, 'spec1': self.enriched_spec,
            'pp_thresh': self.pp_thresh, 'freq_min': self.freq_min, 'freq_max': self.freq_max,
            'freq_match': self.freq_match, 'dyn_range': self.dyn_range, 'j_max': self.j_max,
            'ka_max': self.ka_max, 'dom_min': self.dom_min, 'dom_max': self.dom_max,
            'minor_min': self.minor_min, 'minor_max': self.minor_max, 'topN': self.topN,
            'tag_ee': self.tag_ee, 'num_bins': self.num_bins, 'color': self.color,
            'border': self.border, 'mean_ee': self.mean_ee, 'stdev_ee': self.stdev_ee,
            'stderr_ee': self.stderr_ee, 'max_ee': self.max_ee, 'min_ee': self.min_ee,
            'legend': self.label, 'mean_line': self.mean_line,
            'legend_mean_ee': self.legend_mean_ee, 'legend_stdev_ee': self.legend_stdev_ee,
            'legend_stderr_ee': self.legend_stderr_ee, 'legend_max_ee': self.legend_max_ee,
            'legend_min_ee': self.legend_min_ee, 'plot_title': self.plot_title,
            'x_title': self.xlabel, 'y_title': self.ylabel, 'xmin': self.xmin, 'xmax': self.xmax,
            'ymin': self.ymin, 'ymax': self.ymax, 'omitted_points': self.tk_omitted_points}
        self.text_box_dict = {'notes': self.notes_textbox}
        self.page.enter_textbox(self.notes_textbox)
        self.page.exit_textbox(self.notes_textbox)

    def plot_spectrum(self, spec=None):
        """
        Plot spec and remove all other series from plot.

        Parameters:
            spec (str):
                Options: racemic, rs, enriched, enantioenriched, enantiopure, r, s
        """
        if spec in ['racemic', 'rs']:
            spec = Spectrum(self.rs_spec.get()).spectrum
            spec_legend = 'Racemic Spectrum'
        elif spec in ['enriched', 'enantioenriched', 'enantiopure', 'r', 's']:
            spec = Spectrum(self.enriched_spec.get()).spectrum
            spec_legend = 'Enantioenriched Spectrum'
        else:
            return
        self.spec_pm.ax.cla()
        self.spec_pm.plot_line(
            spec[:, 0], spec[:, 1], color='black', label=spec_legend, picker=self.controller.picker)
        self.spec_pm.set_labels()
        self.spec_pm.zoom()
        self.spec_pm.canvas.draw()
        self.spec_pm.toolbar.update()

    def peak_pick(self, spec=None):
        """
        Identify peaks in spectrum, save temporary file, mark peaks on spectrum and display on plot.

        Parameters:
            spec (str):
                Options: racemic, rs, enriched, enantioenriched, enantiopure, r, s
        Saved temporary files to 'temp' subdirectory:
            'peak_pick_racemic.npy' (binary array):
                Peak pick of the racemic spectrum.
                Shape: (# of transitions , 2)
                col[0] -> freq
                col[1] -> intensity
            'peak_pick_enriched.npy' (binary array):
                Peak pick of the enantioenriched spectrum.
                Shape: (# of transitions , 2)
                col[0] -> freq
                col[1] -> intensity
        """
        if spec in ['racemic', 'rs']:
            spec = Spectrum(self.rs_spec.get())
            spectrum = spec.spectrum
            fname = 'peak_pick_racemic'
            spec_legend = 'Racemic Spectrum'
            self.rs_pp_lock.set(0)
        elif spec in ['enriched', 'enantioenriched', 'enantiopure', 'r', 's']:
            spec = Spectrum(self.enriched_spec.get())
            spectrum = spec.spectrum
            fname = 'peak_pick_enriched'
            spec_legend = 'Enantioenriched Spectrum'
            self.enriched_pp_lock.set(0)
        else:
            return
        pp = spec.peak_pick(thresh=float("{0:.4f}".format(float(self.pp_thresh.get()))), sort=True)
        self.spec_pm.ax.cla()
        self.spec_pm.plot_line(
            spectrum[:, 0], spectrum[:, 1], color='black', label=spec_legend, picker=self.controller.picker)
        self.spec_pm.plot_line(
            pp[:, 0], pp[:, 1], color='red', marker='o', weight=0, label='Peak Pick')
        self.spec_pm.set_labels()
        self.spec_pm.zoom()
        self.spec_pm.canvas.draw()
        self.spec_pm.toolbar.update()
        self.page.save_temp_file(fname, pp)

    def transition_scale_factor(self):
        """
        Run transition_scale_factor() using 'peak_pick_racemic.npy' and 'peak_pick_enriched.npy'.

        Saved temporary files:
            'diastereomer_1_analysis.npy' (binary array):
                Racemic/enantioenriched intensity ratio of diastereomer 1.
                Shape: (# of transitions , 4)
                col[0] -> freq
                col[1] -> intensity in racemic spectrum
                col[2] -> intensity in enantioenriched spectrum.
                col[3] -> col[2] / col[1]
            'diastereomer_2_analysis.npy' (binary array):
                racemic/enantioenriched intensity ratio of diastereomer 2.
                Shape: (# of transitions , 4)
                col[0] -> freq
                col[1] -> intensity in racemic spectrum
                col[2] -> intensity in enantioenriched spectrum.
                col[3] -> col[2] / col[1]
        """
        if self.rs_pp_lock.get():
            showerror(
                'Error',
                message='Perform peak pick on racemic spectrum before proceeding to this step.')
            return
        elif self.enriched_pp_lock.get():
            showerror(
                'Error',
                message='Perform peak pick on enriched spectrum before proceeding to this step.')
            return
        else:
            self.calc_ratios_lock.set(0)
        freq_min = float(self.freq_min.get())
        freq_max = float(self.freq_max.get())
        freq_match = float(self.freq_match.get())
        jmax = int(self.j_max.get())
        ka_max = int(self.ka_max.get())
        dyn_range = float(self.dyn_range.get())

        rs_pp = self.page.load_temp_file('peak_pick_racemic.npy')
        enriched_pp = self.page.load_temp_file('peak_pick_enriched.npy')

        dom_analysis, minor_analysis = transition_scale_factor(
            self.enriched_spec.get(), self.rs_spec.get(), enriched_pp, rs_pp, freq_match,
            species1_cat=self.dom_cat.get(), species2_cat=self.minor_cat.get(),
            freq_min=freq_min, freq_max=freq_max, jmax=jmax, ka_max=ka_max, dyn_range=dyn_range)
        self.dom_pm.histogram(dom_analysis[:, 3], bins=20, border=True, plot_mean=False)
        self.dom_pm.set_labels()
        self.dom_pm.canvas.draw()
        self.minor_pm.histogram(minor_analysis[:, 3], bins=20, border=True, plot_mean=False)
        self.minor_pm.set_labels()
        self.minor_pm.canvas.draw()
        self.page.save_temp_file('diastereomer_1_analysis', dom_analysis)
        self.page.save_temp_file('diastereomer_2_analysis', minor_analysis)

    def filter_dominant(self):
        """
        Remove rows from 'diastereomer_1_analysis.npy' with R value greater than
        3 s.d. away from mean.
        """
        r_analysis = self.page.load_temp_file('diastereomer_1_analysis.npy')
        filtered = sigma_filter(r_analysis, col=3, sigma_multiplier=3)
        self.page.save_temp_file('diastereomer_1_analysis', filtered)
        self.dom_pm.ax.cla()
        self.dom_pm.histogram(filtered[:, 3], bins=20, border=True, plot_mean=False)
        self.dom_pm.set_labels()
        self.dom_pm.canvas.draw()

    def filter_minor(self):
        """
        Remove rows from 'diastereomer_2_analysis.npy' with R value greater than
        3 s.d. away from mean.
        """
        r_analysis = self.page.load_temp_file('diastereomer_2_analysis.npy')
        filtered = sigma_filter(r_analysis, col=3, sigma_multiplier=3)
        self.page.save_temp_file('diastereomer_2_analysis', filtered)
        self.minor_pm.ax.cla()
        self.minor_pm.histogram(filtered[:, 3], bins=20, border=True, plot_mean=False)
        self.minor_pm.set_labels()
        self.minor_pm.canvas.draw()

    @testing.collect_garbage
    def calc_ee(self):
        """
        Calculate EE using 'diastereomer_1_analysis.npy' and 'diastereomer_2_analysis.npy'

        1.  Open 'diastereomer_1_analysis.npy' and 'diastereomer_2_analysis.npy'
        2.  Open *.cat files if provided.
        3.  Filter *.cat files.
        4.  Simulate filtered *.cat files and scale to roughly match the experimental intensity.
        5.  Calculate EE.
        6.  Generate histogram with EE calculations of all possible transition pairs (topN^2).
        7.  Mark transitions used in the EE calculation on the racemic spectrum at the top
            of the page, color coded by diastereomer.
        8.  Invert simulations and plot with the enriched spectrum at the top of the page.

        Saved temporary files:
            'topN_dominant.npy' (binary array):
                Transition intensity data for Top N the strongest transitions
                from 'diastereomer_1_analysis.npy'
                Shape: (Top N , 4)
                col[0] -> freq
                col[1] -> intensity in racemic spectrum
                col[2] -> intensity in enantioenriched spectrum.
                col[3] -> col[2] / col[1]
            'topN_minor.npy' (binary array):
                Transition intensity data for Top N the strongest transitions
                from 'diastereomer_2_analysis.npy'
                Shape: (Top N , 4)
                col[0] -> freq
                col[1] -> intensity in racemic spectrum
                col[2] -> intensity in enantioenriched spectrum.
                col[3] -> col[2] / col[1]
            'ee_histogram.npy' (binary array):
                Individual EE calculations using transition pairs.
                Shape: (topN^2 , )
        """
        if self.rs_pp_lock.get():
            showerror(
                'Error',
                message='Perform peak pick on racemic spectrum before proceeding to this step.')
            return
        elif self.enriched_pp_lock.get():
            showerror(
                'Error',
                message='Perform peak pick on enriched spectrum before proceeding to this step.')
            return
        elif self.calc_ratios_lock.get():
            showerror(
                'Error',
                message='Calculate intensity ratios before proceeding to this step.')
            return
        else:
            self.calc_ee_lock.set(0)
        fmin = self.freq_min.get()
        fmax = self.freq_max.get()
        jmax = self.j_max.get()
        ka_max = self.ka_max.get()
        dr = self.dyn_range.get()
        topN = self.topN.get()
        tag_ee = self.tag_ee.get()
        dom_min = self.dom_min.get()
        dom_max = self.dom_max.get()
        minor_min = self.minor_min.get()
        minor_max = self.minor_max.get()
        rs = Spectrum(self.rs_spec.get())
        enriched = Spectrum(self.enriched_spec.get())
        enriched_spec = enriched.spectrum

        dom = self.page.load_temp_file('diastereomer_1_analysis.npy')
        minor = self.page.load_temp_file('diastereomer_2_analysis.npy')
        dom_cat = self.dom_cat.get()
        minor_cat = self.minor_cat.get()

        if self.tk_omitted_points.get() != 'None':
            omitted_points = page_funcs.format_omitted_points(self.tk_omitted_points)
        else:
            omitted_points = []
        if dom_cat != 'None' and minor_cat != 'None':
            dom_cat = Cat(dom_cat)
            dom_filter = dom_cat.filter(
                freq_min=fmin, freq_max=fmax, N_max=jmax, Ka_max=ka_max, dyn_range=dr)
            dom_lnlst_filter = dom_cat.line_list(dictionary=dom_filter)
            asn = [float("{:.4f}".format(dom[x, 0])) for x in range(len(dom))]
            scale_dom = dom_cat.scale_to_spectrum(rs, asn, dictionary=dom_filter)
            dom_sim = dom_cat.simulate(line_list=dom_lnlst_filter)
            dom_sim = np.column_stack((dom_sim[:, 0], dom_sim[:, 1] * scale_dom))

            minor_cat = Cat(minor_cat)
            minor_filter = minor_cat.filter(
                freq_min=fmin, freq_max=fmax, N_max=jmax, Ka_max=ka_max, dyn_range=dr)
            minor_lnlst_filter = minor_cat.line_list(dictionary=minor_filter)
            asn = [float("{:.4f}".format(minor[x, 0])) for x in range(len(minor))]
            scale_minor = minor_cat.scale_to_spectrum(rs, asn, dictionary=minor_filter)
            minor_sim = minor_cat.simulate(line_list=minor_lnlst_filter)
            minor_sim = np.column_stack((minor_sim[:, 0], minor_sim[:, 1] * scale_minor))
        ee, topN_dom, topN_minor = calculate_ee(
            dom, minor, topN=topN, tag_ee=tag_ee, rmin1=dom_min, rmax1=dom_max, rmin2=minor_min,
            rmax2=minor_max, omitted_points=omitted_points)
        self.page.save_temp_file('topN_dominant', topN_dom)
        self.page.save_temp_file('topN_minor', topN_minor)
        self.page.save_temp_file('ee_histogram', ee)
        self.plot_ee()

        start_freq = float("{0:.4f}".format(enriched.freq_min))
        step_size = float("{0:.4f}".format(enriched.point_spacing))
        row_num_dom = [
            int(round((topN_dom[x, 0] - start_freq) / step_size)) for x in range(len(topN_dom))]
        row_num_minor = [
            int(round((topN_minor[x, 0] - start_freq) / step_size)) for x in range(len(topN_minor))]
        row_num_omitted = [int(round((point - start_freq) / step_size)) for point in omitted_points]

        self.spec_pm.ax.cla()
        self.spec_pm.plot_line(
            enriched_spec[:, 0], enriched_spec[:, 1], weight=0.75, color='black',
            label='Enriched Spectrum', picker=self.controller.picker)
        self.spec_pm.plot_line(
            enriched_spec[row_num_dom, 0], enriched_spec[row_num_dom, 1], weight=0, marker='.',
            color='red', label='Dominant Peaks')
        self.spec_pm.plot_line(
            enriched_spec[row_num_minor, 0], enriched_spec[row_num_minor, 1], weight=0, marker='.',
            color='blue', label='Minor Peaks')
        self.spec_pm.plot_line(
            dom_sim[:, 0], dom_sim[:, 1], invert=1, weight=0.75, color='red',
            label='Dominant Simulation', picker=self.controller.picker)
        self.spec_pm.plot_line(
            minor_sim[:, 0], minor_sim[:, 1], invert=1, weight=0.75, color='blue',
            label='Minor Simulation', picker=self.controller.picker)
        try:
            self.spec_pm.plot_line(
                enriched.spectrum[row_num_omitted, 0], enriched.spectrum[row_num_omitted, 1],
                weight=0, invert=0, marker='x', color='C2', label='omitted')
        except IndexError:
            pass
        self.spec_pm.set_labels()
        self.spec_pm.zoom()
        self.spec_pm.canvas.draw()
        self.spec_pm.toolbar.update()

    def plot_ee(self):
        """ Plot EE histogram along with labels. """
        ee = self.page.load_temp_file('ee_histogram.npy')
        mean_ee = float("{0:.5f}".format(np.mean(ee)))
        stdev_ee = float("{0:.5f}".format(np.std(ee)))
        stderr_ee = float("{0:.5f}".format(stdev_ee / self.topN.get() ** 0.5))
        max_ee = float("{0:.5f}".format(max(ee)))
        min_ee = float("{0:.5f}".format(min(ee)))
        self.mean_ee.set(mean_ee)
        self.stdev_ee.set(stdev_ee)
        self.stderr_ee.set(stderr_ee)
        self.max_ee.set(max_ee)
        self.min_ee.set(min_ee)

        if self.label.get():
            label_list = []
            for label, show, var in [
                (r'$\mathrm{\bar x}=%.4f$', self.legend_mean_ee.get(), mean_ee),
                (r'$\mathrm{\sigma}=%.4f$', self.legend_stdev_ee.get(), stdev_ee),
                (r'$\mathrm{\sigma/\sqrt{n}}=%.4f$', self.legend_stderr_ee.get(), stderr_ee),
                (r'$\mathrm{max}=%.4f$', self.legend_max_ee.get(), max_ee),
                (r'$\mathrm{min}=%.4f$', self.legend_min_ee.get(), min_ee)]:
                if show:
                    label_list.append(label % (var,))
        else:
            label_list = []
        self.ee_pm.ax.cla()
        self.ee_pm.histogram(
            ee, bins=self.num_bins.get(), border=self.border.get(), color=self.color.get(),
            plot_mean=self.mean_line.get(), toolbar=True)
        self.ee_pm.set_labels(
            plot_title=self.plot_title.get(), xlabel=self.xlabel.get(), ylabel=self.ylabel.get(),
            label_list=label_list)
        self.ee_pm.zoom(
            xmin=self.xmin.get(), xmax=self.xmax.get(), ymin=self.ymin.get(), ymax=self.ymax.get())
        self.ee_pm.canvas.draw()
        self.ee_pm.toolbar.update()

    def save_results(self):
        """
        Save set of summary files.

        Save files with a user provided name functioning as the base name for all files.
        Descriptor words are concatenated with the base name to differentiate the files.

        Files saved:
            '{base_name}_summary.txt' (*.txt):
                All labels and entrybox values from GUI.
            '{base_name}_dominant_diastereomer.csv' (DataFrame):
                Transition intensity data for Top N the strongest transitions
                from 'diastereomer_1_analysis.npy'
                Shape:
                    If loading into Excel: (Top N , 5)
                    If loading into DataFrame: (Top N , 4)
                col[0] -> index (only relevant if loading into Excel)
                col[1] -> freq
                col[2] -> intensity in racemic spectrum
                col[3] -> intensity in enantioenriched spectrum.
                col[4] ->col[2] / col[1]
            '{base_name}_minor_diastereomer.csv' (DataFrame):
                Transition intensity data for Top N the strongest transitions
                from 'diastereomer_2_analysis.npy'
                Shape:
                    If loading into Excel: (Top N , 5)
                    If loading into DataFrame: (Top N , 4)
                col[0] -> index (only relevant if loading into Excel)
                col[1] -> freq
                col[2] -> intensity in racemic spectrum
                col[3] -> intensity in enantioenriched spectrum.
                col[4] -> col[2] / col[1]
            '{base_name}_ee_calculations.csv' (DataFrame):
                Individual EE calculations using transition pairs.
                Shape: (topN^2 , )
        """
        if self.calc_ee_lock.get():
            showerror('Error', message='Perform EE calc. before proceeding to this step.')
            return
        else:
            omitted_points = page_funcs.format_omitted_points(self.tk_omitted_points)
            attribute_get_dict = {}
            for key, val in self.attr_dict.items():
                attribute_get_dict[key] = val.get()
            parameter_list = [['Input Parameters', '\n'],
                              ['Path to racemic spectrum:  ', attribute_get_dict["rs_spec"]],
                              ['Path to enriched spectrum:  ', attribute_get_dict["spec1"]],
                              ['Path to dominant cat:  ', attribute_get_dict["dom_cat"]],
                              ['Path to non-dominant cat:  ', attribute_get_dict["species2_cat"]],
                              ['Frequency minimum:  ', attribute_get_dict["freq_min"]],
                              ['Frequency maximum:  ', attribute_get_dict["freq_max"]],
                              ['Frequency match:  ', attribute_get_dict["freq_match"]],
                              ['J max:  ', attribute_get_dict["j_max"]],
                              ['ka max:  ', attribute_get_dict["ka_max"]],
                              ['Dynamic range:  ', attribute_get_dict["dyn_range"]],
                              ['Top N:  ', attribute_get_dict["topN"]],
                              ['Tag ee:  ', attribute_get_dict["tag_ee"]],
                              ['Dominant minimum:  ', attribute_get_dict["dom_min"]],
                              ['Dominant maximum:  ', attribute_get_dict["dom_max"]],
                              ['Non-dominant minimum:  ', attribute_get_dict["minor_min"]],
                              ['Non-dominant maximum:  ', attribute_get_dict["minor_max"]],
                              ['\n', ''],
                              ['Results', '\n'],
                              ['Mean ee:  ', attribute_get_dict["mean_ee"]],
                              ['Std. dev. ee:  ', attribute_get_dict["stdev_ee"]],
                              ['Std. dev. / sqrt(top N):  ', attribute_get_dict["stderr_ee"]],
                              ['Maximum ee:  ', attribute_get_dict["max_ee"]],
                              ['Minimum ee:  ', attribute_get_dict["min_ee"]]]
            fname = page_funcs.save_file(
                initialdir=os.path.dirname(self.rs_spec.get()), ftype='.txt',
                defaultextension='.txt')
            fname = os.path.splitext(fname)[0]
            with open(fname + '_summary.txt', 'w') as f:
                for text, var in parameter_list:
                    f.write('%s %s \n' % (text, var))
                f.write('User omitted point:  %s\n' % omitted_points)

            columns = np.array(
                ('Frequency (MHz)', 'Intensity Racemic (mV)', 'Intensity Enriched (mV)', 'Ratio'))
            topN_dom = self.page.load_temp_file('topN_dominant.npy')
            dom_df = pd.DataFrame(topN_dom, columns=columns)
            dom_df.to_csv(fname + '_dominant_diastereomer.csv')

            topN_minor = self.page.load_temp_file('topN_minor.npy')
            minor_df = pd.DataFrame(topN_minor, columns=columns)
            minor_df.to_csv(fname + '_minor_diastereomer.csv')

            ee_calcs = self.page.load_temp_file('ee_histogram.npy')
            ee_df = pd.DataFrame(ee_calcs)
            ee_df.to_csv(fname + '_ee_calculations.csv')


def transition_scale_factor(spec1, spec2, spec1_pp, spec2_pp, freq_match=None, species1_cat=None,
                            species2_cat=None, **cat_filter):
    """
    Calculate (intensity in spec1 / intensity in spec2) for specified transitions.

    Use for a pair of diastereomeric clusters within an EE calculation. Calculate the intensity
    ratio of each transition in spec1 relative to spec2 for the two species.

    Provide *.cat files for diastereomer clusters if possible.

    If two spectra are collected using equivalent excitation parameters, the observed intensity of
    the spectrum can vary for a number of reasons. However, the intensity of transitions belonging
    to a molecular species should scale proportionally to other transitions from that species.
    Significant deviation from the expected intensity ratio helps identify transitions that should
    be excluded from analytical calculations.

    Two ways to use this function.
    1.  Preferred method is to provide species1_cat and species2_cat. By providing these files,
        distinguishing between transitions of the dominant and minor species is settled from the
        beginning, which results in better filtering.
    2.  Without species1_cat and species2_cat, the peak pick thresholds are very important because
        species1 and species2 are distinguished by peaks from spec2_pp that are not in spec1_pp.
        This becomes problematic if the sample is not of high enantiopurity. If the sample is of
        high enantioimpurity, the diastereomers can be distinguished since the spectral intensity of
        the minor diastereomer will be lowered close to baseline in the enantioenriched
        spectrum. If the sample is not of high enantiopurity, the spectrum of the minor diastereomer
        in the enantioenriched spectrum still could be of comparable strength to the major
        diastereomer. If this is the case, it may be impossible to select a peak pick threshold that
        removes the spectrum of one diastereomer from the enantioenriched spectrum.

    Parameters:
        spec1 (str):
            File path to spectrum. (Enriched spectrum)
        spec2 (str):
            File path to spectrum. (RS spectrum)
        spec1_pp (array):
            Peak pick.
            Col[0] -> Freq.
            Col[1] -> Intensity.
        spec2_pp (array):
            Peak pick.
            Col[0] -> Freq.
            Col[1] -> Intensity.
        species1_cat (str):
            File path to *.cat file. (Dominant species)
        species2_cat (str):
            File path to *.cat file. (Minor species)
        freq_match (float):
            Frequency threshold. Maximum delta freq. for a predicted peak to be deemed a match with
            a peak in spectrum.
            Units: MHz
            Default:  0.020
        **cat_filter(dict):
            Kwargs to filter peaks from cat.
    Returns:
        dom_analysis (array):
            Dominant species intensity ratio (racemic/enantioenriched).
            Shape: (# of transitions , 4)
            Col[0] -> Frequency
            Col[1] -> Intensity in racemic spectrum
            Col[2] -> Intensity in enriched spectrum
            Col[3] -> col[2] / col[1]
        minor_analysis (array):
            Minor species intensity ratio (racemic/enantioenriched).
            Shape: (# of transitions , 4)
            Col[0] -> Frequency
            Col[1] -> Intensity in racemic spectrum
            Col[2] -> Intensity in enriched spectrum
            Col[3] -> col[2] / col[1]
    """
    spec1 = Spectrum(spec1)
    spec2 = Spectrum(spec2)
    if species1_cat is not None and species2_cat is not None:
        if freq_match is None:
            freq_match = 0.020
        species1_cat = Cat(species1_cat)
        dominant_cat_filtered = species1_cat.filter(**cat_filter)
        species2_cat = Cat(species2_cat)
        minor_cat_filtered = species2_cat.filter(**cat_filter)
        dom_freqs_cat, dom_freqs_spec2 = species1_cat.spectrum_matches(
            spec2_pp, dictionary=dominant_cat_filtered, thresh=freq_match)
        minor_freqs_cat, minor_freqs_spec2 = species2_cat.spectrum_matches(
            spec2_pp, dictionary=minor_cat_filtered, thresh=freq_match)
    else:
        dom_freqs_spec2 = []
        minor_freqs_spec2 = []
        for x in range(len(spec2_pp)):
            if spec2_pp[x, 0] in spec1_pp[:, 0]:
                dom_freqs_spec2.append(spec2_pp[x, 0])
            elif spec2_pp[x, 0] + 0.0125 in spec1_pp[:, 0]:
                dom_freqs_spec2.append(spec2_pp[x, 0])
            elif spec2_pp[x, 0] - 0.0125 in spec1_pp[:, 0]:
                dom_freqs_spec2.append(spec2_pp[x, 0])
            else:
                minor_freqs_spec2.append(spec2_pp[x, 0])
    dom_intens_spec1 = [spec1.get_intensity(key) for key in dom_freqs_spec2]
    dom_intens_spec2 = [spec2.get_intensity(key) for key in dom_freqs_spec2]
    dom_ratio = [
        dom_intens_spec1[x] / dom_intens_spec2[x] for x in range(len(dom_intens_spec2))]
    dom_analysis = np.column_stack((dom_freqs_spec2, dom_intens_spec2, dom_intens_spec1, dom_ratio))
    minor_intens_spec1 = [spec1.get_intensity(key) for key in minor_freqs_spec2]
    minor_intens_spec2 = [spec2.get_intensity(key) for key in minor_freqs_spec2]
    minor_ratio = [
        minor_intens_spec1[x] / minor_intens_spec2[x] for x in range(len(minor_intens_spec2))]
    minor_analysis = np.column_stack(
        (minor_freqs_spec2, minor_intens_spec2, minor_intens_spec1, minor_ratio))
    return dom_analysis, minor_analysis


def sigma_filter(arr, col=None, sigma_multiplier=None):
    """
    Remove row if arr[row, col] is detected as outlier (column-wise).

    mean of column +/- s.d. * sigma_multiplier.

    Parameters:
        arr (array):
            Array to filter.
        col (int):
            Column used to filter. Only required if arr has more than one column.
            Default: None
        sigma_multiplier (int):
            Filter condition. Number of standard deviations from the mean.
            Default: 3
    Returns:
        filtered_r (array):
            Filtered array
    """
    if sigma_multiplier is None:
        sigma_multiplier = 3
    if arr.shape[1] != 1:
        if col is None:
            raise IndexError('Specify column')
        else:
            col = col
    r = arr[:, col]
    r_mean = np.mean(r)
    r_std = np.std(r)
    num_sigma = r_std * sigma_multiplier
    r_min = r_mean - num_sigma
    r_max = r_mean + num_sigma
    filtered_r = np.array([arr[x, :] for x in range(len(r)) if r_max >= arr[x, 3] >= r_min])
    return filtered_r


def calculate_ee(species1, species2, topN, rmin1, rmax1, rmin2, rmax2,
                 tag_ee=None, omitted_points=None):
    """
    Calculate enantiomeric excess.

    1.  Filter transitions by internal_intensity_ratio (enantioenriched / racemic) and user
        omitted transitions.
    2.  Sort by intensity and take topN strongest transitions from each species.
    3.  A set of transitions is comprised of one transition from the homochiral species and one
        transition from the heterochiral species. Find normalization val for all sets of
        transitions. (topN^2 in total)
    4.  For each set of transitions, find intensity ratio of one transition to the other
        transition in enantioenriched spectrum.
    5.  Apply normalization factor to intensity ratios.
    6.  Use normalized intensity ratios in ee = (x - 1) / (x + 1)

    Parameters:
        species1 (array):
            col[0] -> freq. of transition.
            col[1] -> intensity in enriched spectrum.
            col[2] -> intensity in racemic spectrum.
            col[3] -> intensity ratio (enriched / racemic).
        species2 (array):
            col[0] -> freq. of transition.
            col[1] -> intensity in enriched spectrum.
            col[2] -> intensity in racemic spectrum.
            col[3] -> intensity ratio (enriched / racemic).
        topN (int):
            Number of transitions from each species used in EE calculation.
        rmin1 (float):
            Minimum filter condition. Filters species1 by intensity ratio.
        rmax1 (float):
            Maximum filter condition. Filters species1 by intensity ratio.
        rmin2 (float):
            Minimum filter condition. Filters species2 by intensity ratio.
        rmax2 (float):
            Maximum filter condition. Filters species2 by intensity ratio.
        tag_ee (float):
            EE of the tag. Used to calibrate final EE determination.
            Default: 1
        omitted_points (list):
            List of frequencies. Transitions at freqs are not used in EE calc.
            Default: []
    Returns:
        ee (array):
            Entries are individual EE calculation using one transition from
            each species. The first topN entries in this array consist of the first transition of
            species1 with each of the topN transitions of species2.
            Shape: ((topN)^2 , )
        topN_dom (array):
            First topN rows of filtered species1 array.
        topN_minor(array):
            First topN rows of filtered species2 array.
    """
    if tag_ee is None:
        tag_ee = 1
    if omitted_points is None:
        omitted_points = []
    dominant = np.array(
        [species1[x, :] for x in range(len(species1)) if
         rmax1 >= species1[x, 3] >= rmin1 and species1[x, 3] != 0 and float(
             "{0:.4f}".format(species1[x, 0])) not in omitted_points])
    minor = np.array(
        [species2[x, :] for x in range(len(species2)) if
         rmax2 >= species2[x, 3] >= rmin2 and species2[x, 3] != 0 and float(
             "{0:.4f}".format(species2[x, 0])) not in omitted_points])
    topN_dom = dominant[0:topN]
    topN_minor = minor[0:topN]
    norm = [(1 / (topN_dom[x, 1] / topN_minor[y, 1])) for x in range(len(topN_dom))
            for y in range(len(topN_minor))]
    R = [topN_dom[x, 2] / topN_minor[y, 2] for x in range(topN) for y in range(topN)]
    R_N = [R[x] * norm[x] for x in range(len(R))]
    ee = [(x - 1) / (x + 1) for x in R_N]
    ee = np.array([ee[x] / tag_ee for x in range(len(ee))])
    return ee, topN_dom, topN_minor
