"""
Author: Channing West
Changelog: 12/5/2019
"""

import numpy as np
import os
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.simpledialog import askinteger
from tkinter.messagebox import showerror
from Pages.PageFormat import PageFormat
from TkAgg_Plotting import PlotManager
from Spectrum import Spectrum
from Spectrum import build_matrix
from Pickett import Cat
from sklearn.cluster import DBSCAN
from sklearn.mixture import GaussianMixture
import Pages.PageFormat as page_funcs
import testing

pad2_e = {'padx': 2, 'pady': 2, 'sticky': 'e'}
pad2_w = {'padx': 2, 'pady': 2, 'sticky': 'w'}
pad2_ew = {'padx': 2, 'pady': 2, 'sticky': 'ew'}
pad2_nsew = {'padx': 2, 'pady': 2, 'sticky': 'nsew'}
pad2_ns = {'padx': 2, 'pady': 2, 'sticky': 'ns'}
pad2 = {'padx': 2, 'pady': 2}
x2_y10_w = {'padx': 2, 'pady': 10, 'sticky': 'w'}
x2_y10_ew = {'padx': 2, 'pady': 10, 'sticky': 'ew'}
x2_y5_w = {'padx': 2, 'pady': 5, 'sticky': 'w'}
x2_y5_ew = {'padx': 2, 'pady': 5, 'sticky': 'ew'}
rspan10_x25_y2_ns = {'rowspan': 10, 'padx': 25, 'pady': 2, 'sticky': 'ns'}
x20_y10_w = {'padx': 20, 'pady': 10, 'sticky': 'w'}
x20_y5_w = {'padx': 20, 'pady': 5, 'sticky': 'w'}


class MixtureAnalysis(ttk.Frame):
    """
    Generate GUI. Attempt to separate composite spectrum into individual molecular spectra by
    characterizing transition signal levels across externally varied spectra (ex. temperature ramp).

    PLOT NAVIGATION BAR
        See TkAgg_Plotting.PlotManager()
    SAVE, LOAD, DEFAULTS, BACK TO NAVIGATOR, EXIT APPLICATION
        See PageFormat.py

    1.  Upload Spectra: Build Matrix or Use Existing
        -   Upload previously built matrix of spectra . If no previously built matrix exists,
            upload a set of spectra to build a new matrix. From file dialog, select multiple spectra
            by holding CTRL and clicking files.
        -   *** In order to add spectra to the matrix in the order they were collected, file names
            MUST BE NUMBERED at the beginning of the file names. ***
        -   After a new matrix is built, file name entry box updates to the name of the matrix.
        Buttons:
            BROWSE
                Run page_funcs.write_paths(self.spec_path, ftype='.ft'). Open file explorer where
                one or more files can be selected. Select > 1 file to build matrix of spectra.
            BUILD MATRIX
                Run build_matrix(*args). Spectra must be over the same frequency region.
                Build spectra matrix from shared frequency region, keeping a single frequency
                column. By saving spectra with a single frequency column, memory is saved. After
                matrix is saved, matrix can be uploaded rather than the set of spectra.
    2A. Characterize Transitions: Specific Component
        -   If the spectrum of a molecular species is known, this section can be used to verify that
            transitions from this species exhibit similar intensity behavior.
        -   See self.characterize_single() for specific intensity characterization parameters.
        -   Upload *.cat file of molecular species.
        -   Dynamic Range:
            Set to limit the predicted transitions used in the calculation to a relative intensity
            range
        -   Top N:
            Set to limit the number of results shown to only include the top N strongest predicted
            transitions. Setting Top N to a certain value does not mean that only those transitions
            are characterized, only that those transitions are displayed in the plot.
        Buttons:
            BROWSE
                Run page_funcs.write_paths(self.cat_path, ftype='.cat'). Select *.cat file from
                file explorer.
            EXECUTE
                Run self.characterize_single(). Characterize transition signal levels for
                a single molecular species using the provided rotational spectra.
            CHANGE PROJECTION
                Run self.single_update(). Update data projection plotted.
            SAVE RESULTS
                Run self.save_single(). Save *.csv files with results of self.known_mixture().
        Option Menu:
            DISPLAYED PROJECTION
                Select a projection of the results to display in the plot.
    2B. Characterize Transitions: All Components
        -   Use for mixtures with unknown components.
        -   See self.unknown_compound() for specific intensity characterization parameters.
        -   Characterize intensity profile of all transitions over the peak pick threshold.
        -   Peak pick threshold:
            If a signal occurs over this threshold in any spectrum in the matrix, the frequency is
            added to the list for intensity profile characterization over the whole set of spectra.
        Buttons:
            EXECUTE
                Run self.characterize_all(). Characterize transition signal levels for all
                transitions above threshold in spectra matrix.
            CHANGE PROJECTION
                Run self.multiple_update(). Update data projection plotted.
            SAVE RESULTS
                Run self.save_mixture(). Save *.csv files with results of self.known_mixture().
        Option Menu:
            DISPLAYED PROJECTION
                Select a projection of the results to display in the plot.
    3.  Find Clusters
        Scan the data set for outliers.
        Two modes:
            1. DBSCAN - Density Based Spatial Clustering of Applications with Noise
                Data points are deemed outliers if no other data points are within a user defined
                range of the point.
            2. GMM - Gaussian Mixture Model
                Data points are deemed outliers if they fall outside the user defined percentile
                of the Gaussian curve.
        Buttons:
            EXECUTE
                Run self.cluster(). Cluster data using a Gaussian Mixture Model. The final
                clustering of the data is only performed using a Gaussian Mixture Model. DBSCAN is
                only used for outlier detection.
            SAVE RESULTS
                Run self.cluster_save(). Save results from self.cluster()
    4.  Split Spectrum
        -   Split raw set of spectra into a set of spectra based on GMM clustering of signal profile
            characterization.
        -   After transitions are assigned to groups based on GMM clustering, all transitions
            belonging to a group will be placed in an array with only other transition of the same
            group. This process is repeated for all GMM groupings. If 10 clusters are found, 10
            arrays are created. For visualization purposes, each transition in the GMM cluster based
            spectra is represented by copying that transition from the raw spectrum with the
            strongest signal.
        -   Split spectra are color coded and plotted.
        Two modes of spectrum splitting:
            SOFT CLUSTER
                Assign probability of each data point belonging to each cluster. Each transition can
                be assigned to multiple clusters if the transition has high enough probability.
            HARD CLUSTER
                Assign each data point to the cluster it has the highest probability of belonging.
        Buttons:
            EXECUTE
                Run split_spectrum(). Split raw set of spectra into a set of spectra based on GMM
                clustering of signal profile characterization.
            SAVE SPECTRA
                Save file temporarily saved from self.split_spectrum().
    5.  Plot Parameters
        Buttons:
            UPDATE PLOT
                Update plot and axes titles with information from entry boxes.
    6.  Notes
        Enter any notes you have about the sample or clustering process that could help you in the
        future. Notes are saved when SAVE button is pressed. Notes are loaded from *.pickle file
        when LOAD is pressed and file selected.
    """

    default = {'sel_x': 'None Selected',
               'sel_y': 'None Selected',
               'all_components_lock': 0,
               'specific_component_lock': 0,
               'find_clusters_lock': 0,
               'split_spectra_lock': 0,
               'plot_title': 'Mixture Analysis',
               'xlabel': 'Time (arb.)',
               'ylabel': 'Norm. Intensity',
               'zlabel': 'None',
               'xmin': 1,
               'x_increment': 1,
               'spec_path': 'None',
               'cat_path': 'None',
               'topN': 10,
               'dyn_range': 100,
               'pp_thresh': 0.001,
               'known_plot': '2-D: Intensity vs. Time',
               'unknown_plot': '3-D: Area vs. <x> vs. width',
               'outlier_mode': 'dbscan',
               'remove_outliers': 1,
               'dbscan_eps': 1.0,
               'gmm_percentile': 4.0,
               'gmm_tolerance': 0.001,
               'max_iter': 100,
               'n_init': 20,
               'cluster_projection': '3-D: Area vs. <x> vs. width',
               'soft_hard': 'hard',
               'probability_thresh': 0.2,
               'line_width': 0.25}

    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.controller = controller
        self.page_title = "Broadband MRR Toolbox - Mixture Analysis"

        self.sel_x = tk.StringVar()
        self.sel_y = tk.StringVar()
        self.sel_x.set(MixtureAnalysis.default['sel_x'])
        self.sel_y.set(MixtureAnalysis.default['sel_y'])
        self.omitted_points = []
        self.all_components_lock = tk.IntVar()
        self.specific_component_lock = tk.IntVar()
        self.find_clusters_lock = tk.IntVar()
        self.split_spectra_lock = tk.IntVar()
        self.all_components_lock.set(MixtureAnalysis.default['all_components_lock'])
        self.specific_component_lock.set(MixtureAnalysis.default['specific_component_lock'])
        self.find_clusters_lock.set(MixtureAnalysis.default['find_clusters_lock'])
        self.split_spectra_lock.set(MixtureAnalysis.default['split_spectra_lock'])
        self.plot_title = tk.StringVar()
        self.xlabel = tk.StringVar()
        self.ylabel = tk.StringVar()
        self.zlabel = tk.StringVar()
        self.xmin = tk.StringVar()
        self.x_increment = tk.StringVar()
        self.plot_title.set(MixtureAnalysis.default['plot_title'])
        self.xlabel.set(MixtureAnalysis.default['xlabel'])
        self.ylabel.set(MixtureAnalysis.default['ylabel'])
        self.zlabel.set(MixtureAnalysis.default['zlabel'])
        self.xmin.set(MixtureAnalysis.default['xmin'])
        self.x_increment.set(MixtureAnalysis.default['x_increment'])
        self.spec_path = tk.StringVar()
        self.spec_path.set(MixtureAnalysis.default['spec_path'])
        self.cat_path = tk.StringVar()
        self.topN = tk.IntVar()
        self.dyn_range = tk.IntVar()
        self.cat_path.set(MixtureAnalysis.default['cat_path'])
        self.topN.set(MixtureAnalysis.default['topN'])
        self.dyn_range.set(MixtureAnalysis.default['dyn_range'])
        self.pp_thresh = tk.DoubleVar()
        self.pp_thresh.set(MixtureAnalysis.default['pp_thresh'])
        self.known_plot = tk.StringVar()
        self.known_plot.set(MixtureAnalysis.default['known_plot'])
        self.unknown_plot = tk.StringVar()
        self.unknown_plot.set(MixtureAnalysis.default['unknown_plot'])
        self.remove_outliers = tk.IntVar()
        self.remove_outliers.set(MixtureAnalysis.default['remove_outliers'])
        self.outlier_mode = tk.StringVar()
        self.outlier_mode.set(MixtureAnalysis.default['outlier_mode'])
        self.dbscan_eps = tk.DoubleVar()
        self.dbscan_eps.set(MixtureAnalysis.default['dbscan_eps'])
        self.percentile = tk.DoubleVar()
        self.percentile.set(MixtureAnalysis.default['gmm_percentile'])
        self.tolerance = tk.DoubleVar()
        self.tolerance.set(MixtureAnalysis.default['gmm_tolerance'])
        self.max_iter = tk.IntVar()
        self.max_iter.set(MixtureAnalysis.default['max_iter'])
        self.n_init = tk.IntVar()
        self.n_init.set(MixtureAnalysis.default['n_init'])
        self.cluster_projection = tk.StringVar()
        self.cluster_projection.set(MixtureAnalysis.default['cluster_projection'])
        self.soft_hard = tk.StringVar()
        self.soft_hard.set(MixtureAnalysis.default['soft_hard'])
        self.probability_thresh = tk.DoubleVar()
        self.probability_thresh.set(MixtureAnalysis.default['probability_thresh'])
        self.line_width = tk.DoubleVar()
        self.line_width.set(MixtureAnalysis.default['line_width'])
        self.plot_frame = ttk.Frame(self.frame)
        outer = ttk.Frame(self.frame)
        inner_0 = ttk.Frame(outer)
        inner_1 = ttk.Frame(outer)
        inner_2 = ttk.Frame(outer)
        inner_3 = ttk.Frame(outer)
        self.attr_dict = {'spec_path': self.spec_path,
                          'plot_title': self.plot_title,
                          'xlabel': self.xlabel,
                          'ylabel': self.ylabel,
                          'zlabel': self.zlabel,
                          'cat_path': self.cat_path,
                          'dyn_range': self.dyn_range,
                          'topN': self.topN,
                          'known_plot': self.known_plot,
                          'pp_thresh': self.pp_thresh,
                          'unknown_plot': self.unknown_plot,
                          'remove_outliers': self.remove_outliers,
                          'outlier_mode': self.outlier_mode,
                          'dbscan_eps': self.dbscan_eps,
                          'gmm_percentile': self.percentile,
                          'gmm_tolerance': self.tolerance,
                          'max_iter': self.max_iter,
                          'n_init': self.n_init,
                          'cluster_projection': self.cluster_projection,
                          'soft_hard': self.soft_hard,
                          'probability_thresh': self.probability_thresh,
                          'line_width': self.line_width}
        h14b = 'Helvetica 14 bold'
        h10 = 'Helvetica 10'
        r = tk.RIGHT
        c = tk.CENTER
        l = tk.LEFT
        h8bL = 'h8b.TLabel'
        h10bL = 'h10b.TLabel'
        h10bRB = 'h10b.TRadiobutton'
        h10bB = 'h10b.TButton'
        # ==========================================================================================
        #                                            Inner 0
        # ==========================================================================================
        spec_section_L = ttk.Label(
            inner_0, text='Upload Spectra:\nBuild Matrix or Use Existing', justify=l, font=h14b)
        warning_L = ttk.Label(
            inner_0, text='** File names must be numbered for proper ordering **',
            style='warning.TLabel')
        spec_path_L = ttk.Label(inner_0, text='File(s):', style=h8bL, justify=r)
        spec_path_E = ttk.Entry(inner_0, textvariable=self.spec_path, justify=c, width=50)
        button_spec_path = ttk.Button(
            inner_0, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_paths(self.spec_path, eb_var=spec_path_E, ftype='.ft'))
        build_matrix_B = ttk.Button(
            inner_0, text='Build Matrix', style='h8b.TButton', command=self.build_matrix)
        spec_section_L.grid(row=0, column=0, columnspan=3, **x2_y10_w)
        warning_L.grid(row=1, column=1, columnspan=1, **pad2_e)
        spec_path_L.grid(row=2, column=0, **pad2_e)
        spec_path_E.grid(row=2, column=1, **pad2_ew)
        button_spec_path.grid(row=2, column=2, **pad2_ew)
        build_matrix_B.grid(row=3, column=2, **pad2_ew)
        # ==========================================================================================
        #                                        Inner 1
        # ==========================================================================================
        plot_param_section = ttk.Label(inner_1, text='Plot Parameters', justify=l, font=h14b)
        plot_title_L = ttk.Label(inner_1, text='Plot Title:', style=h8bL, justify=r)
        xlabel_L = ttk.Label(inner_1, text='X-Axis Title:', style=h8bL, justify=r)
        ylabel_L = ttk.Label(inner_1, text='Y-Axis Title:', style=h8bL, justify=r)
        zlabel_L = ttk.Label(inner_1, text='Z-Axis Title:', style=h8bL, justify=r)
        plot_title_E = ttk.Entry(inner_1, textvariable=self.plot_title, justify=c)
        xlabel_E = ttk.Entry(inner_1, textvariable=self.xlabel, justify=c)
        ylabel_E = ttk.Entry(inner_1, textvariable=self.ylabel, justify=c)
        zlabel_E = ttk.Entry(inner_1, textvariable=self.zlabel, justify=c)
        update_button = ttk.Button(
            inner_1, text='Update Plot', style='h8b.TButton', command=self.update_plot)
        notes_L = ttk.Label(outer, text='Notes', justify=c, font=h14b)
        self.notes_tb = tk.Text(outer, height=10, width=50, relief='sunken', font=h10, wrap=tk.WORD)
        self.notes_tb.delete('1.0', tk.END)
        self.notes_tb.insert('1.0', 'None')
        self.text_dict = {'notes': self.notes_tb}
        notes_L.grid(row=5, column=1, padx=5, pady=10, sticky='sw')
        self.notes_tb.grid(row=6, column=1, rowspan=3, **pad2_ns)
        plot_param_section.grid(row=0, column=0, **x2_y10_w)
        plot_title_L.grid(row=1, column=0, **pad2_e)
        xlabel_L.grid(row=2, column=0, **pad2_e)
        ylabel_L.grid(row=3, column=0, **pad2_e)
        zlabel_L.grid(row=4, column=0, **pad2_e)
        plot_title_E.grid(row=1, column=1, **pad2_ew)
        xlabel_E.grid(row=2, column=1, **pad2_ew)
        ylabel_E.grid(row=3, column=1, **pad2_ew)
        zlabel_E.grid(row=4, column=1, **pad2_ew)
        update_button.grid(row=5, column=1, columnspan=2, **pad2_ew)
        # ==========================================================================================
        #                                       Inner 2
        # ==========================================================================================
        inner_2_1 = ttk.Frame(inner_2)
        inner_2_1.grid(row=0, column=0, **pad2_ew)
        single_section = ttk.Label(
            inner_2_1, text='Characterize Transitions:\nSpecific Component', justify=l, font=h14b)
        cat_L = ttk.Label(inner_2_1, text='Path to CAT:', style=h8bL, justify=r)
        filter_L = ttk.Label(inner_2_1, text='Dynamic Range:', style=h8bL, justify=r)
        topN_L = ttk.Label(inner_2_1, text='Top N:', style=h8bL, justify=r)
        cat_E = ttk.Entry(inner_2_1, textvariable=self.cat_path, justify=c)
        filter_E = ttk.Entry(inner_2_1, textvariable=self.dyn_range, justify=c)
        topN_E = ttk.Entry(inner_2_1, textvariable=self.topN, justify=c)
        button_cat_path = ttk.Button(
            inner_2_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.cat_path, eb_var=cat_E, ftype='.cat'))
        single_section.grid(row=0, column=0, columnspan=3, **x2_y10_w)
        cat_L.grid(row=1, column=0, **pad2_e)
        button_cat_path.grid(row=1, column=2, **pad2_ew)
        filter_L.grid(row=2, column=0, **pad2_e)
        topN_L.grid(row=3, column=0, **pad2_e)

        projections = (
            '3-D: Area vs. <x> vs. width', '2-D: Intensity vs. Time', '2-D: Area vs. <x>',
            '2-D: Area vs. width', '2-D: <x> vs. width')
        known_L = ttk.Label(
            inner_2_1, text='Displayed Projection', justify=r, style=h10bL)
        known_menu = ttk.OptionMenu(
            inner_2, self.known_plot, projections[0], *projections, style="TMenubutton")
        known_L.grid(row=4, column=0, columnspan=1, **x2_y10_w)
        known_menu.grid(row=1, column=0, columnspan=1, pady=5, sticky='ew')
        cat_E.grid(row=1, column=1, **pad2_ew)
        filter_E.grid(row=2, column=1, **pad2_ew)
        topN_E.grid(row=3, column=1, **pad2_ew)

        inner_2_2 = ttk.Frame(inner_2)
        inner_2_2.grid(row=2, column=0, pady=10, sticky='ew')

        single_execute = ttk.Button(
            inner_2_2, text='Execute', command=self.characterize_single, style=h10bB, width=13)
        single_update = ttk.Button(
            inner_2_2, text='Change Projection', command=self.single_update, style=h10bB, width=18)
        save_single = ttk.Button(
            inner_2_2, text='Save Results', command=self.save_single, style=h10bB, width=13)
        single_execute.grid(row=0, column=0, **pad2_ew)
        single_update.grid(row=0, column=1, **pad2_ew)
        save_single.grid(row=0, column=2, **pad2_ew)
        ttk.Separator(inner_2, orient='horizontal').grid(row=3, column=0, padx=2, pady=15,
                                                         sticky='ew')
        # ==========================================================================================
        #                                        Inner 3
        # ==========================================================================================
        inner_2_3 = ttk.Frame(inner_2)
        all_section = ttk.Label(
            inner_2_3, text='Characterize Transitions:\nAll Components ', justify=l, font=h14b)
        pp_thresh_L = ttk.Label(
            inner_2_3, text='Peak pick\nthreshold:', style=h8bL, justify=r)
        pp_thresh_E = ttk.Entry(inner_2_3, textvariable=self.pp_thresh, justify=c)
        projections = (
            '3-D: Area vs. <x> vs. width', '2-D: Area vs. <x>', '2-D: Area vs. width',
            '2-D: <x> vs. width')
        unknown_L = ttk.Label(inner_2_3, text='Displayed Projection', justify=r, style=h10bL)
        unknown_menu = ttk.OptionMenu(inner_2, self.unknown_plot, projections[0], *projections)
        all_section.grid(row=0, column=0, columnspan=2, **x2_y10_w)
        pp_thresh_L.grid(row=1, column=0, **pad2_e)
        pp_thresh_E.grid(row=1, column=1, **pad2_ew)
        unknown_L.grid(row=2, column=0, columnspan=1, **x2_y10_w)
        unknown_menu.grid(row=5, column=0, columnspan=1, pady=5, sticky='ew')

        inner_2_4 = ttk.Frame(inner_2)
        all_execute = ttk.Button(
            inner_2_4, text='Execute', style=h10bB, width=13,
            command=lambda: self.characterize_all())
        all_update = ttk.Button(
            inner_2_4, text='Change Projection', style=h10bB, width=18,
            command=lambda: self.multiple_update())
        all_save = ttk.Button(
            inner_2_4, text='Save Results', style=h10bB, width=13,
            command=lambda: self.save_mixture())
        all_execute.grid(row=0, column=0, **pad2_ew)
        all_update.grid(row=0, column=1, **pad2_ew)
        all_save.grid(row=0, column=2, **pad2_ew)
        inner_2_3.grid(row=4, column=0, sticky='ew')
        inner_2_4.grid(row=6, column=0, pady=10, sticky='ew')
        # ==========================================================================================
        #                                      cluster Block
        # ==========================================================================================
        inner_3_1 = ttk.Frame(inner_3)
        inner_3_1.grid(row=0, column=0)
        cluster_L = ttk.Label(inner_3_1, text='Find Clusters', justify=r, font=h14b)
        outliers_L = ttk.Label(
            inner_3_1, text='Remove outliers with selected method:', justify=r, style=h10bL)
        outliers_checkbox = ttk.Checkbutton(inner_3_1, variable=self.remove_outliers)
        dbscan_rb = ttk.Radiobutton(
            inner_3_1, text='DBSCAN', variable=self.outlier_mode, value='dbscan', style=h10bRB)
        dbscan_eps_L = ttk.Label(inner_3_1, text='Max.\nSeparation', style=h8bL, justify=r)
        dbscan_eps_E = ttk.Entry(inner_3_1, textvariable=self.dbscan_eps, justify=c)
        gmm_rb = ttk.Radiobutton(
            inner_3_1, text='GMM', variable=self.outlier_mode, value='gmm', style=h10bRB)
        percentile_L = ttk.Label(
            inner_3_1, text='Omit Upper and\nLower Percentile:', style=h8bL, justify=r)
        percentile_E = ttk.Entry(inner_3_1, textvariable=self.percentile, justify=c)
        options_L = ttk.Label(
            inner_3_1, text='Final Gaussian Mixture Model:', style=h10bL, justify=r)
        tolerance_L = ttk.Label(inner_3_1, text='Convergence\nThreshold:', style=h8bL, justify=r)
        tolerance_E = ttk.Entry(inner_3_1, textvariable=self.tolerance, justify=c)
        max_iter_L = ttk.Label(inner_3_1, text='Max. Iterations:', style=h8bL, justify=r)
        max_iter_E = ttk.Entry(inner_3_1, textvariable=self.max_iter, justify=c)
        num_init_L = ttk.Label(inner_3_1, text='Initializations:', style=h8bL, justify=r)
        num_init_E = ttk.Entry(inner_3_1, textvariable=self.n_init, justify=c)
        projections = ('3-D: Area vs. <x> vs. width', '2-D: Area vs. <x>', '2-D: Area vs. width',
                       '2-D: <x> vs. width')
        cluster_menu_L = ttk.Label(inner_3_1, text='Projection', justify=r, style=h10bL)
        cluster_menu = ttk.OptionMenu(
            inner_3, self.cluster_projection, projections[0], *projections)
        cluster_L.grid(row=0, column=0, columnspan=2, **x2_y5_w)
        outliers_L.grid(row=1, column=0, columnspan=2, **x2_y5_w)
        outliers_checkbox.grid(row=1, column=2, **x2_y5_w)
        dbscan_rb.grid(row=2, column=0, **x20_y5_w)
        dbscan_eps_L.grid(row=3, column=0, **pad2_e)
        dbscan_eps_E.grid(row=3, column=1, **pad2_ew)
        gmm_rb.grid(row=4, column=0, columnspan=2, **x20_y5_w)
        percentile_L.grid(row=5, column=0, **pad2_e)
        percentile_E.grid(row=5, column=1, **pad2_ew)
        options_L.grid(row=6, column=0, **x2_y10_w)
        tolerance_L.grid(row=7, column=0, **pad2_e)
        tolerance_E.grid(row=7, column=1, **pad2_ew)
        max_iter_L.grid(row=8, column=0, **pad2_e)
        max_iter_E.grid(row=8, column=1, **pad2_ew)
        num_init_L.grid(row=9, column=0, **pad2_e)
        num_init_E.grid(row=9, column=1, **pad2_ew)
        cluster_menu_L.grid(row=10, column=0, **x2_y10_w)
        cluster_menu.grid(row=1, column=0, sticky='ew')

        inner_3_2 = ttk.Frame(inner_3)
        inner_3_2.grid(row=2, column=0, pady=10)
        cluster_execute = ttk.Button(
            inner_3_2, text='Execute', command=self.cluster, style=h10bB, width=22)
        cluster_save = ttk.Button(
            inner_3_2, text='Save Results', command=self.cluster_save, style=h10bB, width=22)
        cluster_execute.grid(row=0, column=0, **pad2_ew)
        cluster_save.grid(row=0, column=1, **pad2_ew)
        ttk.Separator(inner_3, orient='horizontal').grid(row=3, column=0, **x2_y10_ew)
        inner_3_3 = ttk.Frame(inner_3)
        inner_3_3.grid(row=4, column=0, sticky='w')
        split_L = ttk.Label(inner_3_3, text='Split Spectrum', justify=r, font=h14b)
        cluster_menu_L = ttk.Label(inner_3_3, text='Splitting Method: ', justify=r, style=h10bL)
        hard_rb = ttk.Radiobutton(
            inner_3_3, text='Hard Cluster', variable=self.soft_hard, value='hard', style=h10bRB)
        soft_rb = ttk.Radiobutton(
            inner_3_3, text='Soft Cluster', variable=self.soft_hard, value='soft', style=h10bRB)
        prob_thresh_L = ttk.Label(inner_3_3, text='Probability\nThreshold:', style=h10bL, justify=r)
        prob_thresh_E = ttk.Entry(inner_3_3, textvariable=self.probability_thresh, justify=c)
        line_width_L = ttk.Label(inner_3_3, text='Line Width:', style=h10bL, justify=r)
        line_width_E = ttk.Entry(inner_3_3, textvariable=self.line_width, justify=c)
        split_L.grid(row=0, column=0, columnspan=2, **x2_y5_w)
        cluster_menu_L.grid(row=1, column=0, padx=2, pady=5, sticky='e')# **x2_y5_w)
        prob_thresh_L.grid(row=2, column=0, padx=2, pady=5, sticky='e') # **x2_y5_w)
        prob_thresh_E.grid(row=2, column=1, **pad2_ew)
        line_width_L.grid(row=3, column=0, padx=2, pady=5, sticky='e') # **x2_y5_w)
        line_width_E.grid(row=3, column=1, **pad2_ew)
        soft_rb.grid(row=1, column=2, **x20_y10_w)
        hard_rb.grid(row=1, column=1, **x20_y10_w)
        inner_3_4 = ttk.Frame(inner_3)
        inner_3_4.grid(row=5, column=0, sticky='ew')
        split_execute = ttk.Button(
            inner_3_4, text='Execute', command=self.split_spectrum, style=h10bB, width=22)
        split_save = ttk.Button(
            inner_3_4, text='Save Spectra', command=self.split_save, style=h10bB, width=22)
        split_execute.grid(row=0, column=0, **pad2_ew)
        split_save.grid(row=0, column=1, **pad2_ew)
        # ==========================================================================================
        #                                    Outer Block
        # ==========================================================================================
        inner_0.grid(row=1, column=1, **pad2_nsew)
        inner_1.grid(row=3, column=1, **pad2_nsew)
        inner_2.grid(row=1, column=3, rowspan=8, **pad2_nsew)
        inner_3.grid(row=1, column=5, rowspan=8, **pad2_nsew)
        ttk.Separator(outer, orient='vertical').grid(row=0, column=0, **rspan10_x25_y2_ns)
        ttk.Separator(outer, orient='vertical').grid(row=0, column=2, **rspan10_x25_y2_ns)
        ttk.Separator(outer, orient='vertical').grid(row=0, column=4, **rspan10_x25_y2_ns)
        ttk.Separator(outer, orient='vertical').grid(row=0, column=6, **rspan10_x25_y2_ns)
        ttk.Separator(outer, orient='horizontal').grid(row=4, column=1, **x2_y10_ew)
        ttk.Separator(outer, orient='horizontal').grid(row=0, column=1, **x2_y10_ew)
        ttk.Separator(outer, orient='horizontal').grid(row=0, column=3, **x2_y10_ew)
        ttk.Separator(outer, orient='horizontal').grid(row=0, column=5, **x2_y10_ew)
        ttk.Separator(outer, orient='horizontal').grid(row=9, column=1, **x2_y10_ew)
        ttk.Separator(outer, orient='horizontal').grid(row=9, column=3, **x2_y10_ew)
        ttk.Separator(outer, orient='horizontal').grid(row=9, column=5, **x2_y10_ew)
        ttk.Separator(outer, orient='horizontal').grid(row=2, column=1, **x2_y10_ew)
        # ==========================================================================================
        #                                    Plot Frame
        # ==========================================================================================
        self.plot_pm = PlotManager(
            frame=self.plot_frame, figsize=(16, 8), dpi=100, subplotshape=111,
            plot_title=self.plot_title.get(), xlabel=self.xlabel.get(), ylabel=self.ylabel.get(),
            x_min='Auto', x_max='Auto', y_min='Auto', y_max='Auto', legend_show=1, legend_font=10,
            legend_loc=0, left=0.05, right=0.98, top=0.95, bottom=0.09, row=0, column=0,
            columnspan=2, toolbar=True, toolrow=1, toolcol=0, toolpady=2, toolsticky='w')
        button_frame = ttk.Frame(self.plot_frame)
        save = ttk.Button(
            button_frame, text='Save', style=h10bB, width=20,
            command=lambda: page_funcs.save_page(self.attr_dict, self.text_dict))
        eb_lst = [spec_path_E, cat_E]
        load = ttk.Button(
            button_frame, text='Load', style=h10bB, width=20,
            command=lambda: page_funcs.load_page(
                self.attr_dict, self.specific_component_lock, self.all_components_lock,
                self.find_clusters_lock, self.split_spectra_lock, tb_dict=self.text_dict,
                eb_var=eb_lst))
        clear = ttk.Button(
            button_frame, text='Defaults', style=h10bB, width=20,
            command=lambda: page_funcs.clear_page(
                MixtureAnalysis.default, self.attr_dict, self.text_dict))
        save.grid(row=0, column=0, **pad2_nsew)
        load.grid(row=0, column=1, **pad2_nsew)
        clear.grid(row=0, column=2, **pad2_nsew)
        button_frame.grid(row=1, column=1, pady=2, sticky='e')
        self.plot_frame.grid(row=0, column=0, **pad2)
        self.plot_frame.grid(row=0, column=0)
        outer.grid(row=1, column=0)
        self.plot_pm.canvas.mpl_connect(
            'pick_event', lambda event: page_funcs.mpl_click(event, self.sel_int, self.sel_freq))
        self.page.enter_textbox(self.notes_tb)
        self.page.exit_textbox(self.notes_tb)

    @testing.collect_garbage
    def build_matrix(self):
        """
        Spectrum.build_matrix() wrapper. Builds matrix when more than one file name populates
        self.spec_path.

        File names of all files selected from file explorer will populate self.spec_path.
        After saving matrix, self.spec_path is changed to the name of the matrix.
        """
        files_list = page_funcs.list_paths(self.spec_path)
        if len(files_list) > 1:
            fnames, matrix = build_matrix(files_list)
            spec_path = page_funcs.save_file(
                ftype='.ft', initialdir=os.path.dirname(files_list[0]), defaultextension='.ft')
            fnames_path = os.path.splitext(spec_path)[0] + '_fnames.txt'
            if spec_path != '':
                fmt = ['%.4f']
                for x in range(matrix.shape[1] - 1):
                    fmt.append('%.8f')
                np.savetxt(spec_path, matrix, fmt=fmt)
                with open(fnames_path, 'w') as f:
                    for fname in fnames:
                        f.write(fname + '\n')
                f.close()
        else:
            spec_path = files_list[0]
        self.spec_path.set(spec_path)

    def characterize_single(self):
        """
        Characterize transition signal levels for a single molecular species using the provided
        rotational spectra and *.cat file.

        This is mostly a proof-of-concept to validate that transitions of a certain molecular
        species exhibit similar behaviour. self.cluster() does not support results from this method.

        Using transition intensities from a set of spectra, with the spectra typically differing in
        the nozzle temperature at which they are taken, transition intensity is plotted as a
        function of an external variable (time/FIDs/temperature). The mean value along the x-axis,
        the area under curve, and the width of the curve are used to characterize the behavior of
        the transition. Outliers (3 sigma) removed.

        *.cat file must be provided. Dynamic range filters transitions from *.cat file below the
        threshold. Set dynamic range to 10 to only characterize transitions at least 1/10 the
        intensity of the strongest transition in the line list. Top N sets the number of displayed
        transitions, starting with the strongest transition. Set Top N to 10 to plot the
        characterization parameters of the 10 strongest transitions.

        Save temporary files:
            'known_norm.npy' (binary array):
                Normalized signal profile of each transition.
                Shape: (# of transitions , # of raw spectra + 1)
                col[0] -> frequency
                col[1] -> normalized intensity of transition in first spectrum.
                col[2] -> normalized intensity of transition in second spectrum.
                col[3:] -> etc.
            'known_char.npy' (binary array):
                Characterization of normalized signal profiles.
                Shape: (# of transitions , 4)
                col[0] -> frequency
                col[1] -> mean x
                col[2] -> area under curve
                col[3] -> curve width
        """
        dyn_range = self.dyn_range.get()
        files_list = page_funcs.list_paths(self.spec_path)
        if len(files_list) > 1:
            fnames, matrix = build_matrix(files_list)
            spec_path = page_funcs.save_file(
                ftype='.ft', initialdir=os.path.dirname(files_list[0]), defaultextension='.ft')
            fnames_path = os.path.splitext(spec_path)[0] + '_fnames.txt'
            if spec_path != '':
                fmt = ['%.4f']
                for x in range(matrix.shape[1] - 1):
                    fmt.append('%.8f')
                np.savetxt(spec_path, matrix, fmt=fmt)
                self.spec_path.set(spec_path)
                with open(fnames_path, 'w') as f:
                    for fname in fnames:
                        f.write(fname + '\n')
                f.close()
        else:
            spec_path = files_list[0]
        spectra = Spectrum(spec_path)
        cat = Cat(self.cat_path.get())
        cat_filter = cat.filter(
            freq_min=spectra.freq_min, freq_max=spectra.freq_max, dyn_range=dyn_range)
        cat_freqs = list(cat_filter.keys())
        high_points = spectra.signal_max(
            cat_freqs, delta_freq=2 * spectra.point_spacing)
        exp_pp_freqs = high_points[:, 0]
        exp_pp_rows = [spectra.freq_to_row(x) for x in exp_pp_freqs]
        intensity_rows = [spectra.spectrum[x, :].tolist() for x in exp_pp_rows]
        normalized = np.array([spectra.normalize_transition(intensity_rows[x][0]) for x in
                               range(len(intensity_rows))])
        mean_x = [mean_x_axis(x) for x in normalized[:, 2:]]
        areas = [area_under_curve(x) for x in normalized[:, 2:]]
        width = [curve_width(x) for x in normalized[:, 2:]]
        hm_point = [width[x][0] for x in range(len(width))]
        width_val = [width[x][1] for x in range(len(width))]
        characterization_array = np.column_stack((exp_pp_freqs, mean_x, areas, width_val))
        filtered_array, avgs, stds = outlier_test(characterization_array, cols=[1, 2, 3], num_std=3)
        self.page.save_temp_file('known_norm', normalized)
        self.page.save_temp_file('known_char', filtered_array)
        self.change_projection(mode='known')
        self.specific_component_lock.set(0)

    def characterize_all(self):
        """
        Characterize transition signal levels for all transitions above threshold in spectra matrix.

        Peak pick is performed on all individual spectra in the matrix, if a transition occurs at a
        particular frequency above the threshold in any spectrum in the matrix, frequency is
        added to list for characterization.

        Using transition intensities from a set of spectra, with the spectra typically differing in
        the nozzle temperature at which they are taken, transition intensity is plotted as a
        function of an external variable (time/FIDs/temperature). The mean value along the x-axis,
        the area under curve, and the width of the curve are used to characterize the behavior of
        the transition.

        Save temporary files:
            'unknown_norm.npy' (binary array):
                Normalized signal profile of each transition.
                Shape: (# of transitions , # of raw spectra + 2)
                col[0] -> frequency
                col[1] -> Intensity of strongest signal observed. Normalization factor.
                col[2] -> normalized intensity of transition in first spectrum.
                col[3] -> normalized intensity of transition in second spectrum.
                col[4] -> etc.
            'unknown_char.npy' (binary array):
                Characterization of normalized signal profile.
                Shape: (# of transitions , 5)
                col[0] -> frequency
                col[1] -> mean x
                col[2] -> area under curve
                col[3] -> curve width
        """
        files_list = page_funcs.list_paths(self.spec_path)
        if len(files_list) > 1:
            fnames, matrix = build_matrix(*files_list)
            spec_path = page_funcs.save_file(
                ftype='.ft', initialdir=os.path.dirname(files_list[0]), defaultextension='.ft')
            fnames_path = os.path.splitext(spec_path)[0] + '_fnames.txt'
            if spec_path != '':
                fmt = ['%.4f']
                for x in range(matrix.shape[1] - 1):
                    fmt.append('%.8f')
                np.savetxt(spec_path, matrix, fmt=fmt)
                self.spec_path.set(spec_path)
                with open(fnames_path, 'w') as f:
                    for fname in fnames:
                        f.write(fname + '\n')
                f.close()
        else:
            spec_path = files_list[0]
        spectra = Spectrum(spec_path)
        exp_pp_rows = spectra.peak_pick_sequence_measurement(thresh=self.pp_thresh.get())
        exp_pp_freqs = []
        intensity_rows = []
        for row in exp_pp_rows:
            exp_pp_freqs.append(spectra.row_to_freq(row))
            intensity_rows.append(spectra.spectrum[row, :].tolist())
        norm_list = [
            spectra.normalize_transition(intensity_rows[x][0]) for x in range(len(intensity_rows))]
        mean_x = []
        areas = []
        width = []
        for x in np.array(norm_list)[:, 2:]:
            mean_x.append(mean_x_axis(x))
            areas.append(area_under_curve(x))
            width.append(curve_width(x))
        hm_point = []
        width_val = []
        for x in range(len(width)):
            hm_point.append(width[x][0])
            width_val.append(width[x][1])
        to_delete = [x for x in range(len(hm_point)) if hm_point[x] == 0]
        to_delete = sorted(to_delete, reverse=True)
        for x in to_delete:
            list_list = [exp_pp_freqs, norm_list, mean_x, areas, width, hm_point, width_val]
            for l in list_list:
                del l[x]
        characterization_array = np.column_stack((exp_pp_freqs, mean_x, areas, width_val))
        self.page.save_temp_file('unknown_norm', np.array(norm_list))
        self.page.save_temp_file('unknown_char', characterization_array)
        self.change_projection(mode='unknown')
        self.all_components_lock.set(0)

    @testing.collect_garbage
    def cluster(self):
        """
        Fit signal characterization data to Gaussian mixture model. Supports 2D and 3D GMM.

        1.  Optional outlier check
            Two outlier modes:
                1.  DBSCAN - density based. If no other data points within self.tolerance,
                    data point deemed outlier.
                2.  GMM - Gaussian probability. If probability less than self.percentile, data
                    point deemed outlier.
        2.  Data set fit to different number of Gaussians, between 2 and 25, to determine best
            number of Gaussians for final fit. Bayesian Information Criterion (BIC) is plotted,
            which allows the user to find best fit. User asked for number of Gaussians for final
            fit. The key is to minimize BIC without overfitting. It is likely that BIC will
            continue lower over this range, but there will likely be a point where the return of
            adding a Gaussian diminishes significantly. This is where the slope of the
            tangent line is more or less zero.
        3.  Refit data set to requested number of Gaussians, self.tolerance, self.max_iter,
            self.n_init.
        4.  Plot data with clusters visualized as ellipses or ellipsoids.

        Save temporary files:
            'projection_details (binary array):
                Data projection information for naming files and tables in later steps.
                arr[0] -> title to add to table
                arr[1] -> string to add to file name
            'char_cleaned.npy' (binary array):
                Characterization array with outliers removed.
                Shape: (# of valid transitions , 4)
                col[0] -> frequency
                col[1] -> mean x
                col[2] -> area under curve
                col[3] -> width of curve
            'char_outliers.npy' (binary array):
                Outliers, GMM centers.
                Shape: (# of outliers , 4)
                col[0] -> frequency
                col[1] -> mean x
                col[2] -> area under curve
                col[3] -> width of curve
            'norm_cleaned.npy' (binary array):
                Normalized signal profile of transitions with outliers removed.
                Shape: (# of transitions , # of raw spectra + 2)
                col[0] -> frequency
                col[1] -> Intensity of strongest signal observed. Normalization factor.
                col[2] -> normalized intensity of transition in first spectrum.
                col[3] -> normalized intensity of transition in second spectrum.
                col[4] -> etc.
            'norm_outliers.npy' (binary array):
                Outliers of normalized signal profile of transitions.
                Shape: (# of outliers , # of raw spectra + 2)
                col[0] -> frequency
                col[1] -> intensity of strongest signal observed. Normalization factor.
                col[2] -> normalized intensity of transition in first spectrum.
                col[3] -> normalized intensity of transition in second spectrum.
                col[4] -> etc.
            'gmm_means.npy' (binary array):
                GMM covariances.
                Shape: (# of clusters , # of characterization parameters)
                col[0] -> x vals
                col[1] -> y vals
                col[2] -> z vals
            'gmm_covs.npy' (binary array):
                Covariance matrices of Gaussians. Square matrices. Either 2x2 matrices or 3x3
                matrices. One matrix for each cluster. Used for cluster visualization.
                Shape: (# of clusters , # of characterization params , # of characterization params)
                gmm_covs[0] -> covariance matrix of cluster 1.
                gmm_covs[1] -> covariance matrix of cluster 2.
                gmm_covs[2] -> etc.
            'hard_cluster.npy' (binary array):
                Assign each transition a number that corresponds to the cluster it belongs to.
                Shape: (# of transitions,)
            'soft_cluster.npy' (binary array):
                Soft cluster probabilities of each transition belonging to each cluster.
                Shape: (# of transitions , # of clusters)
        """
        if self.all_components_lock.get():
            showerror('Error', message='Characterize peaks before proceeding to this step.')
            return
        char = self.page.load_temp_file('unknown_char.npy')
        norm = self.page.load_temp_file('unknown_norm.npy')
        projection_title = self.unknown_plot.get()
        cluster_projection = self.cluster_projection.get()
        if cluster_projection == '3-D: Area vs. <x> vs. width':
            data = np.column_stack((char[:, 1], char[:, 2], char[:, 3]))
            projection_fname = '3d'
            plot_title = 'Width vs. Area vs <X>'
            xlabel = 'x (<X>)'
            ylabel = 'y (Area)'
            zlabel = 'z (Width)'
        elif cluster_projection == '2-D: Area vs. <x>':
            data = np.column_stack((char[:, 1], char[:, 2]))
            projection_fname = 'meanx_area'
            plot_title = 'Area vs <X>'
            xlabel = '<X>'
            ylabel = 'Area'
        elif cluster_projection == '2-D: Area vs. width':
            data = np.column_stack((char[:, 2], char[:, 3]))
            projection_fname = 'area_width'
            plot_title = 'Width vs. Area'
            xlabel = 'Area'
            ylabel = 'Width'
        elif cluster_projection == '2-D: <x> vs. width':
            data = np.column_stack((char[:, 1], char[:, 3]))
            projection_fname = 'meanx_width'
            plot_title = '<X> vs. Width'
            xlabel = '<X>'
            ylabel = 'Width'
        projection_details = [projection_title, projection_fname]

        tol = self.tolerance.get()
        max_iter = self.max_iter.get()
        n_init = self.n_init.get()
        # ==========================================================================================
        # Outlier removal mode.
        # In -> data.
        # Out -> data_cleaned, data_cleaned_indices, data_outliers, data_outlier_indices
        data_outliers = []
        data_outliers_indices = []
        data_cleaned = []
        data_cleaned_indices = []
        if self.remove_outliers.get():
            outlier_mode = self.outlier_mode.get()
            if outlier_mode == 'dbscan':
                outlier_param = self.dbscan_eps.get()
                dbscan = DBSCAN(eps=outlier_param).fit(data)
                labels = dbscan.labels_
                for x in range(len(labels)):
                    if labels[x] == -1:
                        data_outliers.append(data[x])
                        data_outliers_indices.append(x)
                    if labels[x] != -1:
                        data_cleaned.append(data[x])
                        data_cleaned_indices.append(x)
                data_outliers = np.array(data_outliers)
                data_cleaned = np.array(data_cleaned)
            if outlier_mode == 'gmm':
                outlier_param = self.percentile.get()
                n_clstr = np.arange(2, 25)
                clfs = [GaussianMixture(n_components=n, tol=0.001, max_iter=100, n_init=5).fit(data)
                        for n in n_clstr]
                bics = [clf.bic(data) for clf in clfs]
                self.reset_for_2d(
                    plot_title='Bayesian Information Criterion', xlabel='# of Gaussians',
                    ylabel='Score')
                self.plot_pm.plot_line(
                    n_clstr, bics, weight=0.5, marker='.', picker=self.controller.picker)
                n_components = askinteger(
                    'Number of Clusters', 'Enter the number of clusters to fit the data to.')
                gmm = GaussianMixture(
                    n_components=n_components, tol=tol, max_iter=max_iter, n_init=n_init)
                gmm.fit(data)
                densities = gmm.score_samples(data)
                density_threshold = np.percentile(densities, outlier_param)
                for x in range(len(densities)):
                    if densities[x] < density_threshold:
                        data_outliers.append(data[x])
                        data_outliers_indices.append(x)
                    if densities[x] > density_threshold:
                        data_cleaned.append(data[x])
                        data_cleaned_indices.append(x)
        else:
            data_cleaned = data
            for x in range(len(data_cleaned)):
                data_cleaned_indices.append(x)
        data_outliers = np.array(data_outliers)
        data_cleaned = np.array(data_cleaned)
        data_outliers_indices = np.array(data_outliers_indices)
        data_cleaned_indices = np.array(data_cleaned_indices)
        # End outlier removal
        # ==========================================================================================
        char_columns = char.shape[1]
        norm_columns = norm.shape[1]
        char_cleaned = np.zeros((len(data_cleaned_indices), char_columns))
        norm_cleaned = np.zeros((len(data_cleaned_indices), norm_columns))
        char_outliers = np.zeros((len(data_outliers), char_columns))
        norm_outliers = np.zeros((len(data_outliers), norm_columns))
        for x in range(len(data_cleaned_indices)):
            char_cleaned[x, :] = char[data_cleaned_indices[x], :]
            norm_cleaned[x, :] = norm[data_cleaned_indices[x], :]
        for x in range(len(data_outliers_indices)):
            char_outliers[x, :] = char[data_outliers_indices[x], :]
            norm_outliers[x, :] = norm[data_outliers_indices[x], :]
        n_clstr = np.arange(2, 25)
        clfs = [GaussianMixture(
            n_components=n, tol=0.001, max_iter=100, n_init=5).fit(data_cleaned) for n in n_clstr]
        bics = [clf.bic(data_cleaned) for clf in clfs]
        self.reset_for_2d(
            plot_title='Bayesian Information Criterion', xlabel='# of Gaussians', ylabel='Score')
        self.plot_pm.plot_line(n_clstr, bics, weight=0.5, marker='.', picker=self.controller.picker)

        n_components = askinteger(
            'Number of Clusters', 'How many Gaussians would you like to fit the data to?')
        gmm = GaussianMixture(
            n_components=n_components, tol=tol, max_iter=max_iter, n_init=n_init)
        gmm.fit(data_cleaned)
        covs = gmm.covariances_
        means = gmm.means_

        if cluster_projection in ['2-D: Area vs. <x>', '2-D: Area vs. width', '2-D: <x> vs. width']:
            self.reset_for_2d(plot_title=plot_title, xlabel=xlabel, ylabel=ylabel)
            self.plot_pm.plot_line(
                data[:, 0], data[:, 1], color='black', marker='.', weight=0,
                picker=self.controller.picker)
            try:
                self.plot_pm.plot_line(
                    data_outliers[:, 0], data_outliers[:, 1], color='red', marker='o', weight=0,
                    picker=self.controller.picker)
            except IndexError:
                pass
            for x in range(len(covs)):
                self.plot_pm.plot_ellipse(covs[x], center=means[x], alpha=0.3)
        else:
            self.reset_for_3d(plot_title=plot_title, xlabel=xlabel, ylabel=ylabel, zlabel=zlabel)
            self.plot_pm.scatter_3d_single(
                data[:, 0], data[:, 1], data[:, 2], color='black', marker='.')
            try:
                self.plot_pm.scatter_3d_single(
                    data_outliers[:, 0], data_outliers[:, 1], data_outliers[:, 2], color='red',
                    marker='o')
            except IndexError:
                pass
            for x in range(len(covs)):
                x_, y_, z_ = means[x][0], means[x][1], means[x][2]
                c = [x_, y_, z_]
                cov = covs[x]
                self.plot_pm.scatter_3d_single(x_, y_, z_, color='lime', marker='o')
                self.plot_pm.plot_ellipsoid(cov, center=c, sigma_mult=3)
                self.plot_pm.canvas.draw()
        self.plot_pm.canvas.draw()

        hard_cluster = gmm.fit_predict(data_cleaned)
        soft_cluster = gmm.predict_proba(data_cleaned)
        self.find_clusters_lock.set(0)
        self.page.save_temp_file('projection_details', projection_details)
        self.page.save_temp_file('gmm_means', means)
        self.page.save_temp_file('gmm_covs', covs)
        self.page.save_temp_file('hard_cluster', hard_cluster)
        self.page.save_temp_file('soft_cluster', soft_cluster)
        self.page.save_temp_file('char_cleaned', char_cleaned)
        self.page.save_temp_file('norm_cleaned', norm_cleaned)
        self.page.save_temp_file('char_outliers', char_outliers)
        self.page.save_temp_file('norm_outliers', norm_outliers)

    def cluster_save(self):
        """
        Permanently save the files that were temporarily saved with self.cluster().

        Save files with a user provided name functioning as the base name for all files saved as a
        result of this method. Descriptor words are concatenated with the base name to differentiate
        the files.

        Files Saved:
            '{base_name}_gmm_cluster_summary.csv' (DataFrame):
                Results of final GMM clustering.
                Shape:
                    If loading into Excel: (# of transitions , # of clusters + 5)
                    If loading into DataFrame: (# of transitions , # of clusters + 4)
                col[0] -> index (only relevant if loading into Excel)
                col[1] -> frequency
                col[2] -> mean x
                col[3] -> area under curve
                col[4] -> curve width
                col[5] -> hard cluster assignment
                col[6:] -> soft cluster probabilities of each cluster
            '{base_name}_gmm_cluster_outliers.csv' (DataFrame):
                Outliers removed from data set.
                Shape:
                    If loading into Excel: (# of transitions , 5)
                    If loading into DataFrame: (# of transitions , 4)
                col[0] -> index (only relevant if loading into Excel)
                col[1] -> frequency
                col[2] -> mean x
                col[3] -> area under curve
                col[4] -> curve width
            '{base_name}_means.npy' (binary array):
                Coordinates of Gaussian centers. Used for cluster visualization.
                Shape: (# of clusters , # of characterization parameters)
                col[0] -> x vals
                col[1] -> y vals
                col[2] -> z vals
            '{base_name}_covariances.npy' (binary array):
                Covariance matrices of Gaussians. Square matrices. Either a 2x2 matrices or 3x3
                matrices. Used for cluster visualization.
                Shape: (# of clusters , # of characterization params , # of characterization params)
                covs[0] -> covariance matrix of cluster 1.
                covs[1] -> covariance matrix of cluster 2.
                covs[2] -> etc.
        """
        if self.find_clusters_lock.get():
            showerror('Error', message='Cluster spectra before proceeding to this step.')
            return
        projection_details = self.page.load_temp_file('projection_details.npy')
        projection_fname = projection_details[1]
        char_cleaned = self.page.load_temp_file('char_cleaned.npy')
        char_outliers = self.page.load_temp_file('char_outliers.npy')
        gmm_means = self.page.load_temp_file('gmm_means.npy')
        gmm_covs = self.page.load_temp_file('gmm_covs.npy')
        hard_cluster = self.page.load_temp_file('hard_cluster.npy')
        soft_cluster = self.page.load_temp_file('soft_cluster.npy')

        outlier_col_headers = ['Freq. (MHz)', '<X>', 'Area Under Curve', 'HWHM']
        outliers_df = pd.DataFrame(char_outliers, columns=outlier_col_headers)
        char_col_headers = ['Freq. (MHz)', '<X>', 'Area Under Curve', 'HWHM']
        char_col_headers.append('Hard Cluster')
        for col in range(soft_cluster.shape[1]):
            string = 'Soft Cluster ' + str(col)
            char_col_headers.append(string)
        clean_hard_soft = np.column_stack((char_cleaned, hard_cluster, soft_cluster))
        cleaned_df = pd.DataFrame(clean_hard_soft, columns=char_col_headers)

        _path = page_funcs.list_paths(self.spec_path)
        _dir = os.path.dirname(_path[0])
        init_fname = os.path.splitext(os.path.basename(self.spec_path.get()))[0]
        init_fname = page_funcs.save_file(initialfile=init_fname, initialdir=_dir, ftype='all')
        init_fname = os.path.splitext(init_fname)[0]
        cleaned_df.to_csv(init_fname + '_gmm_cluster_summary_' + projection_fname + '.csv')
        outliers_df.to_csv(init_fname + '_gmm_cluster_outliers_' + projection_fname + '.csv')
        np.save(init_fname + '_means_' + projection_fname, gmm_means)
        np.save(init_fname + '_covariances_' + projection_fname, gmm_covs)

    @testing.collect_garbage
    def split_spectrum(self):
        """
        Split raw set of spectra into a set of spectra based on GMM clustering of signal profile
        characterization.

        For visualization purposes, each transition in the GMM cluster based spectra is represented
        by that transition from the raw spectrum with the strongest signal.

        Two splitting modes:
            1.  hard - each transition can only be assigned to one cluster, and therefore,
                will only be in one spectrum.
            2.  soft - each transition can be assigned to multiple clusters if the transition has
                to probability > 0.2 of belonging to that cluster.

        Save temporary file:
            'split_spectrum.npy' (binary array):
                Spectra split based on GMM clustering.
                Shape: (length of spectra_matrix , # of clusters + 1)
                col[0] -> frequency
                col[1] -> cluster 1 spectrum
                col[2] -> cluster 2 spectrum
                col[3] -> etc.
        """
        if self.find_clusters_lock.get():
            showerror('Error', message='Cluster spectra before proceeding to this step.')
            return
        spec_path = page_funcs.list_paths(self.spec_path)[0]
        spectra_obj = Spectrum(spec_path)
        spectra_matrix = spectra_obj.spectrum

        norm = self.page.load_temp_file('norm_cleaned.npy')
        freqs = norm[:, 0]
        intensities = norm[:, 2:]
        strongest_spectrum = [
            np.where(intensities[x, :] == 1.)[0][0] for x in range(len(intensities))]

        projection_details = self.page.load_temp_file('projection_details.npy')
        projection_title = projection_details[0]

        mode = self.soft_hard.get()
        if mode == 'hard':
            hard = self.page.load_temp_file('hard_cluster.npy')
            num_groups = int(np.max(hard) + 1)
            # Create empty lists to group the spectra by predicted group. Populate 'groups' with
            # transition frequency and spectrum label with the greatest intensity.
            groups = [[] for _ in range(num_groups)]
            for i in range(len(hard)):
                group = int(hard[i])
                groups[group].append([freqs[i], strongest_spectrum[i]])
        elif mode == 'soft':
            prob_thresh = self.probability_thresh.get()
            soft = self.page.load_temp_file('soft_cluster.npy')
            groups = [[] for _ in range(soft.shape[1])]
            splits = []
            for x in range(len(soft)):
                hits = [
                    (group, prob) for group, prob in enumerate(soft[x, :]) if prob > prob_thresh]
                if len(hits) > 1:
                    splits.append([freqs[x], strongest_spectrum[x] + 1])
                for group, prob in hits:
                    groups[group].append([freqs[x], strongest_spectrum[x]])
        split_spectra = np.zeros((len(spectra_matrix), len(groups) + 1))
        split_spectra[:, 0] = spectra_matrix[:, 0]
        # Populate transition windows with spectral signal from spectrum with greatest intensity
        # for that window.
        ps = spectra_obj.point_spacing
        lw = self.line_width.get()
        if (lw / ps) % 2 != 0:
            lw = lw + ps
        for i in range(len(groups)):
            group = groups[i]
            freqs = [group[x][0] for x in range(len(group))]
            max_spec = [group[x][1] for x in range(len(group))]
            center_rows = [spectra_obj.freq_to_row(freqs[int(x)]) for x in range(len(freqs))]
            for j in range(len(freqs)):
                center_row = center_rows[j]
                row_min = int(center_row - ((lw / ps) / 2))
                row_max = int(center_row + ((lw / ps) / 2) + ps)
                spec = max_spec[j] + 1
                target = spectra_matrix[row_min:row_max, spec]
                split_spectra[row_min:row_max, i + 1] = target
        self.page.save_temp_file('split_spectrum', split_spectra)
        pt = "Split Spectrum: " + projection_title
        self.reset_for_2d(plot_title=pt, xlabel="Frequency / MHz", ylabel="Intensity / mV")
        for x in range(1, split_spectra.shape[1]):
            self.plot_pm.plot_line(
                split_spectra[:, 0], split_spectra[:, x], picker=self.controller.picker)
        self.plot_pm.canvas.draw()
        self.split_spectra_lock.set(0)

    def split_save(self):
        """
        Permanently save the file that was temporarily saved with self.split_spectrum().

        Save file with a user provided name functioning as the base name for all files saved as a
        result of this method. '_split_' and projection_fname are concatenated with the base name.

        Files saved:
            '{base_name}_split_{projection_fname}.ft' (array):
                Matrix of spectra split according to GMM clustering.
                Shape: (length of spectra_matrix , # of clusters + 1)
                col[0] -> frequency
                col[1] -> cluster 1 spectrum
                col[2] -> cluster 2 spectrum
                col[3] -> etc.
        """
        if self.split_spectra_lock.get():
            showerror('Error', message='Split spectra before proceeding to this step.')
            return
        split_spectrum = self.page.load_temp_file('split_spectrum.npy')
        projection_details = self.page.load_temp_file('projection_details.npy')
        projection_fname = projection_details[1]
        fmt = ['%.4f']
        for col in range(1, split_spectrum.shape[1]):
            fmt.append('%.8f')
        _path = page_funcs.list_paths(self.spec_path)
        _dir = os.path.dirname(_path[0])
        init_fname = os.path.splitext(os.path.basename(self.spec_path.get()))[0]
        init_fname = init_fname + '_split_' + projection_fname
        fname = page_funcs.save_file(
            initialfile=init_fname, initialdir=_dir, ftype='ft', defaultextension='.ft')
        np.savetxt(fname, split_spectrum, fmt=fmt)

    def single_update(self):
        """ Change plot projection of 'Characterize Transitions: Specific Component' section. """
        if self.specific_component_lock.get():
            showerror('Error', message='Characterize transitions before changing projection.')
            return
        self.change_projection(mode='known')

    def multiple_update(self):
        """ Change plot projection for the 'Characterize Transitions: All Components' section. """
        if self.all_components_lock.get():
            showerror('Error', message='Characterize transitions before changing projection.')
            return
        self.change_projection(mode='unknown')

    def save_single(self):
        """
        Permanently save the files that were temporarily saved with self.characterize_single().

        Two files saved:
            '{base_name}_normalized_signals.csv' (DataFrame):
                Normalized signal profiles
                Shape:
                    If loading into Excel: (# of transitions : # of raw spectra + 3)
                    If loading into DataFrame: (# of transitions : # of raw spectra + 2)
                col[0] -> index (only relevant if loading into Excel)
                col[1] -> frequency
                col[2] -> intensity of strongest signal observed. Normalization factor.
                col[3] -> normalized intensity of transition in first spectrum.
                col[4] -> normalized intensity of transition in second spectrum.
                col[5:] -> etc.
            2. 'base_name_transition_characterization.csv' (DataFrame):
                Characterization of signal profiles (mean x, area under curve, and curve width)
                Shape:
                    If loading into Excel: (# of transitions : 5)
                    If loading into DataFrame: (# of transitions : 4)
                col[0] -> index (only relevant if loading into excel)
                col[1] -> frequency
                col[2] -> mean x
                col[3] -> area under curve
                col[4] -> curve width
        """
        if self.specific_component_lock.get():
            showerror('Error', message='Characterize transitions before saving results.')
            return
        norm = self.page.load_temp_file('known_norm.npy')
        char = self.page.load_temp_file('known_char.npy')
        init_fname = os.path.splitext(os.path.basename(self.cat_path.get()))[0]
        init_fname = page_funcs.save_file(
            initialfile=init_fname, ftype='csv', defaultextension='.csv')
        init_fname = os.path.splitext(init_fname)[0]
        norm_df = pd.DataFrame(norm)
        norm_df.style.format("{:.6f}")
        norm_df.to_csv(init_fname + '_normalized_signals.csv')
        column_headers = np.array(
            ('Frequency (MHz)', '<X>', 'Area Under Curve', 'HWHM'))
        char_df = pd.DataFrame(char, columns=column_headers)
        char_df.style.format(
            {'Frequency (MHz)': "{:.4f}", '<X>': "{:.6f}", 'Area Under Curve': "{:.6f}",
             'HWHM': "{:.6f}"})
        char_df.to_csv(init_fname + '_transition_characterization.csv')

    def save_mixture(self):
        """
        Permanently save the files that were temporarily saved with self.characterize_all().

        User prompted to provide a base name in file dialog box.
        Two files saved:
            '{base_name}_normalized_signals.csv' (DataFrame):
                Normalized signal profiles for each transition.
                Shape:
                    If loading into Excel: (# of transitions : # of raw spectra + 3)
                    If loading into DataFrame: (# of transitions : # of raw spectra + 2)
                col[0] -> index (only relevant if loading into excel)
                col[1] -> frequency
                col[2] -> intensity of strongest signal observed. Normalization factor.
                col[3] -> normalized intensity of transition in first spectrum.
                col[4] -> normalized intensity of transition in second spectrum.
                col[5] -> etc.
            '{base_name}_transition_characterization.csv' (DataFrame):
                Characterization of signal profiles (mean x, area under curve, and curve width)
                Shape: [# of transitions : 5]
                col[0] -> index (only relevant if loading into excel)
                col[1] -> frequency
                col[2] -> mean x
                col[3] -> area under curve
                col[4] -> curve width
        """
        if self.all_components_lock.get():
            showerror('Error', message='Characterize transitions before saving results.')
            return
        norm = self.page.load_temp_file('unknown_norm.npy')
        char = self.page.load_temp_file('unknown_char.npy')
        init_fname = os.path.splitext(os.path.basename(self.spec_path.get()))[0]
        init_fname = page_funcs.save_file(
            initialfile=init_fname, ftype='csv', defaultextension='.csv')
        init_fname = os.path.splitext(init_fname)[0]
        pd.DataFrame(norm).to_csv(init_fname + '_normalized_signals.csv')
        column_headers = np.array(
            ('Frequency (MHz)', '<X>', 'Area Under Curve', 'HWHM'))
        df = pd.DataFrame(char, columns=column_headers)
        df.style.format(
            {'Frequency (MHz)': "{:.4f}", '<X>': "{:.6f}", 'Area Under Curve': "{:.6f}",
             'HWHM': "{:.6f}"})
        df.to_csv(init_fname + '_transition_characterization.csv')

    def reset_for_2d(self, plot_title=None, xlabel=None, ylabel=None):
        """ Prepare plot for 2d projection. """
        self.plot_pm.figure.clf()
        self.plot_pm.toolbar.destroy()
        if plot_title is None:
            plot_title = self.plot_title.get()
        if xlabel is None:
            xlabel = self.xlabel.get()
        if ylabel is None:
            ylabel = self.ylabel.get()
        self.plot_pm = PlotManager(
            frame=self.plot_frame, figsize=(16, 8), dpi=100, subplotshape=111,
            plot_title=plot_title, xlabel=xlabel, ylabel=ylabel, x_min='Auto', x_max='Auto',
            y_min='Auto', y_max='Auto', legend_show=1, legend_font=10, legend_loc=0, left=0.05,
            right=0.98, top=0.95, bottom=0.09, row=0, column=0, columnspan=2, toolbar=True,
            toolrow=1, toolcol=0, toolpady=2, toolsticky='w')

    def reset_for_3d(self, plot_title=None, xlabel=None, ylabel=None, zlabel=None):
        """ Prepare plot for 3d projection. """
        self.plot_pm.figure.clf()
        self.plot_pm.toolbar.destroy()
        if plot_title is None:
            plot_title = self.plot_title.get()
        if xlabel is None:
            xlabel = self.xlabel.get()
        if ylabel is None:
            ylabel = self.ylabel.get()
        if zlabel is None:
            zlabel = self.zlabel.get()
        self.plot_pm = PlotManager(
            frame=self.plot_frame, figsize=(16, 8), dpi=100, subplotshape=111, projection='3d',
            plot_title=plot_title, xlabel=xlabel, ylabel=ylabel, zlabel=zlabel, x_min='Auto',
            x_max='Auto', y_min='Auto', y_max='Auto', legend_show=1, legend_font=10, legend_loc=0,
            left=0.05, right=0.98, top=0.95, bottom=0.09, row=0, column=0, columnspan=2,
            toolbar=True, toolrow=1, toolcol=0, toolpady=2, toolsticky='w')

    def change_projection(self, mode='known'):
        """
        Change plot projection without recalculating intensity profiles.

        Parameters:
            mode (str):
                'known':
                    enables '2-D: Intensity vs. Time' projection. *.cat file must be provided.
                    Only transitions from *.cat are characterized.
                'unknown':
                    Does not require *.cat. All transitions above threshold in spectra matrix
                    are characterized.
        """
        if mode == 'known':
            char = self.page.load_temp_file('known_char.npy')
            norm = self.page.load_temp_file('known_norm.npy')
            plot_mode = self.known_plot.get()
        elif mode == 'unknown':
            char = self.page.load_temp_file('unknown_char.npy')
            norm = self.page.load_temp_file('unknown_norm.npy')
            plot_mode = self.unknown_plot.get()
        mean_x = char[:, 1]
        area = char[:, 2]
        width = char[:, 3]
        if plot_mode == '3-D: Area vs. <x> vs. width':
            self.reset_for_3d(
                plot_title='Width vs. Area vs <X>', xlabel='<X>', ylabel='Area', zlabel='Width')
            self.plot_pm.scatter_3d_single(mean_x, area, width, color='blue', marker='.')
            self.plot_pm.set_labels()
        elif plot_mode == '2-D: Area vs. <x>':
            self.reset_for_2d(plot_title='Area vs <X>', xlabel='<X>', ylabel='Area')
            self.plot_pm.plot_line(
                mean_x, area, weight=0, marker='.', picker=self.controller.picker)
            self.plot_pm.set_labels()
        elif plot_mode == '2-D: Area vs. width':
            self.reset_for_2d(plot_title='Width vs. Area', xlabel='Width', ylabel='Area')
            self.plot_pm.plot_line(
                width, area, weight=0, marker='.', picker=self.controller.picker)
            self.plot_pm.set_labels()
        elif plot_mode == '2-D: <x> vs. width':
            self.reset_for_2d(plot_title='<X> vs. Width', xlabel='Width', ylabel='<X>')
            self.plot_pm.plot_line(
                width, mean_x, weight=0, marker='.', picker=self.controller.picker)
            self.plot_pm.set_labels()
        elif plot_mode == '2-D: Intensity vs. Time':
            self.reset_for_2d(
                plot_title='Transition Intensity vs. Time', xlabel='Time (arb.)',
                ylabel='Norm. Intensity')
            for x in range(self.topN.get()):
                norm_row = norm[x]
                enum = [x for x, row in enumerate(norm_row[1:])]
                self.plot_pm.plot_line(
                    enum, norm_row[1:], weight=0.5, marker='.', picker=self.controller.picker)
            self.plot_pm.set_labels()
        self.plot_pm.zoom()
        self.plot_pm.canvas.draw()
        self.plot_pm.toolbar.update()

    def update_plot(self):
        """ Update plot. """
        self.plot_pm.set_labels(plot_title=self.plot_title.get(), xlabel=self.xlabel.get(),
                                ylabel=self.ylabel.get(), zlabel=self.zlabel.get())
        self.plot_pm.canvas.draw()


def outlier_test(arr, cols=None, num_std=None):
    """
    Remove arr[row, :] from arr if arr[row, col] is not within (num_std * standard deviations) of
    column mean.

    Parameters:
        arr (np.array):
            Array to filter
        cols (list):
            List of column indices. Array is filtered using these columns.
            Default: number of columns.
        num_std (float):
            standard deviation multiplier
            Default: 3
    Returns:
        filtered (np.array):
            Array with rows removed.
        avgs (np.array):
            Column averages.
        stds (np.array):
            Column standard deviations.
    """
    if num_std is None:
        num_std = 3
    filtered = arr.tolist()
    if cols is None:
        cols = np.arange(0, arr.shape[1])
    avgs = []
    stds = []
    for col in cols:
        outlier_bool = True
        while outlier_bool:
            column = [filtered[x][col] for x in range(len(filtered))]
            lower_bound = np.mean(column) - num_std * np.std(column)
            upper_bound = np.mean(column) + num_std * np.std(column)
            outliers = []
            for x in range(len(column)):
                if column[x] < lower_bound:
                    outliers.append(x)
                elif column[x] > upper_bound:
                    outliers.append(x)
            if len(outliers) != 0:
                outliers = sorted(outliers, reverse=True)
                for outlier in outliers:
                    del filtered[outlier]
            else:
                outlier_bool = False
        avgs.append(np.mean(column))
        stds.append(np.std(column))
    filtered = np.array(filtered)
    avgs = np.array(avgs)
    stds = np.array(stds)
    return filtered, avgs, stds


def mean_x_axis(intensity_list, xmin=None, x_increment=None):
    """
    Calculate the average value along the x-axis for intensity vs. time data.

    This method is for use with a matrix of multiple spectra, col[0] containing shared frequencies
    and subsequent columns containing spectral intensity of independent spectra. Calling this
    method calculates the expectation value along the time-axis for a single transition.

    Parameters:
        intensity_list (list):
            Signal intensities of a single transition. Normalization not required.
        xmin (float):
            Lower bound for the x-axis. Time or spectrum number.
            Default:  1
        x_increment (float):
            Increment between adjacent x-axis values.
            Default:  1
    Return:
        mean_x (float):
            average value along x-axis.
    """
    if xmin is None:
        xmin = 1
    if x_increment is None:
        x_increment = 1
    xmax = xmin + x_increment * len(intensity_list)
    xvals = np.arange(xmin, xmax, x_increment)
    weighted_intensity = [intensity_list[x] * xvals[x] for x in range(len(intensity_list))]
    intensity_sum = sum(intensity_list)
    weighted_intensity_sum = sum(weighted_intensity)
    mean_x = weighted_intensity_sum / intensity_sum
    return mean_x


def area_under_curve(intensity_list, xmin=None, x_increment=None):
    """
    Calculate the area under the curve created by plotting spectral intensity as a function of time.

    This method is for use with a matrix of multiple spectra, col[0] containing shared frequencies
    and subsequent columns containing spectral intensity of independent spectra. Calling this
    method calculates the area under the curve created when the intensity of a transition is
    plotted against time/spectrum number.

    Parameters:
        intensity_list (list):
            Signal intensities of a single transition. Normalization required.
        xmin (float):
            Lower bound for the x-axis. Time or spectrum number.
            Default:  1
        x_increment (float):
            Increment between adjacent x-axis values.
            Default:  1
    Returns:
        area (float):
            Area under the curve.
    """
    if xmin is None:
        xmin = 1
    if x_increment is None:
        x_increment = 1
    xmax = xmin + x_increment * len(intensity_list)
    xvals = np.arange(xmin, xmax, x_increment)
    area = np.trapz(intensity_list, xvals, dx=x_increment)
    return area


def curve_width(intensity_list, xmin=None, x_increment=None):
    """
    Calculate width of curve created by plotting spectral intensity as a function of time.

    This method is for use with a matrix of multiple spectra, col[0] containing shared frequencies
    and subsequent columns containing spectral intensity of independent spectra. This method
    calculates the width of the curve created when the intensity of a transition is plotted against
    time/spectrum number. How the width is calculated depends on the shape of the curve.

    If a single half-max point exists on the curve, the width is calculated using the half-max
    point and the appropriate boundary of the x-axis (upper or lower boundary). The difference
    between the half-max point and the boundary is returned.

    If two half-max points exist in the plot range, half width at half max is returned.

    If more than two half-max points are found, the width is calculated to be the difference
    between the outer-most set of points and returned.

    Along with the width, the number of half-max points is returned.

    Parameters:
        intensity_list (list):
            Signal intensities of a single transition. Normalization required.
        xmin (float):
            Lower bound for the x-axis. Time or spectrum number.
            Default: 1
        x_increment (float):
            Increment between adjacent x-axis values.
            Default: 1
    Returns:
        (num_hm, width) (tuple):
            Number of half-max points, curve width calculated according to rules above.
    """
    if xmin is None:
        xmin = 1
    if x_increment is None:
        x_increment = 1
    xmax = xmin + x_increment * len(intensity_list)
    xvals = np.arange(xmin, xmax, x_increment)
    index_max_intensity = np.argmax(intensity_list)
    x_loc_max_intensity = xvals[index_max_intensity]

    ints = intensity_list
    xmin_xmax_segments = [[xvals[j], xvals[j + 1]] for j in range(len(xvals) - 1)]
    slopes = [(ints[j + 1] - ints[j]) / (xvals[j + 1] - xvals[j]) for j in range(len(ints) - 1)]
    y_intercepts = [ints[j] - slopes[j] * xvals[j] for j in range(len(ints) - 1)]
    x_where_segment_equals_half = [
        ((0.5 - float(y_intercepts[k])) / slopes[k]) for k in range(len(slopes))]
    HWHM_points = []
    for z in range(len(x_where_segment_equals_half)):
        xmin_xmax_segment = xmin_xmax_segments[z]
        xmin = xmin_xmax_segment[0]
        xmax = xmin_xmax_segment[1]
        if xmin < x_where_segment_equals_half[z] < xmax:
            HWHM_points.append(x_where_segment_equals_half[z])
    if len(HWHM_points) == 1:
        if HWHM_points[0] > x_loc_max_intensity:
            width = HWHM_points[0]
        elif HWHM_points[0] < x_loc_max_intensity:
            width = xvals[-1] - HWHM_points[0]
    elif len(HWHM_points) == 2:
        width = abs(HWHM_points[0] - HWHM_points[1]) / 2
    elif len(HWHM_points) > 2:
        sort = sorted(HWHM_points)
        width = sort[-1] - sort[0]
    elif len(HWHM_points) == 0:
        width = 0
    num_hm_points = len(HWHM_points)
    class_width = (num_hm_points, width)
    return class_width
