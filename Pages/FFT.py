"""
Author: Channing West 
Changelog: 12/5/2019

"""

import tkinter as tk
from tkinter import messagebox
import Spectrum
from Pages.PageFormat import PageFormat
import os
import numpy as np
import tkinter.ttk as ttk
from TkAgg_Plotting import PlotManager, SpecPlot
import Pages.PageFormat as page_funcs
import testing


class FFT(ttk.Frame):
    """
    Generate GUI. Perform fast Fourier transforms on broadband molecular rotational spectra.

    Steps:
        BUTTONS
            PLOT NAVIGATION BAR
                See TkAgg_Plotting.PlotManager()
            SAVE, LOAD, DEFAULTS, BACK TO NAVIGATOR, EXIT APPLICATION
                See PageFormat.py
        1.  Upload Time Domain Files
            -   Select one or more *.txt files from file browser.
            -   The number of files chosen and total number of FIDs within those files are displayed
                if files follow naming convention (see Broadband_Controller.Auto_Controller.py)
            -   File names must follow naming convention to perform weighted average correctly.
            Buttons:
                BROWSE
                    Browse files with *.ft extension.
        2.  Fast Fourier Transform Parameters
            -   Either manually enter values for each parameter or use one of the buttons from 
                section 3.
        3.  Quick Fill Options
                Buttons:
                    2000 MHz | 8000 MHz | 25 GSa/s | 1FF | 9.5KB | 80 \u03BCs
                    2000 MHz | 8000 MHz | 25 GSa/s | 0.5FF | 9.5KB | 80 \u03BCs
                    2000 MHz | 8000 MHz | 25 GSa/s | 0.5FF | 4KB | 80 \u03BCs
                    6000 MHz | 18000 MHz | 50 GSa/s | 1FF | 9.5KB | 80 \u03BCs
                    6000 MHz | 18000 MHz | 50 GSa/s | 0.5FF | 9.5KB | 80 \u03BCs
                    6000 MHz | 18000 MHz | 50 GSa/s | 0.5FF | 4KB | 80 \u03BCs
            -   Press a button to import these parameters into section 2.
        4.  FFT Buttons
            -   If multiple files are selected, user asked whether to perform a weighted time-domain
                average of the files or process each file individually. If weighted average is
                chosen, *.txt file of the weighted average is generated, and user is given the
                option to name the file before it is saved.
            -   FID, filtered FID, and FFT are plotted after FFT completes, unless multiple files
                are processed individually.
            Buttons:
                MAGNITUDE FFT
                    Run fft(full_ft=False). Sum of squares of real and imaginary parts of FFT.
                    Result is 2 column array.
                FULL FFT
                    Runs fft(full_ft=True). Real and imaginary spectrum. Result is 3 column array.
    """
    default = {'files': 'None',
               'num_files': 'Number of files:  0',
               'num_avg': 'Total averages:  0'}

    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.controller = controller
        self.page_title = "Broadband MRR Toolbox - Fast Fourier Transform"

        self.freq_start = tk.IntVar()
        self.freq_stop = tk.IntVar()
        self.sample_rate = tk.IntVar()
        self.frac = tk.DoubleVar()
        self.KB = tk.DoubleVar()
        self.ZP = tk.IntVar()
        self.files = tk.StringVar()
        self.files.set(FFT.default['files'])
        self.num_files = tk.StringVar()
        self.num_files.set(FFT.default['num_files'])
        self.num_avg = tk.StringVar()
        self.num_avg.set(FFT.default['num_avg'])

        self.plot_frame = ttk.Frame(self.frame)
        other_frame = ttk.Frame(self.frame)

        h8bB = 'h8b.TButton'
        v = 'vertical'
        h = 'horizontal'
        r = tk.RIGHT
        c = tk.CENTER
        h8bL_r = {'style': 'h8b.TLabel', 'justify': tk.RIGHT}
        x2y2e = {'padx': 2, 'pady': 2, 'sticky': 'e'}
        x2y2ew = {'padx': 2, 'pady': 2, 'sticky': 'ew'}
        x2y2w = {'padx': 2, 'pady': 2, 'sticky': 'w'}
        rspan3x20ns = {'rowspan': 3, 'padx': 20, 'sticky': 'ns'}
        cspan2x10y5e = {'columnspan': 2, 'padx': 10, 'pady': 5, 'sticky': 'e'}
        cspan8y5ew = {'columnspan': 8, 'pady': 5, 'sticky': 'ew'}
        rspan2x20ns = {'rowspan': 2, 'padx': 20, 'sticky': 'ns'}
        # ==========================================================================================
        page_title = ttk.Label(
            other_frame, text='Fast Fourier Transform Parameters:', justify=c, style='h14b.TLabel')
        self.num_files_L = ttk.Label(other_frame, textvariable=self.num_files, justify=r)
        self.num_avg_L = ttk.Label(other_frame, textvariable=self.num_avg, justify=r)
        warning_L = ttk.Label(
            other_frame,
            text='**\nCo-Add File Name Structure: \n1. Use underscore as delimiter.\n'
                 '2. Give # of avgs. in base 1000 followed by "k" (ex. 100k).\n**',
            style='warning.TLabel')
        # ==========================================================================================
        start_L = ttk.Label(other_frame, text='Start Frequency\n(MHz)', **h8bL_r)
        stop_L = ttk.Label(other_frame, text='Stop Frequency\n(MHz)', **h8bL_r)
        samp_rate_L = ttk.Label(other_frame, text='Sample Rate\n(GSa/s)', **h8bL_r)
        ff_L = ttk.Label(other_frame, text='Fraction\nof FID', **h8bL_r)
        kb_L = ttk.Label(other_frame, text='Kaiser Bessel\nParameter', **h8bL_r)
        trl_L = ttk.Label(other_frame, text='Zero-Pad Length\n(\u03BCs)', **h8bL_r)
        start_E = ttk.Entry(other_frame, textvariable=self.freq_start, justify=c)
        stop_E = ttk.Entry(other_frame, textvariable=self.freq_stop, justify=c)
        samp_rate_E = ttk.Entry(other_frame, textvariable=self.sample_rate, justify=c)
        ff_E = ttk.Entry(other_frame, textvariable=self.frac, justify=c)
        kb_E = ttk.Entry(other_frame, textvariable=self.KB, justify=c)
        trl_E = ttk.Entry(other_frame, textvariable=self.ZP, justify=c)
        # ==========================================================================================
        quick_fill_L = ttk.Label(
            other_frame, text='Quick Fill Options:', justify=r, font='Helvetica 14 bold')
        option_1 = ttk.Button(
            other_frame,
            text="        2000 MHz | 8000 MHz | 25 GSa/s | 1FF | 9.5KB | 80 \u03BCs        ",
            style=h8bB, command=lambda: self.quick_fill_entry(2000, 8000, 25, 1, 9.5, 80))
        option_2 = ttk.Button(
            other_frame,
            text="        2000 MHz | 8000 MHz | 25 GSa/s | 0.5FF | 9.5KB | 80 \u03BCs        ",
            style=h8bB, command=lambda: self.quick_fill_entry(2000, 8000, 25, 0.5, 9.5, 80))
        option_3 = ttk.Button(
            other_frame,
            text="        2000 MHz | 8000 MHz | 25 GSa/s | 0.5FF | 4KB | 80 \u03BCs        ",
            style=h8bB, command=lambda: self.quick_fill_entry(2000, 8000, 25, 0.5, 4, 80))
        option_4 = ttk.Button(
            other_frame,
            text="       6000 MHz | 18000 MHz | 50 GSa/s | 1FF | 9.5KB | 80 \u03BCs       ",
            style=h8bB, command=lambda: self.quick_fill_entry(6000, 18000, 50, 1, 9.5, 80))
        option_5 = ttk.Button(
            other_frame,
            text="       6000 MHz | 18000 MHz | 50 GSa/s | 0.5FF | 9.5KB | 80 \u03BCs       ",
            style=h8bB, command=lambda: self.quick_fill_entry(6000, 18000, 50, 0.5, 9.5, 80))
        option_6 = ttk.Button(
            other_frame,
            text="       6000 MHz | 18000 MHz | 50 GSa/s | 0.5FF | 4KB | 80 \u03BCs       ",
            style=h8bB, command=lambda: self.quick_fill_entry(6000, 18000, 50, 0.5, 4, 80))
        # ==========================================================================================
        upload_files_L = ttk.Label(
            other_frame, text='Upload Time Domain Files:', justify=r, style='h8b.TLabel')
        files_L = ttk.Label(other_frame, text='File(s):', **h8bL_r)
        self.files_E = ttk.Entry(other_frame, textvariable=self.files, justify=c)
        browse_button = ttk.Button(
            other_frame, text='Browse', command=self.upload_files, style=h8bB)
        # ==========================================================================================
        magnitude = ttk.Button(
            other_frame, text="Magnitude FFT", style='h10b.TButton',
            command=lambda: self.execute_fft(full_ft=False))
        full = ttk.Button(
            other_frame, text="Full FFT", style='h10b.TButton',
            command=lambda: self.execute_fft(full_ft=True))
        ttk.Separator(other_frame, orient=h).grid(row=0, column=0, **cspan8y5ew)
        ttk.Separator(other_frame, orient=v).grid(row=1, column=0, **rspan2x20ns)
        ttk.Separator(other_frame, orient=v).grid(row=1, column=7, **rspan2x20ns)
        upload_files_L.grid(row=1, column=1, pady=15, sticky='w')
        self.num_files_L.grid(row=1, column=3, **x2y2w)
        self.num_avg_L.grid(row=1, column=4, **x2y2w)
        warning_L.grid(row=1, column=5, columnspan=2, **x2y2w)
        files_L.grid(row=2, column=1, **x2y2e)
        self.files_E.grid(row=2, column=2, columnspan=4, **x2y2ew)
        browse_button.grid(row=2, column=6, **x2y2w)
        ttk.Separator(other_frame, orient=h).grid(row=3, column=0, **cspan8y5ew)
        ttk.Separator(other_frame, orient=v).grid(row=4, column=0, **rspan3x20ns)
        ttk.Separator(other_frame, orient=v).grid(row=4, column=7, **rspan3x20ns)
        page_title.grid(row=4, column=1, columnspan=2, pady=15, sticky='w')
        start_L.grid(row=5, column=1, **x2y2e)
        stop_L.grid(row=5, column=3, **x2y2e)
        samp_rate_L.grid(row=5, column=5, **x2y2e)
        ff_L.grid(row=6, column=1, **x2y2e)
        kb_L.grid(row=6, column=3, **x2y2e)
        trl_L.grid(row=6, column=5, **x2y2e)
        start_E.grid(row=5, column=2, **x2y2ew)
        stop_E.grid(row=5, column=4, **x2y2ew)
        samp_rate_E.grid(row=5, column=6, **x2y2ew)
        ff_E.grid(row=6, column=2, **x2y2ew)
        kb_E.grid(row=6, column=4, **x2y2ew)
        trl_E.grid(row=6, column=6, **x2y2ew)
        ttk.Separator(other_frame, orient=h).grid(row=7, column=0, **cspan8y5ew)
        ttk.Separator(other_frame, orient=v).grid(row=8, column=0, **rspan3x20ns)
        ttk.Separator(other_frame, orient=v).grid(row=8, column=7, **rspan3x20ns)
        quick_fill_L.grid(row=8, column=1, columnspan=1, padx=0, pady=15, sticky='w')
        option_1.grid(row=9, column=1, **cspan2x10y5e)
        option_2.grid(row=9, column=3, **cspan2x10y5e)
        option_3.grid(row=9, column=5, **cspan2x10y5e)
        option_4.grid(row=10, column=1, **cspan2x10y5e)
        option_5.grid(row=10, column=3, **cspan2x10y5e)
        option_6.grid(row=10, column=5, **cspan2x10y5e)
        ttk.Separator(other_frame, orient=h).grid(row=12, column=0, **cspan8y5ew)
        ttk.Separator(other_frame, orient=v).grid(row=13, column=0, padx=20, sticky='ns')
        ttk.Separator(other_frame, orient=v).grid(row=13, column=7, padx=20, sticky='ns')
        magnitude.grid(row=13, column=2, columnspan=2, padx=2, pady=20, sticky='ew')
        full.grid(row=13, column=4, columnspan=2, padx=2, pady=20, sticky='ew')
        ttk.Separator(other_frame, orient=h).grid(row=14, column=0, **cspan8y5ew)
        # ==========================================================================================
        self.time_pm = PlotManager(
            self.plot_frame, figsize=(10, 4.5), dpi=80, subplotshape=111, zoom_mode=0,
            plot_title='Free Induction Decay', xlabel='Time / Microseconds', ylabel='Voltage / mV',
            x_min='Auto', x_max='Auto', y_min='Auto', y_max='Auto', legend_show=False, left=0.08,
            right=0.98, top=0.92, bottom=0.1, row=0, column=0, toolbar=False)
        self.time_plot = SpecPlot(self.time_pm.ax, show=1, color='black', weight=0.3, marker=None)

        self.window_pm = PlotManager(
            self.plot_frame, figsize=(10, 4.5), dpi=80, subplotshape=111, zoom_mode=0,
            plot_title='Kaiser Filtered FID', xlabel='Time / Microseconds', ylabel='Voltage / Arb.',
            x_min='Auto', x_max='Auto', y_min='Auto', y_max='Auto', legend_show=False, left=0.08,
            right=0.98, top=0.92, bottom=0.1, row=0, column=1, toolbar=False)
        self.window_plot = SpecPlot(self.window_pm.ax, show=1, color='black', weight=0.3)

        self.fft_pm = PlotManager(
            self.plot_frame, figsize=(16, 6), dpi=100, subplotshape=111, zoom_mode=0,
            plot_title='Fast Fourier Transform', xlabel='Frequency / MHz', ylabel='Intensity / mV',
            x_min='Auto', x_max='Auto', y_min='Auto', y_max='Auto', legend_show=True, left=0.05,
            right=0.99, top=0.96, bottom=0.08, row=1, column=0, columnspan=2, toolbar=True,
            toolrow=2, toolcol=0, toolsticky='w')
        self.fft_plot = SpecPlot(self.fft_pm.ax, show=1, color='black', weight=0.75)
        self.fft_plot_2 = SpecPlot(self.fft_pm.ax, show=1, color='black', weight=0.75)

        other_frame.grid(row=1, column=0, pady=20)
        self.plot_frame.grid(row=0, column=0)

    def quick_fill_entry(self, start, stop, samp_rate, ff, kb, trl):
        """
        Called when quick-fill buttons are pressed. Fill Entry boxes with the settings shown.

        Parameters:
            start (float):
                Starting frequency.
                Units: MHz
            stop (float):
                Stopping frequency.
                Units: MHz
            samp_rate (float):
                Sampling rate.
                Units: GSa./s
            ff (float):
                Fraction of FID used for FFT.
            kb (float):
                Kaiser-Bessel parameter.
            trl (float):
                Total record length.
                Units: microseconds
        """
        self.freq_start.set(start)
        self.freq_stop.set(stop)
        self.sample_rate.set(samp_rate)
        self.frac.set(ff)
        self.KB.set(kb)
        self.ZP.set(trl)

    def upload_files(self):
        """
        Called when uploading time series data file(s).

        A list of file names is generated and displayed in the entry box. Display the number of
        files selected and the total number of FID averages within those files.
        """
        page_funcs.write_paths(self.files, eb_var=self.files_E, ftype='txt')
        files_list = page_funcs.list_paths(self.files)
        try:
            tot_avg, weights = weights_and_total_avg(files_list)
        except UnboundLocalError:
            tot_avg = 'Error'
        self.num_files.set('Number of files:  ' + str(len(files_list)))
        self.num_avg.set('Total averages:  ' + str(tot_avg))

    def execute_fft(self, full_ft=False):
        """
        Called when Magnitude FFT or Full FFT buttons are pressed. Executes FFT.

        Parameters:
            full_ft (bool):
                Set whether magnitude FFT or real + imaginary FFT is saved.
                Default: False
        """
        sr = self.sample_rate.get() * 1E9
        files_list = page_funcs.list_paths(self.files)
        if len(files_list) > 1:
            coadd_files = messagebox.askyesno(
                "Co-Add Option", "Co-add files? Otherwise, files are processed individually.")
            if coadd_files:
                coadd_arr, coadd_fname = coadd_time_domain(files_list, sr, save=True)
                self.fft(coadd_fname, full_ft=full_ft, plot=True)
            else:
                for file in files_list:
                    self.fft(file, full_ft=full_ft, plot=False)
        else:
            self.fft(files_list[0], full_ft=full_ft, plot=True)

    @testing.collect_garbage
    def fft(self, file, full_ft=False, plot=True):
        """
        Get settings from GUI, perform, save, and plot FFT.

        Parameters:
            file (str):
                File path.
            full_ft (bool):
                Set whether magnitude FFT or real + imaginary fft is saved.
                Default: False
            plot (bool):
                Set whether data from FFT is plotted on GUI.
                Default: True
        """
        fstart = self.freq_start.get()
        fstop = self.freq_stop.get()
        sr = self.sample_rate.get() * 1E9
        ff = self.frac.get()
        kb = self.KB.get()
        zp = self.ZP.get()

        fid = Spectrum.FID(file, srate=sr)
        fid.gate_kaiser_zeropad(frac=ff, kb=kb, total_time=zp)
        fid.time_column_fid()
        fft = fid.fft(fstart=fstart, fstop=fstop, full_ft=full_ft)
        self.save_fft(str(os.path.splitext(file)[0]), fft)
        if plot:
            self.plot_fft(fid.fid, fid.ff_kb_abs_fid, fft, full_ft=full_ft)

    def plot_fft(self, fid_time, abs_norm_kaiser, fft, full_ft=False):
        """
        Handles clearing and drawing 3 GUI plots: time series, filtered time series, and fft.

        Parameters:
            fid_time (array):
                2 column array.
                Col[0] -> time
                Col[1] -> magnitude or real.
            abs_norm_kaiser (array):
                Col[0] -> Normalized absolute value of the Kaiser filtered intensity.
            fft (array):
                2 or 3 column array.
                Col[0] -> frequency.
                Col[1] -> magnitude or real.
                Col[2] -> Imaginary.
            full_ft (bool):
                False -> magnitude fft.
                True -> real + imaginary fft.
        """
        self.time_pm.ax.cla()
        self.time_pm.plot_line(fid_time[:, 0], fid_time[:, 1], color='red', weight=0.3)
        self.time_pm.set_labels()
        self.time_pm.zoom()
        self.time_pm.canvas.draw()

        self.window_pm.ax.cla()
        self.window_pm.plot_line(
            fid_time[:len(abs_norm_kaiser), 0], abs_norm_kaiser, color='red', weight=0.3)
        self.window_pm.set_labels()
        self.window_pm.zoom()
        self.window_pm.canvas.draw()

        self.fft_pm.ax.cla()
        p = self.controller.picker
        if full_ft:
            self.fft_pm.plot_lines(
                [fft[:, 0], fft[:, 0]], [fft[:, 1], fft[:, 2]], color=['black', 'orange'],
                weight=[0.3, 0.3], label=['Real', 'Imaginary'], picker=[p, p])
        else:
            self.fft_pm.plot_line(
                fft[:, 0], fft[:, 1], color='black', weight=0.75, label='Magnitude',
                picker=self.controller.picker)
        self.fft_pm.set_labels()
        self.fft_pm.zoom()
        self.fft_pm.canvas.draw()
        self.fft_pm.toolbar.update()

    def save_fft(self, fname, fft):
        """
        Ask user to save fft. If yes, additional parameters are appended fname. Extension is *.ft.

        Additional parameters added to file name:
            1.  Fraction of FID in FFT multiplied by 10 (To remove decimal).
                If half the FID is used, '_FF5' is appended to the end of the file name.
            2.  Kaiser-Bessel parameter multiplied by 10 (To remove decimal):
                If 9.5 is used, '_KB95' is appended to the end of the file name.
            3.  Total Record Length: FID time and zero-padding in units of microseconds.
                If the total record length is 80 microseconds, '_TRL80' is appended to the
                end of the file name.
        Parameters:
            fname (str):
                Typically the file name of the FID.
            fft (array):
                2 or 3 column array.
                Col[0] -> frequency.
                Col[1] -> magnitude or real.
                Col[2] -> imaginary.
        """
        ff = self.frac.get()
        kb = self.KB.get()
        zp = self.ZP.get()
        fname = os.path.splitext(fname)[0]
        params = '_FF' + str(round(ff * 10)) + '_KB' + str(round(kb * 10)) + '_TRL' + str(
            round(zp))
        if fft.shape[1] == 3:
            fname = fname + params + '_full.ft'
            np.savetxt(fname, fft, fmt=['%.4f', '%.8f', '%.8f'])
        elif fft.shape[1] == 2:
            fname = fname + params + '.ft'
            np.savetxt(fname, fft, fmt=['%.4f', '%.8f'])


def weights_and_total_avg(files_list):
    """
    Return number of FID averages for each file in a list of files and the sum total of averages.

    File names must use underscore as delimeter. File name must also provide the number
    of averages in base 1000 and end number with a 'k' (Ex. 100k for 100,000 FIDs).

    Parameters:
        files_list (list of strings):
            List of file paths.
    Returns:
        total_avgs (int):
            Number of total FIDs for all files in files_list.
        weights (list of ints):
            List of number of FIDs for each file in files_list.
    """
    total_avgs = 0
    weights = []
    for file in files_list:
        split_name = os.path.basename(file).split('_')
        endswithk = [x for x in split_name if x.endswith('k')]
        for x in endswithk:
            try:
                avgs = int(x.split('k')[0])
                weights.append(avgs)
                total_avgs += avgs
            except ValueError:
                continue
    return total_avgs, weights


def coadd_time_domain(files_list, srate, save=True):
    """
    Return weighted average of time series data from files in files_list.

    File names must use underscore as delimeter. File name must also provide
    the number of averages in base 1000 and end number with a 'k' (Ex. 100k for 100,000 FIDs).

    Parameters:
        files_list (list of strings):
            List of file paths.
        srate (int):
            Sampling rate of digitizer. Must be the same for all files in files_list.
        save (bool):
            Save the weighted average
    Returns:
        coadd_arr (array):
            Weighted average.
        file (str):
            File name of saved file
    """
    split_name = os.path.basename(files_list[0]).split('_')
    coadd_arr = np.zeros((len(Spectrum.FID(files_list[0], srate=srate).fid), 1))
    total_avgs, weightings = weights_and_total_avg(files_list)
    for x in range(len(files_list)):
        weight = weightings[x] / total_avgs
        weighted_fid = Spectrum.FID(files_list[x], srate=srate).fid * weight
        coadd_arr += weighted_fid
    coadd_fname = ['CoAdd']
    for x in split_name[1:-7]:
        if not x.endswith('k'):
            coadd_fname.append(x)
        else:
            coadd_fname.append(str(total_avgs) + 'k')
    for x in split_name[-7:]:
        if not x.endswith('k'):
            coadd_fname.append(x)
        else:
            coadd_fname.append(str(total_avgs) + 'k')
    coadd_fname = '_'.join(coadd_fname)
    if save:
        filename = page_funcs.save_file(
            initialfile=coadd_fname, ftype='.txt', defaultextension='.txt')
        if filename != '':
            np.savetxt(filename, coadd_arr, fmt='%.5E')
    else:
        filename = coadd_fname
    return coadd_arr, filename


def quick_fft_files(files_list, fstart, fstop, sr, ff, kb, zp, full_ft=False):
    """
    Perform FFTs for each file in files_list, individually, using the given settings.

    File names must use underscore as delimeter. File name must also provide the
    number of averages in base 1000 and end number with a 'k' (Ex. 100k for 100,000 FIDs).

    Parameters:
        files_list (list of strings):
            List of file paths.
        fstart (float):
            FFT starting frequency.
            Units: MHz
        fstop (float):
            FFT stopping frequency.
            Units: MHz
        sr (int):
            Sampling rate
            Units: Samples/second
        ff (float):
            Fraction of FID
        kb (float):
            Kaiser-Bessel parameter
        zp (int):
            zero padding
            Units: microseconds
        full_ft (bool):
            Set whether magnitude FFT or real + imaginary FFT is saved.
            Default: False
    """
    for file in files_list:
        fname = os.path.splitext(file)[0]
        fid = Spectrum.FID(file, srate=sr)
        fft = fid.quick_fft(
            frac=ff, kb=kb, total_time=zp, fstart=fstart, fstop=fstop, full_ft=full_ft)
        params = '_FF' + str(round(ff * 10)) + '_KB' + str(round(kb * 10)) + '_TRL' + str(round(zp))
        if not full_ft:
            fname = fname + params + '.ft'
            np.savetxt(fname, fft, fmt=['%.4f', '%.8f'])
        else:
            fname = fname + params + '_full.ft'
            np.savetxt(fname, fft, fmt=['%.4f', '%.8f', '%.8f'])

    #
    # coadd_fname = os.path.splitext(file)[0]
    # if not coadd_fname:
    #     return

# file = ['C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\Rotational Spectroscopy Data Analysis 4_24_2020\\3_1_2021_Testing\FFT\\16_38_37_Varenicline_2to8_10k_175C_4us_15psig_.txt',
#         'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\Rotational Spectroscopy Data Analysis 4_24_2020\\3_1_2021_Testing\FFT\\16_44_59_Varenicline_2to8_10k_175C_4us_15psig_.txt']
# coadd_time_domain(file, 1)
