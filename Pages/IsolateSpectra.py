"""
Author: Channing West
Changelog: 3/18/2019
"""

import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from Pages.PageFormat import PageFormat
from Spectrum import Spectrum
from Pickett import Cat
from TkAgg_Plotting import PlotManager, SpecPlot
import os
import Pages.PageFormat as page_funcs
import testing


r = tk.RIGHT
c = tk.CENTER
l = tk.LEFT
h10bL = 'h10b.TLabel'
h12bB = 'h12b.TButton'
h8bB = 'h8b.TButton'
width10_h8bB = {'width': 10, 'style': h8bB}
width20_h12bB = {'width': 20, 'style': h12bB}
cspan5_x2_y10_ew = {'columnspan': 5, 'padx': 2, 'pady': 10, 'sticky': 'ew'}
pad2_e = {'padx': 2, 'pady': 2, 'sticky': 'e'}
pad2_w = {'padx': 2, 'pady': 2, 'sticky': 'w'}
pad2_ew = {'padx': 2, 'pady': 2, 'sticky': 'ew'}
pad2_sw = {'padx': 2, 'pady': 2, 'sticky': 'sw'}
h10bL_l = {'style': h10bL, 'justify': l}
rspan2x20y2ns = {'rowspan': 2, 'padx': 20, 'pady': 2, 'sticky': 'ns'}
rspan2x50y2ns = {'rowspan': 2, 'padx': 50, 'pady': 2, 'sticky': 'ns'}


class IsolateSpectra(ttk.Frame):
    """
    Generate GUI. Isolate individual spectra from a composite spectrum.

    1.  Upload a target spectrum. This is what will be modified.
    2.  Upload up to 3 peak pick spectra. These are used to identify peaks in the target spectrum.
    3.  Enter intensity threshold for an experimental spectrum or dynamic range for a simulation.
        PLOT buttons are useful for finding appropriate values.
    4.  Enter baseline width, the width along the frequency axis targeted for each
        cut/revealed transition. Section is centered at peak transition intensity.
    5.  Press CUT or REVEAL.
        -   CUT removes transitions from Peak Pick Files from Target Spectrum if transitions
            are above intensity cutoff or dynamic range cutoff.
        -   REVEAL removes everything except Peak Pick Files from Target Spectrum if
            transitions are above intensity cutoff or dynamic range cutoff.
    6.  After CUT/REVEAL, display three plots.
        a.  Top left - unmodified spectrum.
        b.  top right - selected transitions are marked on the unmodified spectrum. If more than
            one Peak Pick File is uploaded, unique markers are used for each file.
        c.  Bottom plot - modified spectrum.
    7.  Press SAVE to name and save modified spectrum.
    Buttons:
        NAVIGATION BAR
            HOME: Return plot to original zoom.
            BACK: Return to previous zoom/pan setting.
            FORWARD: Undo BACK
            PAN: click and drag plot. Scroll to zoom along one axis.
            ZOOM: select plot region to zoom into focus.
            ADJUST MARGINS: Adjust the dimensions of the plot. Useful for figures.
            SAVE IMAGE: Save an image of the plot. Not interactive.
        BROWSE
            Open file explorer
        PLOT
            Graph spectrum or simulation. Useful for choosing intensity threshold or dynamic range.
        CUT
            Remove Peak Pick Files from Target Spectrum.
        REVEAL
            Remove everything except Peak Pick Files from Target Spectrum
        SAVE
            Save modified spectrum
    """
    default = {'target_spec': 'None',
               'pp_file_1': 'None',
               'pp_file_2': 'None',
               'pp_file_3': 'None',
               'pp_1_thresh': 0.001,
               'pp_2_thresh': 0.001,
               'pp_3_thresh': 0.001,
               'fwhm': 0.250}

    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Isolate Spectra"
        self.target_file = tk.StringVar()
        self.target_file.set(IsolateSpectra.default['target_spec'])
        self.pp_file_1 = tk.StringVar()
        self.pp_file_1.set(IsolateSpectra.default['pp_file_1'])
        self.pp_1_thresh = tk.StringVar()
        self.pp_1_thresh.set(IsolateSpectra.default['pp_1_thresh'])
        self.pp_file_2 = tk.StringVar()
        self.pp_file_2.set(IsolateSpectra.default['pp_file_2'])
        self.pp_2_thresh = tk.StringVar()
        self.pp_2_thresh.set(IsolateSpectra.default['pp_2_thresh'])
        self.pp_file_3 = tk.StringVar()
        self.pp_file_3.set(IsolateSpectra.default['pp_file_3'])
        self.pp_3_thresh = tk.StringVar()
        self.pp_3_thresh.set(IsolateSpectra.default['pp_3_thresh'])
        self.line_width = tk.DoubleVar()
        self.line_width.set(IsolateSpectra.default['fwhm'])

        frame1 = ttk.Frame(self.frame)
        frame1.grid(row=0, column=0)
        frame2_1 = ttk.Frame(frame1)
        frame2_1.grid(row=2, column=0, sticky='nw')
        frame2_2 = ttk.Frame(frame1)
        frame2_2.grid(row=2, column=1, sticky='s')
        frame3 = ttk.Frame(self.frame)
        frame3.grid(row=1, column=0)
        frame4_1 = ttk.Frame(frame2_2)
        frame4_1.grid(row=2, column=0)
        frame4_2 = ttk.Frame(frame4_1)
        frame4_2.grid(row=2, column=1)
        frame4_3 = ttk.Frame(frame4_1)
        frame4_3.grid(row=2, column=3)
        # ==========================================================================================
        #                                  Unmodified Spectrum
        # ==========================================================================================
        self.unmod_pm = PlotManager(
            frame1, figsize=(10, 6), dpi=80, subplotshape=111, plot_title='Unmodified Spectrum',
            xlabel='Frequency / MHz', ylabel='Intensity / mV', x_min='Auto', x_max='Auto',
            y_min='Auto', y_max='Auto', left=0.08, right=0.98, top=0.92, bottom=0.1, row=0,
            column=0, columnspan=1, toolbar=True, toolrow=1, toolcol=0, toolcspan=1, toolpady=5,
            toolsticky='w')
        self.unmod_plot = SpecPlot(self.unmod_pm.ax, show=1, color='black', weight=0.75)
        # ==========================================================================================
        #                                  Peak Pick Spectrum
        # ==========================================================================================
        self.pp_pm = PlotManager(
            frame1, figsize=(10, 6), dpi=80, subplotshape=111, plot_title='Peak Pick',
            xlabel='Frequency / MHz', ylabel='Intensity / mV', x_min='Auto', x_max='Auto',
            y_min='Auto', y_max='Auto', left=0.08, right=0.98, top=0.92, bottom=0.1, row=0,
            column=1, columnspan=1, toolbar=True, toolrow=1, toolcol=1, toolcspan=1, toolpady=5,
            toolsticky='w')
        self.pp_spec = SpecPlot(self.pp_pm.ax, show=1, color='black', weight=0.75)
        self.pp_marker_1 = SpecPlot(self.pp_pm.ax, show=1, color='red', weight=0, marker='.')
        self.pp_plot_1 = SpecPlot(self.pp_pm.ax, show=1, invert=1, color='red', weight=0.75)
        self.pp_marker_2 = SpecPlot(self.pp_pm.ax, show=1, color='blue', weight=0, marker='.')
        self.pp_plot_2 = SpecPlot(self.pp_pm.ax, show=1, invert=1, color='blue', weight=0.75)
        self.pp_marker_3 = SpecPlot(self.pp_pm.ax, show=1, color='green', weight=0, marker='.')
        self.pp_plot_3 = SpecPlot(self.pp_pm.ax, show=1, invert=1, color='green', weight=0.75)
        # ==========================================================================================
        #                        Labels, Entries, Buttons for Spectrum Upload
        # ==========================================================================================
        target_spec_L = ttk.Label(frame2_1, text='\nTarget Spectrum:', **h10bL_l)
        target_1_L = ttk.Label(frame2_1, text='1:', justify=r, style=h10bL)
        peak_pick_L = ttk.Label(frame2_1, text='Peak Pick Files:', **h10bL_l)
        thresh_L = ttk.Label(frame2_1, text='Intensity Cut-off/\nDynamic Range:', **h10bL_l)
        pp_1_L = ttk.Label(frame2_1, text='1:', justify=r, style=h10bL)
        pp_2_L = ttk.Label(frame2_1, text='2:', justify=r, style=h10bL)
        pp_3_L = ttk.Label(frame2_1, text='3:', justify=r, style=h10bL)
        target_1_E = ttk.Entry(frame2_1, textvariable=self.target_file, justify=c, width=70)
        pp_1_E = ttk.Entry(frame2_1, textvariable=self.pp_file_1, justify=c, width=70)
        pp_2_E = ttk.Entry(frame2_1, textvariable=self.pp_file_2, justify=c, width=70)
        pp_3_E = ttk.Entry(frame2_1, textvariable=self.pp_file_3, justify=c, width=70)
        pp_1_thresh_E = ttk.Entry(frame2_1, textvariable=self.pp_1_thresh, justify=c)
        pp_2_thresh_E = ttk.Entry(frame2_1, textvariable=self.pp_2_thresh, justify=c)
        pp_3_thresh_E = ttk.Entry(frame2_1, textvariable=self.pp_3_thresh, justify=c)

        target_browse = ttk.Button(
            frame2_1, text='Browse', **width10_h8bB,
            command=lambda: page_funcs.write_path(self.target_file, eb_var=target_1_E, ftype='ft'))
        target_plot = ttk.Button(
            frame2_1, text='Plot', **width10_h8bB,
            command=lambda: self.plot_unmod(self.target_file.get()))
        pp_1_browse = ttk.Button(
            frame2_1, text='Browse', **width10_h8bB,
            command=lambda: page_funcs.write_path(
                self.pp_file_1, eb_var=pp_1_E, ftype='ft_cat_prn'))
        pp_1_plot = ttk.Button(
            frame2_1, text='Plot', **width10_h8bB,
            command=lambda: self.plot_pp(self.pp_file_1.get()))
        pp_2_browse = ttk.Button(
            frame2_1, text='Browse', **width10_h8bB, command=lambda: page_funcs.write_path(
                self.pp_file_2, eb_var=pp_2_E, ftype='ft_cat_prn'))
        pp_2_plot = ttk.Button(
            frame2_1, text='Plot', **width10_h8bB, command=lambda: self.plot_pp(
                self.pp_file_2.get()))
        pp_3_browse = ttk.Button(
            frame2_1, text='Browse', **width10_h8bB, command=lambda: page_funcs.write_path(
                self.pp_file_3, eb_var=pp_3_E, ftype='ft_cat_prn'))
        pp_3_plot = ttk.Button(
            frame2_1, text='Plot', **width10_h8bB, command=lambda: self.plot_pp(
                self.pp_file_3.get()))
        target_spec_L.grid(row=0, column=1, columnspan=2, **pad2_sw)
        target_1_L.grid(row=1, column=0, **pad2_e)
        target_1_E.grid(row=1, column=1, columnspan=2, **pad2_ew)
        target_browse.grid(row=1, column=3, **pad2_ew)
        target_plot.grid(row=1, column=4, **pad2_ew)
        peak_pick_L.grid(row=2, column=1, **pad2_sw)
        thresh_L.grid(row=2, column=2, **pad2_sw)
        pp_1_L.grid(row=3, column=0, **pad2_e)
        pp_1_E.grid(row=3, column=1, **pad2_ew)
        pp_1_thresh_E.grid(row=3, column=2, **pad2_ew)
        pp_1_browse.grid(row=3, column=3, **pad2_ew)
        pp_1_plot.grid(row=3, column=4, **pad2_ew)
        pp_2_L.grid(row=4, column=0, **pad2_e)
        pp_2_E.grid(row=4, column=1, **pad2_ew)
        pp_2_thresh_E.grid(row=4, column=2, **pad2_ew)
        pp_2_browse.grid(row=4, column=3, **pad2_ew)
        pp_2_plot.grid(row=4, column=4, **pad2_ew)
        pp_3_L.grid(row=5, column=0, **pad2_e)
        pp_3_E.grid(row=5, column=1, **pad2_ew)
        pp_3_thresh_E.grid(row=5, column=2, **pad2_ew)
        pp_3_browse.grid(row=5, column=3, **pad2_ew)
        pp_3_plot.grid(row=5, column=4, **pad2_ew)
        # ==========================================================================================
        #                                         modified Spectrum
        # ==========================================================================================
        self.mod_pm = PlotManager(
            frame3, figsize=(16, 7), dpi=100, subplotshape=111, plot_title='Modified Spectrum',
            xlabel='Frequency / MHz', ylabel='Intensity / mV', x_min='Auto', x_max='Auto',
            y_min='Auto', y_max='Auto', left=0.05, right=0.99, top=0.94, bottom=0.08, row=0,
            column=0, columnspan=1, pady=2, toolbar=True, toolrow=1, toolcol=0, toolcspan=1,
            toolpady=5, toolsticky='w')
        self.mod_plot = SpecPlot(self.mod_pm.ax, show=1, color='black', weight=0.75)
        self.mod_plot_2 = SpecPlot(self.mod_pm.ax, show=1, invert=1, color='red', weight=0.75)
        self.mod_plot_3 = SpecPlot(self.mod_pm.ax, show=1, invert=1, color='blue', weight=0.75)
        self.mod_plot_4 = SpecPlot(self.mod_pm.ax, show=1, invert=1, color='green', weight=0.75)
        frame1.grid(row=0, column=0)
        # ==========================================================================================
        #                                         Lower Frame
        # ==========================================================================================
        baseline_width_L = ttk.Label(frame4_2, text='Baseline Width (MHz):', style=h10bL, justify=r)
        line_width_E = ttk.Entry(frame4_2, textvariable=self.line_width, justify=c)
        cut_button = ttk.Button(frame4_3, text='Cut', **width20_h12bB, command=self.cut)
        reveal_button = ttk.Button(frame4_3, text='Reveal', **width20_h12bB, command=self.reveal)
        save_button = ttk.Button(
            frame4_3, text='Save Spectrum', **width20_h12bB, command=self.save_isolated)
        defaults_button = ttk.Button(
            frame4_3, text='Defaults', **width20_h12bB, command=lambda: page_funcs.clear_page(
                IsolateSpectra.default, self.attr_dict, self.mod_pm,
                self.unmod_pm, self.pp_pm))
        ttk.Separator(frame4_1, orient=tk.HORIZONTAL).grid(row=0, column=0, **cspan5_x2_y10_ew)
        ttk.Separator(frame4_1, orient=tk.HORIZONTAL).grid(row=3, column=0, **cspan5_x2_y10_ew)
        ttk.Separator(frame4_1, orient=tk.VERTICAL).grid(row=1, column=0, **rspan2x20y2ns)
        ttk.Separator(frame4_1, orient=tk.VERTICAL).grid(row=1, column=2, **rspan2x50y2ns)
        ttk.Separator(frame4_1, orient=tk.VERTICAL).grid(row=1, column=4, **rspan2x20y2ns)
        baseline_width_L.grid(row=1, column=0, rowspan=2, **pad2_ew)
        line_width_E.grid(row=1, column=1, rowspan=2, **pad2_ew)
        cut_button.pack(side='top', fill='x', expand=True, pady=10)
        reveal_button.pack(fill='x', expand=True, pady=10)
        defaults_button.pack(side='bottom', fill='x', expand=True, pady=10)
        save_button.pack(side='bottom', fill='x', expand=True, pady=10)

        self.attr_dict = {'target_spec': self.target_file,
                          'pp_file_1': self.pp_file_1,
                          'pp_file_2': self.pp_file_2,
                          'pp_file_3': self.pp_file_3,
                          'pp_1_thresh': self.pp_1_thresh,
                          'pp_2_thresh': self.pp_2_thresh,
                          'pp_3_thresh': self.pp_3_thresh,
                          'fwhm': self.line_width}

    @testing.collect_garbage
    def reveal(self):
        """
        Remove everything from Target Spectrum except transitions found in Peak Pick Files
        above threshold.

        Fill plots. Save temporary file so modified spectrum can be saved later if the user chooses.
        """
        spec_path = self.target_file.get()
        target = Spectrum(spec_path)
        target_spec = target.spectrum
        fmin = float("{0:.4f}".format(target.freq_min))
        fmax = float("{0:.4f}".format(target.freq_max))
        lw = self.line_width.get()
        ps = target.point_spacing

        reveal_array = np.zeros((len(target_spec), 2))
        reveal_array[:, 0] = target_spec[:, 0]

        path_1 = self.pp_file_1.get()
        thresh_1 = float(self.pp_1_thresh.get())
        line_1 = self.pp_plot_1
        marker_1 = self.pp_marker_1
        path_2 = self.pp_file_2.get()
        thresh_2 = float(self.pp_2_thresh.get())
        line_2 = self.pp_plot_2
        marker_2 = self.pp_marker_2
        path_3 = self.pp_file_3.get()
        thresh_3 = float(self.pp_3_thresh.get())
        line_3 = self.pp_plot_3
        marker_3 = self.pp_marker_3

        self.pp_pm.ax.cla()
        self.pp_pm.plot_line(target_spec[:, 0], target_spec[:, 1], color='black')

        for path, thresh, line, marker in ((path_1, thresh_1, line_1, marker_1),
                                           (path_2, thresh_2, line_2, marker_2),
                                           (path_3, thresh_3, line_3, marker_3)):
            if path != 'None':
                pp_ext = os.path.splitext(path)[1]
                if pp_ext in ['.ft', '.txt']:
                    spectrum = Spectrum(path)
                    pp_invert = spectrum.spectrum
                    peak_freqs = spectrum.peak_pick(thresh=thresh, sort=True)[:, 0]
                elif pp_ext == '.cat':
                    cat = Cat(path)
                    filter = cat.filter(freq_min=fmin, freq_max=fmax, dyn_range=thresh)
                    lnlst = cat.line_list(dictionary=filter)
                    filter_scale = cat.filter(freq_min=fmin, freq_max=fmax, Ka_max=3, dyn_range=10)
                    freqs_scale = list(filter_scale.keys())
                    sf = cat.scale_to_spectrum(target, freqs_scale, dictionary=filter_scale)
                    pp_invert = cat.simulate(
                        line_list=lnlst, freq_min=fmin, freq_max=fmax, step_size=ps, fwhm=lw,
                        scale_factor=sf)
                    peak_freqs = lnlst[:, 0]
                elif pp_ext == '.prn':
                    spectrum = Spectrum(path)
                    pp_invert = spectrum.spectrum
                    peak_freqs = spectrum.peak_pick(dyn_range=thresh, sort=True)[:, 0]
                target_intens = [target.get_intensity(x) for x in peak_freqs]
                if (lw / ps) % 2 != 0:
                    lw = lw + ps
                for peak in peak_freqs:
                    freq_min = peak - (lw / 2)
                    freq_max = peak + (lw / 2) + ps
                    row_min = int((freq_min - fmin) / ps)
                    row_max = int((freq_max - fmin) / ps)
                    intensity_slice = target_spec[row_min:row_max, 1]
                    reveal_array[row_min:row_max, 1] = intensity_slice
                self.pp_pm.plot_lines(
                    [pp_invert[:, 0], peak_freqs[:]], [pp_invert[:, 1], target_intens],
                    invert=[line.invert.get(), marker.invert.get()],
                    color=[line.color.get(), marker.color.get()],
                    marker=[line.marker.get(), marker.marker.get()],
                    weight=[line.weight.get(), marker.weight.get()])
            else:
                self.pp_pm.plot_lines(
                    [[], []], [[], []], invert=[line.invert.get(), marker.invert.get()],
                    color=[line.color.get(), marker.color.get()],
                    marker=[line.marker.get(), marker.marker.get()],
                    weight=[line.weight.get(), marker.weight.get()])
        self.pp_pm.set_labels()
        self.pp_pm.zoom()
        self.pp_pm.canvas.draw()
        self.pp_pm.toolbar.update()

        self.unmod_pm.ax.cla()
        self.unmod_pm.plot_line(target_spec[:, 0], target_spec[:, 1], color='black', weight=0.75)
        self.unmod_pm.set_labels()
        self.unmod_pm.zoom()
        self.unmod_pm.canvas.draw()
        self.unmod_pm.toolbar.update()

        self.mod_pm.ax.cla()
        self.mod_pm.plot_line(reveal_array[:, 0], reveal_array[:, 1], color='black', weight=0.75)
        self.mod_pm.set_labels()
        self.mod_pm.zoom()
        self.mod_pm.canvas.draw()
        self.mod_pm.toolbar.update()
        self.page.save_temp_file('isolated_spectrum', reveal_array)

    @testing.collect_garbage
    def cut(self):
        """
        Remove transitions found in Peak Pick Files above threshold from Target Spectrum.

        Fill plots. Save temporary file so that modified spectrum can be saved later if the
        user chooses.
        """
        spec_path = self.target_file.get()
        target = Spectrum(spec_path)
        target_spec = target.spectrum
        fmin = float("{0:.4f}".format(target.freq_min))
        fmax = float("{0:.4f}".format(target.freq_max))
        lw = self.line_width.get()
        ps = target.point_spacing

        path_1 = self.pp_file_1.get()
        thresh_1 = float(self.pp_1_thresh.get())
        line_1 = self.pp_plot_1
        marker_1 = self.pp_marker_1
        path_2 = self.pp_file_2.get()
        thresh_2 = float(self.pp_2_thresh.get())
        line_2 = self.pp_plot_2
        marker_2 = self.pp_marker_2
        path_3 = self.pp_file_3.get()
        thresh_3 = float(self.pp_3_thresh.get())
        line_3 = self.pp_plot_3
        marker_3 = self.pp_marker_3

        self.pp_pm.ax.cla()
        self.pp_pm.plot_line(target_spec[:, 0], target_spec[:, 1], color='black')
        copy = np.copy(target.spectrum)
        for path, thresh, line, marker in ((path_1, thresh_1, line_1, marker_1),
                                           (path_2, thresh_2, line_2, marker_2),
                                           (path_3, thresh_3, line_3, marker_3)):
            if path != 'None':
                pp_ext = os.path.splitext(path)[1]
                if pp_ext in ['.ft', '.txt']:
                    spectrum = Spectrum(path)
                    pp_invert = spectrum.spectrum
                    peak_freqs = spectrum.peak_pick(thresh=thresh, sort=True)[:, 0]
                elif pp_ext == '.cat':
                    cat = Cat(path)
                    filter = cat.filter(freq_min=fmin, freq_max=fmax, dyn_range=thresh)
                    lnlst = cat.line_list(dictionary=filter)
                    filter_scale = cat.filter(freq_min=fmin, freq_max=fmax, Ka_max=3, dyn_range=10)
                    freqs_scale = list(filter_scale.keys())
                    sf = cat.scale_to_spectrum(target, freqs_scale, dictionary=filter_scale)
                    pp_invert = cat.simulate(
                        line_list=lnlst, freq_min=fmin, freq_max=fmax, step_size=ps, fwhm=lw,
                        scale_factor=sf)
                    peak_freqs = lnlst[:, 0]
                elif pp_ext == '.prn':
                    spectrum = Spectrum(path)
                    pp_invert = spectrum.spectrum
                    peak_freqs = spectrum.peak_pick(dyn_range=thresh, sort=True)[:, 0]
                target_intens = [target.get_intensity(x) for x in peak_freqs]
                if (lw / ps) % 2 != 0:
                    lw = lw + ps
                for peak in peak_freqs:
                    freq_min = peak - (lw / 2)
                    freq_max = peak + (lw / 2) + ps
                    row_min = int((freq_min - fmin) / ps)
                    row_max = int((freq_max - fmin) / ps)
                    copy[row_min:row_max, 1] = 0
                self.pp_pm.plot_lines(
                    [pp_invert[:, 0], peak_freqs[:]], [pp_invert[:, 1], target_intens],
                    invert=[line.invert.get(), marker.invert.get()],
                    color=[line.color.get(), marker.color.get()],
                    marker=[line.marker.get(), marker.marker.get()],
                    weight=[line.weight.get(), marker.weight.get()])
            else:
                self.pp_pm.plot_lines(
                    [[], []], [[], []], invert=[line.invert.get(), marker.invert.get()],
                    color=[line.color.get(), marker.color.get()],
                    marker=[line.marker.get(), marker.marker.get()],
                    weight=[line.weight.get(), marker.weight.get()])
        self.pp_pm.set_labels()
        self.pp_pm.zoom()
        self.pp_pm.canvas.draw()
        self.pp_pm.toolbar.update()

        self.unmod_pm.ax.cla()
        self.unmod_pm.plot_line(target_spec[:, 0], target_spec[:, 1], color='black', weight=0.75)
        self.unmod_pm.set_labels()
        self.unmod_pm.zoom()
        self.unmod_pm.canvas.draw()
        self.unmod_pm.toolbar.update()

        self.mod_pm.ax.cla()
        self.mod_pm.plot_line(copy[:, 0], copy[:, 1], color='black', weight=0.75)
        self.mod_pm.set_labels()
        self.mod_pm.zoom()
        self.mod_pm.canvas.draw()
        self.mod_pm.toolbar.update()

        self.page.save_temp_file('isolated_spectrum', copy)

    def save_isolated(self):
        """ Run when SAVE pressed. Prompt user for name and saves modified spectrum. """
        spec = self.page.load_temp_file('isolated_spectrum.npy')
        fname = page_funcs.save_file(
            ftype='.ft', initialdir=os.path.dirname(self.target_file.get()), defaultextension='.ft')
        fname = os.path.splitext(fname)[0]
        np.savetxt(fname + '.ft', spec, fmt=['%.4f', '%.8f'])

    def plot_unmod(self, spec_path):
        """
        Plot spec_path in the upper left plot. For selecting intensity threshold or dynamic range.
        """
        spectrum = Spectrum(spec_path).spectrum
        self.unmod_pm.ax.cla()
        self.unmod_pm.plot_line(spectrum[:, 0], spectrum[:, 1], color='black', weight=0.75)
        self.unmod_pm.set_labels()
        self.unmod_pm.zoom()
        self.unmod_pm.canvas.draw()
        self.unmod_pm.toolbar.update()

    def plot_pp(self, path):
        """
        Plot spectrum or simulation in upper right plot. For selecting intensity threshold or
        dynamic range.
        """
        ext = os.path.splitext(path)[1]
        if ext in ['.ft', '.prn', '.txt']:
            spectrum = Spectrum(path).spectrum
        elif ext in ['.cat']:
            spectrum = Cat(path).simulate()
        self.pp_pm.ax.cla()
        self.pp_pm.plot_line(spectrum[:, 0], spectrum[:, 1], color='black', weight=0.75)
        self.pp_pm.set_labels()
        self.pp_pm.zoom()
        self.pp_pm.canvas.draw()
        self.pp_pm.toolbar.update()
