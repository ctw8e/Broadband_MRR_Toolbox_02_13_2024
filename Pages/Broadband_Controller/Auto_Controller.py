"""
Author: Channing West
Changelog: 11/14/2020

"""

import time
import math
import os
import glob
import scipy
import numpy as np
import threading
import Pages.PageFormat as pagefmt
from threading import Thread, Event
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import askokcancel, askyesnocancel, showerror
from tkinter import simpledialog
import Pages.PageFormat as page_funcs
from Instrument_Drivers.Oscilloscope_Driver import OscilloscopeDriver
import minimalmodbus
import Spectrum

label_fmt = {'justify': 'right', 'style': 'h10b.TLabel', 'width': 17, 'anchor': 'e'}


class AutoController:
    """
    Generate GUI to control automated spectral collection using the 2-8 GHz and 6-18 GHz
    broadband spectrometer in the Pate lab.

    Parameters:
        master (ttk.Frame)
        scope_module (Pages.Broadband_Controller.Scope_Controller())
        awg_module (Pages.Broadband_Controller.AWG_Controller())
        temp_module (Pages.Broadband_Controller.Temp_Controller())
    Attributes:
        self.scope_module:
            Instance of Pages.Broadband_Controller.Scope_Controller.ScopeController class.
        self.awg_module:
            Instance of Pages.Broadband_Controller.AWG_Controller.AWGController class.
        self.temp_module:
            Instance of Pages.Broadband_Controller.Temp_Controller.TempController class.
        self.runmode (tk.StringVar):
            single | continuous | temperature sequence | chirp sequence
            Default: continuous
        self.pickett_dir (tk.StringVar):
            Destination directory of saved files.
            Default: 'C:/Users/Pate Lab/OneDrive/Oscilloscope Data-Controller'
        self.fname (tk.StringVar):
            Sample name. Chemical compound.
            Default: Blank
        self.save_every (tk.IntVar):
            Number of FIDs collected before saving waveform.
            Default: 1000
        self.instsetup (tk.StringVar):
            The spectral region the spectrometer is set up for.
            Options: 2-8 or 6-18
            Default: 2-8
        self.chirpdur (tk.IntVar):
            Chirp duration.
            Units: microseconds.
            Default: 4
        self.temp (tk.StringVar):
            Nozzle temperature.
            Units: Celsius.
            Default: 20
        self.temp_tol_bool(tk.IntVar):
            If True, wait for nozzle temperature to enter tolerance region at each step
            before starting data acquisition.
            Default: 0
        self.temp_tol (tk.StringVar):
            Temperature tolerance for temperature ramp measurement.
            See Instrument_Drivers.Temp_Cont_Driver.pv_sv_tolerance_check(tolerance, *args)
            See self.temp_tol_bool
            Units: Celsius.
            Default: None
        self.pressure (tk.IntVar):
            Backing pressure.
            Units: psig.
            Default: 15
        self.tempseq (tk.StringVar):
            Sequence of temperatures for ramp.
            Format -> First, Last, Increment
            Units: Celsius
            Default: None
        self.chirpseq (tk.StringVar):
            Sequence of chirp durations. Used to find optimal chirp duration.
            Options:
                 2-8 GHz: 1, 2, 4 microsecond
                 2-8 GHz: 4, 2, 1 microsecond
                 6-18 GHz: 1, 2, 4 microsecond
                 6-18 GHz: 4, 2, 1 microsecond
            Default: None
        self.seq_previous (tk.StringVar):
            Variable holds the last completed measurement from a sequence measurement.
            Default: None
        self.seq_current (tk.StringVar):
            Variable holds the sequence measurement currently running.
            Default: None
        self.seq_next (tk.StringVar):
            Variable holds the sequence measurement next in the queue.
            Default: None
        self.fftbool (tk.IntVar()):
            Boolean to turn automatic FFT on/off.
            Default: 1
        self.sr (tk.IntVar()):
            Sampling rate.
            Units: GSa./sec.
            Default: 25
        self.fftlower (tk.DoubleVar()):
            Lower bound of FFT.
            Units: MHz.
            Default: 2000
        self.fftupper (tk.DoubleVar()):
            Upper bound of FFT.
            Units: MHz.
            Default: 8000
        self.ff (tk.DoubleVar()):
            Fraction of waveform to FFT.
            Between 0 and 1.
            Default: 1
        self.kb (tk.DoubleVar()):
            Kaiser-Bessel window parameter.
            Default: 9.5
        self.trl (tk.DoubleVar()):
            Total record length. FID + zero padding.
            Units: microseconds
            Default: 80
        self.event (threading.Event):
            self.event.is_set() to abort thread.
    Methods:
        check_instsetup()
            Confirm oscilloscope is set up for the requested spectral region.
        check_math2mem()
            Confirm (self.scope_module.math2_mem/8) is not less than self.save_every.
        check_fft_bounds()
            Confirm auto FFT bounds match spectral region.
        check_temp_sv()
            Confirm self.temp matches temperature controller set point.
        check_tempseq()
            Confirm properly formatted temperature sequence is provided.
        check_chirp()
            Confirm active waveform matches self.instsetup and self.chirpdur.
        check_chirpseq()
            Confirm correct waveform is active before starting chirp sequence.
        auto_prerun_check()
            Full instrument check using linked variables.
        auto_run()
            Communicate with scope, awg, and temp controllers to monitor measurements and save data
            at set intervals.
        auto_stop()
            Pause or abort the archive process.
        fid_averaging()
            Return trigger_save when self.scope_module.numavgs reached or when self.event.is_set().
        single()
            Save FID waveform after defined number of FIDs signal averaged. Stop data acquisition.
        continuous()
            Save FID waveform after defined number of FIDs signal averaged, clear, restart, repeat
            until self.event.set().
        temperature_sequence(sequence, start_tolerance, step_tolerance, reset, tolerance)
            Collect a series of spectra at different temperatures.
        tempseq_continue()
            When the current measurement finishes, run an additional measurement at the same
            temperature before continuing to next temperature in the queue by updating
            self.seq_next.
        tempseq_skip()
            Skip the next temperature in the queue by updating self.seq_next.
        update_temp_queue(sequence)
            Use to update sequence queue (previous, current, next) with correct temperatures after
            each iteration.
        wait_for_temp_tolerance(degrees, sleep_time)
            Monitor nozzle temperature until temperature enters tolerance region.
        chirp_sequence(setup)
            Run a series of measurements with different chirp durations.
        auto_save_fid(temp)
            Save waveform in self.pickett_dir folder. File is named using information from GUI.
        auto_save_fft()
            Calculate FFT of most recent waveform saved in self.pickett_dir.
    BUTTONS:
        BROWSE
            Open file explorer to select a directory. Spectra saved in directory.
        <= REPEAT
            Used with temperature sequence and chirp sequence measurements. When the current
            measurement finishes, run an additional measurement at the same temperature or chirp
            duration before continuing to next measurement settings.
        <= SKIP
            Used with temperature sequence and chirp sequence measurements.
            Skip the upcoming measurement and proceed to the item after that one.
        RUN
            auto_run()
        PAUSE
            self.auto_stop(clear_scope=False, awg_stop=False, lower_temp=False)
        ABORT
            self.auto_stop(clear_scope=True, awg_stop=True, lower_temp=True)
    """

    default = {'run_mode': 'continuous',
               'pickett_dir': 'C:/Users/Pate Lab/OneDrive/Oscilloscope Data-Controller',
               'sample': 'Blank',
               'save_every': 1000,
               'inst_setup': '2-8',
               'chirp_duration': 4,
               'temperature': '20',
               'temperature_tolerance': 'None',
               'temperature_tolerance_step': 0,
               'backing_pressure': 15,
               'previous': 'None',
               'current': 'None',
               'next': 'None',
               'perform_fft': 1,
               'sampling_rate': 25,
               'fft_start': 2000,
               'fft_stop': 8000,
               'ff': 1,
               'kb': 9.5,
               'trl': 80,
               'temp_control': 3,
               'temp_ramp_vals': 'None',
               'awg_chirp_list': 'None'}

    def __init__(self, master, scope_module, awg_module, temp_module):
        self.scope_module = scope_module
        self.awg_module = awg_module
        self.temp_module = temp_module

        self.runmode = tk.StringVar()
        self.dir = tk.StringVar()
        self.fname = tk.StringVar()
        self.save_every = tk.IntVar()
        self.instsetup = tk.StringVar()
        self.chirpdur = tk.IntVar()
        self.temp = tk.StringVar()
        self.temp_tol = tk.StringVar()
        self.temp_tol_bool = tk.IntVar()
        self.pressure = tk.IntVar()
        self.tempseq = tk.StringVar()
        self.chirpseq = tk.StringVar()
        self.seq_previous = tk.StringVar()
        self.seq_current = tk.StringVar()
        self.seq_next = tk.StringVar()
        self.runmode.set(AutoController.default['run_mode'])
        self.dir.set(AutoController.default['pickett_dir'])
        self.fname.set(AutoController.default['sample'])
        self.save_every.set(AutoController.default['save_every'])
        self.instsetup.set(AutoController.default['inst_setup'])
        self.chirpdur.set(AutoController.default['chirp_duration'])
        self.temp.set(AutoController.default['temperature'])
        self.temp_tol.set(AutoController.default['temperature_tolerance'])
        self.temp_tol_bool.set(AutoController.default['temperature_tolerance_step'])
        self.pressure.set(AutoController.default['backing_pressure'])
        self.tempseq.set(AutoController.default['temp_ramp_vals'])
        self.chirpseq.set(AutoController.default['awg_chirp_list'])
        self.seq_previous.set(AutoController.default['previous'])
        self.seq_current.set(AutoController.default['current'])
        self.seq_next.set(AutoController.default['next'])

        self.fftbool = tk.IntVar()
        self.sr = tk.IntVar()
        self.fftlower = tk.DoubleVar()
        self.fftupper = tk.DoubleVar()
        self.ff = tk.DoubleVar()
        self.kb = tk.DoubleVar()
        self.trl = tk.DoubleVar()
        self.fftbool.set(AutoController.default['perform_fft'])
        self.sr.set(AutoController.default['sampling_rate'])
        self.fftlower.set(AutoController.default['fft_start'])
        self.fftupper.set(AutoController.default['fft_stop'])
        self.ff.set(AutoController.default['ff'])
        self.kb.set(AutoController.default['kb'])
        self.trl.set(AutoController.default['trl'])

        self.event = Event()

        h8RB = 'h8.TRadiobutton'
        h8bB = 'h8b.TButton'
        h10bB = 'h10b.TButton'
        x5y3w = {'padx': 5, 'pady': 3, 'sticky': 'w'}
        x5y3 = {'padx': 5, 'pady': 3}
        x4y10 = {'padx': 4, 'pady': 10}
        x5y3e = {'padx': 5, 'pady': 3, 'sticky': 'e'}
        x4y3w = {'padx': 4, 'pady': 3, 'sticky': 'w'}
        x4y3 = {'padx': 4, 'pady': 3}
        x4y3e = {'padx': 4, 'pady': 3, 'sticky': 'e'}
        h10bL_r = {'style': 'h10b.TLabel', 'justify': 'right'}
        width25_c = {'justify': 'center', 'width': 25}
        h10L_l = {'style': 'h10.TLabel', 'justify': 'left'}
        h8bB_width10 = {'style': h8bB, 'width': 10}
        h10bB_width10 = {'style': h10bB, 'width': 10}

        frame = ttk.Frame(master)
        frame.grid(row=0, column=0, padx=20, pady=3, sticky='n')
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=28, column=0, columnspan=3, **x4y3)

        auto_L = ttk.Label(frame, text='Automatic Spectrum Collection', style='h14b.TLabel')
        auto_L.grid(row=1, column=0, columnspan=3, pady=3, sticky='w')

        continuous_rb = ttk.Radiobutton(
            frame, text='Continuous', style=h8RB, variable=self.runmode, value='continuous')
        single_rb = ttk.Radiobutton(
            frame, text='Single', style=h8RB, variable=self.runmode, value='single')
        temp_ramp_rb = ttk.Radiobutton(
            frame, text='Temperature Sequence', style=h8RB, variable=self.runmode,
            value='temperature sequence')
        chirp_dur_rb = ttk.Radiobutton(
            frame, text='Chirp Sequence', style=h8RB, variable=self.runmode, value='chirp sequence')
        continuous_rb.grid(row=2, column=1, **x5y3w)
        single_rb.grid(row=3, column=1, **x5y3w)
        temp_ramp_rb.grid(row=4, column=1, **x5y3w)
        chirp_dur_rb.grid(row=5, column=1, **x5y3w)

        mode_L = ttk.Label(frame, text='Run Mode', **h10bL_r)
        dir_L = ttk.Label(frame, text='Directory', **label_fmt)
        sample_L = ttk.Label(frame, text='Sample Name', **label_fmt)
        save_every_L = ttk.Label(frame, text='Save Every', **label_fmt)
        save_every_units = ttk.Label(frame, text='FIDs', **h10bL_r)
        inst_setup_L = ttk.Label(frame, text='Instrument Setup', **label_fmt)
        inst_setup_units = ttk.Label(frame, text='GHz', **h10bL_r)
        cd_L = ttk.Label(frame, text='Chirp Duration', **label_fmt)
        cd_units = ttk.Label(frame, text='\u03BCs', **h10bL_r)
        bp_L = ttk.Label(frame, text='Backing Pressure', **label_fmt)
        bp_units = ttk.Label(frame, text='psig', **h10bL_r)
        temp_L = ttk.Label(frame, text='Temperature', **label_fmt)
        temp_units = ttk.Label(frame, text='\u00B0C', **h10bL_r)
        mode_L.grid(row=2, column=0, **x5y3e)
        dir_L.grid(row=6, column=0, **x5y3e)
        sample_L.grid(row=7, column=0, **x5y3e)
        save_every_L.grid(row=8, column=0, **x5y3e)
        save_every_units.grid(row=8, column=2, **x5y3w)
        inst_setup_L.grid(row=9, column=0, **x5y3e)
        inst_setup_units.grid(row=9, column=2, **x5y3w)
        cd_L.grid(row=10, column=0, **x4y3e)
        bp_L.grid(row=11, column=0, **x4y3e)
        temp_L.grid(row=12, column=0, **x4y3e)
        cd_units.grid(row=10, column=2, **x4y3w)
        bp_units.grid(row=11, column=2, **x4y3w)
        temp_units.grid(row=12, column=2, **x4y3w)

        self.dir_E = ttk.Entry(frame, textvariable=self.dir, **width25_c)
        dir_B = ttk.Button(
            frame, text='Browse', style=h8bB, width=8,
            command=lambda: page_funcs.write_directory(self.dir_E))
        sample_CB = ttk.Combobox(frame, textvariable=self.fname, **width25_c)
        sample_CB['values'] = ('Blank', 'Solvent_Purge')
        save_every_CB = ttk.Combobox(frame, textvariable=self.save_every, **width25_c)
        save_every_CB['values'] = (1000, 5000, 10000, 20000, 40000, 100000, 200000)
        inst_setup_CB = ttk.Combobox(frame, textvariable=self.instsetup, **width25_c)
        inst_setup_CB['values'] = ('2-8', '6-18')
        cd_CB = ttk.Combobox(frame, textvariable=self.chirpdur, **width25_c)
        cd_CB['values'] = (1, 2, 4)
        bp_CB = ttk.Combobox(frame, textvariable=self.pressure, **width25_c)
        bp_CB['values'] = (5, 10, 15, 20, 25, 30)
        temp_CB = ttk.Combobox(frame, textvariable=self.temp, **width25_c)
        temp_CB['values'] = (
            'Temperature Sequence', '20', '30', '40', '50', '60', '70', '80', '90', '100', '110',
            '120', '130', '140', '150', '160', '170', '180', '190', '200')
        self.dir_E.grid(row=6, column=1, **x5y3w)
        dir_B.grid(row=6, column=2, **x5y3)
        sample_CB.grid(row=7, column=1, **x5y3)
        save_every_CB.grid(row=8, column=1, **x5y3)
        inst_setup_CB.grid(row=9, column=1, **x5y3)
        cd_CB.grid(row=10, column=1, **x4y3)
        bp_CB.grid(row=11, column=1, **x4y3)
        temp_CB.grid(row=12, column=1, **x4y3)

        sep8 = ttk.Separator(frame, orient='horizontal')
        sep8.grid(row=13, column=0, columnspan=3, padx=40, pady=10, sticky='ew')

        temp_seq_L = ttk.Label(frame, text='Temp. Sequence', **label_fmt)
        temp_seq_units = ttk.Label(frame, text='\u00B0C', **h10bL_r)
        toleracne_L = ttk.Label(
            frame, text='Temp. Tolerance\nCheck box to\napply at each step', **label_fmt)
        chirp_seq_L = ttk.Label(frame, text='Chirp Sequence', **label_fmt)
        previous_seq_L = ttk.Label(frame, text='Previous', **label_fmt)
        current_seq_L = ttk.Label(frame, text='Current', **label_fmt)
        next_seq_L = ttk.Label(frame, text='Next', **label_fmt)
        toleracne_L.grid(row=15, column=0, **x4y3w)
        temp_seq_L.grid(row=14, column=0, **x4y3)
        temp_seq_units.grid(row=14, column=2, columnspan=2, **x4y3w)
        chirp_seq_L.grid(row=16, column=0, **x4y3)
        previous_seq_L.grid(row=17, column=0, **x4y3)
        current_seq_L.grid(row=18, column=0, **x4y3)
        next_seq_L.grid(row=19, column=0, **x4y3)

        temp_seq_CB = ttk.Combobox(frame, textvariable=self.tempseq, **width25_c)
        temp_seq_CB['values'] = ('None', 'Format -> First, Last, Increment', '40, 150, 10')
        temp_tol_CB = ttk.Combobox(frame, textvariable=self.temp_tol, **width25_c)
        temp_tol_CB['values'] = ('None', '10', '5', '3', '1')
        temp_tol_check = ttk.Checkbutton(frame, variable=self.temp_tol_bool)
        chirp_seq_CB = ttk.Combobox(frame, textvariable=self.chirpseq, **width25_c)
        chirp_seq_CB['values'] = (
            'None', '2-8 GHz:     1, 2, 4 microsecond', '2-8 GHz:     4, 2, 1 microsecond',
            '6-18 GHz:   1, 2, 4 microsecond', '6-18 GHz:   4, 2, 1 microsecond')
        previous_E = ttk.Label(frame, textvariable=self.seq_previous, **h10L_l)
        current_E = ttk.Label(frame, textvariable=self.seq_current, **h10L_l)
        next_E = ttk.Label(frame, textvariable=self.seq_next, **h10L_l)
        continue_B = ttk.Button(
            frame, text='<= Repeat', **h8bB_width10, command=self.tempseq_continue)
        skip_B = ttk.Button(frame, text='<= Skip', **h8bB_width10, command=self.tempseq_skip)
        temp_seq_CB.grid(row=14, column=1, **x4y3w)
        temp_tol_CB.grid(row=15, column=1, **x4y3w)
        temp_tol_check.grid(row=15, column=2, **x4y3w)
        chirp_seq_CB.grid(row=16, column=1, **x4y3)
        previous_E.grid(row=17, column=1, **x4y3)
        current_E.grid(row=18, column=1, **x4y3)
        next_E.grid(row=19, column=1, **x4y3)
        continue_B.grid(row=18, column=2)
        skip_B.grid(row=19, column=2)

        sep8 = ttk.Separator(frame, orient='horizontal')
        sep8.grid(row=20, column=0, columnspan=3, padx=40, pady=10, sticky='ew')

        fft_L = ttk.Label(frame, text='Automatically FFT saved files', **h10bL_r)
        sr_L = ttk.Label(frame, text='Sampling Rate', **label_fmt)
        sr_units = ttk.Label(frame, text='GSa/s', **h10bL_r)
        fstart_L = ttk.Label(frame, text='Start Freq.', **label_fmt)
        fstart_units = ttk.Label(frame, text='MHz', **h10bL_r)
        fstop_L = ttk.Label(frame, text='Stop Freq.', **label_fmt)
        fstop_units = ttk.Label(frame, text='MHz', **h10bL_r)
        ff_L = ttk.Label(frame, text='Fraction of FID', **label_fmt)
        kb_L = ttk.Label(frame, text='Kaiser-Bessel', **label_fmt)
        trl_L = ttk.Label(frame, text='Record Length', **label_fmt)
        trl_units = ttk.Label(frame, text=' \u03BCs', **h10bL_r)
        fft_L.grid(row=21, column=1, columnspan=2, **x4y10, sticky='w')
        sr_L.grid(row=22, column=0, **x4y3)
        fstart_L.grid(row=23, column=0, **x4y3)
        fstop_L.grid(row=24, column=0, **x4y3)
        ff_L.grid(row=25, column=0, **x4y3)
        kb_L.grid(row=26, column=0, **x4y3)
        trl_L.grid(row=27, column=0, **x4y3)
        sr_units.grid(row=22, column=2, **x4y3w)
        fstart_units.grid(row=23, column=2, **x4y3w)
        fstop_units.grid(row=24, column=2, **x4y3w)
        trl_units.grid(row=27, column=2, **x4y3w)

        fft_check = ttk.Checkbutton(frame, variable=self.fftbool)
        sr_CB = ttk.Combobox(frame, textvariable=self.sr, **width25_c)
        sr_CB['values'] = (25, 50)
        fstart_CB = ttk.Combobox(frame, textvariable=self.fftlower, **width25_c)
        fstart_CB['values'] = (2000, 6000)
        fstop_CB = ttk.Combobox(frame, textvariable=self.fftupper, **width25_c)
        fstop_CB['values'] = (8000, 18000)
        ff_CB = ttk.Combobox(frame, textvariable=self.ff, **width25_c)
        ff_CB['values'] = (0.25, 0.5, 1)
        kb_CB = ttk.Combobox(frame, textvariable=self.kb, **width25_c)
        kb_CB['values'] = (4, 9.5)
        trl_CB = ttk.Combobox(frame, textvariable=self.trl, **width25_c)
        trl_CB['values'] = (40, 60, 80)
        fft_check.grid(row=21, column=0, **x4y3e)
        sr_CB.grid(row=22, column=1, **x4y3)
        fstart_CB.grid(row=23, column=1, **x4y3)
        fstop_CB.grid(row=24, column=1, **x4y3)
        ff_CB.grid(row=25, column=1, **x4y3)
        kb_CB.grid(row=26, column=1, **x4y3)
        trl_CB.grid(row=27, column=1, **x4y3)

        archive_run = ttk.Button(buttons_frame, text='Run', **h10bB_width10, command=self.auto_run)
        archive_pause = ttk.Button(
            buttons_frame, text='Pause', **h10bB_width10, command=self.auto_stop)
        archive_stop = ttk.Button(
            buttons_frame, text='Abort', style='h10b.TButton', width=12,
            command=lambda: self.auto_stop(clear_scope=True, awg_stop=True, lower_temp=True))
        archive_run.grid(row=0, column=0, **x4y10)
        archive_pause.grid(row=0, column=1, **x4y10)
        archive_stop.grid(row=0, column=2, **x4y10)

    def check_instsetup(self):
        """
        Confirm oscilloscope is set up for the requested spectral region.
        Ask for user input if inconsistent.

        Query oscilloscope for sampling rate, which determines the spectral region.
        Linked variables:
            self.instsetup, self.scope_module.sr
        """
        if str(self.instsetup.get()) == '2-8':
            err_msg = 'Oscilloscope set up for 6-18 GHz collection. Switch to 2-8 GHz setup?'
            if str(self.scope_module.sr.get()) != '25':
                if askokcancel('Unexpected Oscilloscope Setup', message=err_msg):
                    self.scope_module.setup.set('2-8 GHz (CH2)')
                    self.scope_module.recall_setup(
                        self.scope_module.scope_setup_dict['2-8 GHz (CH2)'])
        elif str(self.instsetup.get()) == '6-18':
            err_msg = 'Oscilloscope set up for 2-8 GHz collection. Switch to 6-18 GHz setup?'
            if str(self.scope_module.sr.get()) != '50':
                if askokcancel('Unexpected Oscilloscope Setup', message=err_msg):
                    self.scope_module.setup.set('6-18 GHz (CH3)')
                    self.scope_module.recall_setup(
                        self.scope_module.scope_setup_dict['6-18 GHz (CH3)'])

    def check_math2mem(self):
        """
        Confirm (self.scope_module.math2_mem/8) is not less than self.save_every.
        Change math2_mem if inconsistent.

        If (math2_mem/8) < save_every, data at the beginning of measurement is overwritten before
        waveform is saved.

        Linked variables:
            self.save_every, self.scope_module.math2_mem
        """
        if int(self.save_every.get()) > int(self.scope_module.math2_mem.get()):
            self.scope_module.math2_mem.set(int(self.save_every.get()))
            self.scope_module.math2_mem.set(math.ceil(int(self.save_every.get()) / 8))

    def check_fft_bounds(self):
        """
        Confirm auto FFT bounds match spectral region. Change bounds if inconsistent.

        Linked variables:
            self.instsetup, self.fftlower, self.fftupper
        """
        if self.fftbool.get():
            if str(self.instsetup.get()) == '2-8':
                self.fftlower.set(2000)
                self.fftupper.set(8000)
            elif str(self.instsetup.get()) == '6-18':
                self.fftlower.set(6000)
                self.fftupper.set(18000)

    def check_temp_sv(self):
        """
        Confirm self.temp matches temperature controller set point.
        Ask for user input if inconsistent.

        Linked variables:
            self.temp, self.temp_module.sv
        """
        auto_temp = self.temp.get()
        try:
            tc1, tc2, tc3 = self.temp_module.connect()
            tc1_sv = tc1.read_setpoint_value()
            tc2_sv = tc2.read_setpoint_value()
            tc3_sv = tc3.read_setpoint_value()
            if tc1_sv == tc2_sv == tc3_sv:
                if float(auto_temp) != float(tc1_sv):
                    err_msg = 'Temperature controller set point inconsistent with value from ' \
                              'Automated Spectrum Collection. Change set point to ' + \
                              str(auto_temp) + 'C?'
                    err = askyesnocancel('Unexpected Temperature', message=err_msg)
                    if err is None:
                        pass
                    if err:
                        tc1.write_setpoint_value(int(auto_temp))
                        tc2.write_setpoint_value(int(auto_temp))
                        tc3.write_setpoint_value(int(auto_temp))
                        self.temp_module.sv.set(auto_temp)
                    elif not err:
                        self.temp_module.event.set()
                        self.temp_module.monitor(feedback=False)
                        self.temp.set(str(self.temp_module.sv.get()))
            else:
                err_msg = 'Set point temperatures inconsistent. Change to consistent value?'
                sv = simpledialog.askinteger('Set Temperature', prompt=err_msg)
                if sv is not None:
                    tc1.write_setpoint_value(int(sv))
                    tc2.write_setpoint_value(int(sv))
                    tc3.write_setpoint_value(int(sv))
        except minimalmodbus.NoResponseError:
            self.temp_module.conn.configure(text='Disconnected', foreground='red',
                                            font=('Helvetica', '10', 'bold'))
            self.temp_module.sv.set('?')
            self.temp_module.noz1_pv.set('?')
            self.temp_module.noz2_pv.set('?')
            self.temp_module.noz3_pv.set('?')

    def check_tempseq(self):
        """
        Confirm properly formatted temperature sequence is provided. Inform user if inconsistent.

        Linked variables:
            self.tempseq, self.temp_module.sv
        """
        if self.tempseq.get() in [None, 'None', 'none']:
            msg = "No sequence entered. Format -> First, Last, Increment."
            showerror(title='Invalid Temperature Sequence', message=msg)
        elif self.tempseq.get() == 'Format -> First, Last, Increment':
            msg = "Format example selected, which is not a valid sequence. Enter a valid sequence."
            showerror(title='Invalid Temperature Sequence', message=msg)
        else:
            sequence = self.tempseq.get()
            sequence = sequence.replace(',', '').split()
            if sequence[0] != self.temp_module.sv.get():
                self.temp_module.set_sv(int(sequence[0]))

    def check_chirp(self):
        """
        Confirm active waveform matches self.instsetup and self.chirpdur.
        Ask for user input if inconsistent.

        Linked variables:
            self.awg_module.output_wf, self.instsetup, self.chirpdur
        """
        consistent_setups = (('2-8', '4', '2_8_GHz_4mus_8_frames.txt'),
                             ('2-8', '2', '2_8_GHz_2mus_8_frames.txt'),
                             ('2-8', '1', '2_8_GHz_1mus_8_frames.txt'),
                             ('6-18', '4', '3_9_GHz_4mus_8_frames.txt'),
                             ('6-18', '2', '3_9_GHz_2mus_8_frames.txt'),
                             ('6-18', '1', '3_9_GHz_1mus_8_frames.txt'))
        for x, y, z in consistent_setups:
            if str(self.instsetup.get()) == x:
                if str(self.chirpdur.get()) == y:
                    if str(self.awg_module.output_wf.get()) != z:
                        err_msg = 'Unexpected waveform for a ' + y + ' microsecond ' + x \
                                  + ' GHz chirp.\nSwitch to ' + z + '?'
                        if askyesnocancel('Unexpected waveform', message=err_msg):
                            self.awg_module.stop()
                            self.awg_module.output_wf.set(z)

    def check_chirpseq(self):
        """
        Confirm correct waveform is active before starting chirp sequence.

        Linked variables:
            self.awg_module.output_wf, self.chirpseq
        """
        first_chirp = {'2-8 GHz:     1, 2, 4 microsecond': '2_8_GHz_1mus_8_frames.txt',
                       '2-8 GHz:     4, 2, 1 microsecond': '2_8_GHz_4mus_8_frames.txt',
                       '6-18 GHz:     1, 2, 4 microsecond': '3_9_GHz_1mus_8_frames.txt',
                       '6-18 GHz:     4, 2, 1 microsecond': '3_9_GHz_4mus_8_frames.txt'}
        self.awg_module.output_wf.set(first_chirp[self.chirpseq.get()])
        self.awg_module.load_wf()

    def auto_prerun_check(self):
        """
        Full instrument check using linked variables.

        Use at the beginning of self.auto_run() to ensure information presented on GUI is
        consistent with the actual instrument settings.

        See 'check' methods for linked variables.
            check_instsetup()
            check_math2mem()
            check_fft_bounds()
            check_temp_sv()
            check_tempseq()
            check_chirp()
            check_chirpseq()
        """
        runmode = self.runmode.get()
        self.check_instsetup()
        self.check_math2mem()
        if self.fftbool.get():
            self.check_fft_bounds()
        if runmode == 'temperature sequence':
            self.check_tempseq()
        else:
            self.check_temp_sv()
        if runmode == 'chirp sequence':
            self.check_chirpseq()
        else:
            self.check_chirp()

    def auto_run(self):
        """
        Communicate with scope, awg, and temp controllers to monitor measurements and save data
        at set intervals.

        Runs on dedicated thread that can be terminated at any time by self.event.set().

        Modes of operation:
            1. single
                Collect a user defined number of FIDs, save waveform, stop data acquisition.
            2. continuous
                Collect a user defined number of FIDs, save waveform, repeat until
                self.event.is_set().
            3. temperature ramp
                Collect user defined number of FIDs, save waveform, change temperature, repeat until
                spectra has been collected for all temperatures.
            4. chirp sequence
                Collect user defined number of FIDs, save waveform, change chirp, repeat until
                spectra has been collected for all chirp durations.
        Procedure:
            1.  event.set() on scope and temp cont events to terminate any previous monitoring
                processes. This prevents communication errors with instrument.
            2.  event.clear() scope and temperature controller events to allow new processes.
            3.  Pre-run check with self.auto_prerun_check().
            4.  self.event.clear().
            5.  Determine mode.
            6.  Run mode on dedicated thread.
        """
        self.scope_module.event.set()
        self.temp_module.event.set()

        self.scope_module.event.clear()
        self.temp_module.event.clear()

        self.auto_prerun_check()

        if self.event.is_set():
            self.event.clear()

        mode = self.runmode.get()

        if mode == 'single':
            def thread_func():
                self.single()
        elif mode == 'continuous':
            def thread_func():
                self.continuous()
        elif mode == 'temperature sequence':
            sequence = self.tempseq.get()
            sequence = sequence.replace(',', '').split()
            for x in range(len(sequence)):
                sequence[x] = int(sequence[x])
            temps = np.arange(sequence[0], sequence[1] + sequence[2], sequence[2])

            def thread_func():
                self.temperature_sequence(temps)
        elif mode == 'chirp sequence':
            def thread_func():
                self.chirp_sequence(self.chirpseq.get())
        t = Thread(name='auto run', target=thread_func)
        t.start()

    def auto_stop(self, clear_scope=False, awg_stop=False, lower_temp=False):
        """
        Pause or abort the archive process.

        Parameters:
            clear_scope (bool):
                Clear waveform data from oscilloscope.
                Default: False
            awg_stop (bool):
                Stop waveform generation from awg.
                Default: False
            lower_temp (bool):
                Set nozzle temperature to 20 degrees C.
                Default: False
        """
        self.event.set()
        self.scope_module.stop()
        if clear_scope:
            self.scope_module.clear()
        if awg_stop:
            self.awg_module.stop()
        if lower_temp:
            self.temp_module.sv.set(20)
            self.temp_module.event.set()

    def fid_averaging(self):
        """
        Return trigger_save when self.scope_module.numavgs reached or when self.event.is_set().

        trigger_save used to avoid saving waveform if self.event.is_set().

        Returns:
            trigger_save (bool):
                Save FID if True.
        """
        trigger_save = False
        while True:
            num_avgs = int(self.scope_module.get_numavgs_and_cursormax())
            if num_avgs > self.save_every.get():
                trigger_save = True
                break
            if self.event.is_set():
                break
            else:
                time.sleep(2)
                self.temp_module.monitor(feedback=False)
        return trigger_save

    def single(self):
        """
        Save FID waveform after defined number of FIDs signal averaged. Stop data acquisition.

        Pause or abort process using PAUSE and ABORT buttons.
        """
        self.awg_module.run()
        self.scope_module.run(feedback=False)
        self.temp_module.event.set()

        trigger_save = self.fid_averaging()
        self.event.set()
        self.scope_module.stop()
        if trigger_save:
            self.auto_save_fid()
        if self.fftbool.get():
            self.auto_save_fft()
        self.scope_module.clear()
        self.awg_module.stop()
        self.scope_module.conn.configure(
            text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))
        self.temp_module.conn.configure(
            text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))
        self.temp_module.noz1_pv.set(self.temp_module.default['pv'])
        self.temp_module.noz2_pv.set(self.temp_module.default['pv'])
        self.temp_module.noz3_pv.set(self.temp_module.default['pv'])

    def continuous(self):
        """
        Save FID waveform after defined number of FIDs signal averaged, clear, restart, repeat
        until self.event.set().

        Pause or abort process using PAUSE and ABORT buttons.
        """
        self.awg_module.run()
        self.scope_module.run(feedback=False)
        self.temp_module.event.set()
        while not self.event.is_set():
            trigger_save = self.fid_averaging()
            if trigger_save:  # save if save_every was reached. Pass if self.event was set by abort.
                self.scope_module.stop()
                self.auto_save_fid()
                self.scope_module.clear()
                self.scope_module.run(feedback=False)
                if self.fftbool.get():
                    self.auto_save_fft()
                # trigger_save = False  # Reset trigger_save to False before restarting process
                else:
                    break
        self.temp_module.conn.configure(
            text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))
        self.temp_module.noz1_pv.set(self.temp_module.default['pv'])
        self.temp_module.noz2_pv.set(self.temp_module.default['pv'])
        self.temp_module.noz3_pv.set(self.temp_module.default['pv'])
        self.scope_module.stop()
        self.awg_module.stop()

    def temperature_sequence(self, sequence, start_tolerance=True, step_tolerance=False,
                             reset=False, tolerance=None):
        """
        Collect a series of spectra at different temperatures.

        Steps:
            1.  Set nozzle temperature to first temperature in sequence.
            2.  (Optional) Wait for nozzle temperature to enter accepted tolerance range.
                Set start_tolerance = True to enable this feature.
                Set start_tolerance = False to begin data acquisition immediately.
            3.  Start data acquisition
            4.  Save waveform after self.save_every number of FIDs are signal averaged
            5.  (Optional) Compute and save FFT.
            6.  Clear data.
            7.  Change temperature.
            8.  (Optional) Wait for nozzle temperature to enter accepted tolerance range.
                Set step_tolerance = True to enable this feature.
                Set start_tolerance = False to begin data acquisition immediately.
            9.  Restart data acquisition.

        Additional measurements can be added at the current temperature and upcoming measurements
        can be skipped while the measurement is running. Since the upcoming temperature is
        determined by querying self.seq_next, adding or skipping a measurement is accomplished
        by updating self.seq_next. See self.tempseq_continue() and self.tempseq_skip() for more
        information on  these processes.

        self.event.set() can be used to pause or abort process, which is executed with ABORT.

        Parameters:
            sequence (list):
                List of set point temperatures in ascending order.
            tolerance (float):
                Defines tolerance range around nozzle temp that triggers start of data acquisition.
                Units: Celsius
                Default: None
            start_tolerance (bool):
                If True, first measurement starts when nozzle temperature enters tolerance
                region around the first temperature in sequence. If False, first measurement starts
                as soon as possible.
                Default: True
            step_tolerance (bool):
                if True, all measurements do not start until nozzle temperature enters tolerance
                region around each step. If False, each measurement starts as soon as possible.
                Default: False
            reset (bool):
                Reset instrument on ABORT (clear scope, set temp low).
                Default: False
        """
        self.scope_module.event.set()
        self.scope_module.event.clear()
        self.temp_module.event.set()
        self.temp_module.event.clear()
        self.event.clear()

        time.sleep(2)
        self.awg_module.run()

        self.temp_module.sv.set(sequence[0])
        self.temp_module.set_sv()
        self.temp_module.monitor(feedback=False)

        self.seq_current.set(sequence[0])
        self.seq_next.set(sequence[1])
        self.temp.set(sequence[0])
        # Tolerance check ensures PV is within 3 degrees C of sequence[0] before starting scope.
        if start_tolerance:
            if tolerance is None:
                tolerance = 3
            self.wait_for_temp_tolerance(tolerance)
        self.scope_module.run(feedback=False)
        # Set fftbool False here, skips first loop iteration (before FID file is saved).
        fftbool = False
        # Save FID at each temperature in sequence (For all temperatures in sequence except first)
        while True:
            if self.event.is_set():
                break
            else:
                if step_tolerance:
                    self.wait_for_temp_tolerance(tolerance)
                self.scope_module.run(feedback=False)
                if fftbool:  # fft of previous iteration is executed here, after restarting scope.
                    self.auto_save_fft()
            fftbool = self.fftbool.get()  # Changing fftbool from False to self.fftbool.get() for next iteration.
            trigger_save = self.fid_averaging()
            if trigger_save:
                self.scope_module.stop()
                self.update_temp_queue(sequence)
                if self.seq_current.get() == 'Complete':
                    t = self.temp.get()
                    self.auto_save_fid(temp=t)
                    self.scope_module.clear()
                    break
                else:
                    t = self.temp.get()
                    self.temp_module.sv.set(self.seq_current.get())
                    self.temp_module.set_sv()
                    self.temp.set(self.seq_current.get())
                    self.auto_save_fid(temp=t)
                    self.scope_module.clear()
            else:
                fftbool = False
                break
        if fftbool:
            self.auto_save_fft()
        self.scope_module.stop()
        self.awg_module.stop()
        if reset:
            self.temp_module.sv.set('20')
            self.temp_module.set_sv()
            self.temp_module.conn.configure(
                text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))
            self.temp_module.noz1_pv.set('searching. . .')
            self.temp_module.noz2_pv.set('searching. . .')
            self.temp_module.noz3_pv.set('searching. . .')
            self.scope_module.clear()

    def tempseq_continue(self):
        """
        When the current measurement finishes, run an additional measurement at the same
        temperature before continuing to next temperature in the queue by updating self.seq_next.

        Useful if volatile compound has not been sufficiently depleted.
        """
        curr = self.seq_current.get()
        curr = curr.split(')')
        curr = curr[0].split('(')
        curr_temp = int(curr[0].strip())
        try:
            curr_iter = int(curr[1].strip())
        except IndexError:
            curr_iter = 1
        repeat = '%s (%s)' % (curr_temp, curr_iter + 1)
        self.seq_next.set(repeat)

    def tempseq_skip(self):
        """ Skip the next temperature in the queue by updating self.seq_next. """
        seq_list = self.tempseq.get()
        seq_list = seq_list.replace(',', '').split()
        for x in range(len(seq_list)):
            seq_list[x] = int(seq_list[x])
        seq_list = np.arange(seq_list[0], seq_list[1] + seq_list[2], seq_list[2])
        next = self.seq_next.get()
        next = next.split(')')
        next = next[0].split('(')
        curr = int(next[0].strip())
        curr_ind = np.where(seq_list == curr)[0][0]
        next_temp = seq_list[curr_ind + 1]
        self.seq_next.set(str(next_temp))
        return next_temp

    def update_temp_queue(self, sequence):
        """
        Use to update sequence queue (previous, current, next) with correct temperatures after
        each iteration.

        Parameters:
            sequence (list):
                list of temperatures.
                Units: Celsius
        """
        self.seq_previous.set(self.seq_current.get())
        self.seq_current.set(self.seq_next.get().split('(')[0])
        index = 0
        try:
            while int(self.seq_next.get().split('(')[0]) != sequence[index + 1]:
                index += 1
            index += 1
            self.seq_next.set(sequence[index + 1])
        except IndexError:
            self.seq_next.set('Complete')
        except ValueError:
            self.seq_next.set('. . .')

    def wait_for_temp_tolerance(self, degrees=None, sleep_time=None):
        """
        Monitor nozzle temperature until temperature enters tolerance region.

        Parameters:
             degrees (float):
                Buffer to add to +/- sides of nozzle set point temp.
                Units: Celsius
                Default: 3
             sleep_time (float):
                Time in seconds before temperature is checked again.
                Units: seconds
                Default: 2
        """
        if degrees is None:
            degrees = 3
        if sleep_time is None:
            sleep_time = 2
        check = False
        while not check:
            if self.temp_module.pv_sv_tolerance_check(degrees):
                break
            elif self.event.is_set():
                break
            else:
                time.sleep(sleep_time)

    def chirp_sequence(self, setup):
        """
        Run a series of measurements with different chirp durations.

        Steps:
            1.  First waveform from sequence set as active waveform on AWG.
            2.  Start data acquisition
            3.  Save waveform after self.save_every number of FIDs are signal averaged.
            4.  (Optional) Compute and save FFT.
            5.  Clear data from scope.
            5.  Switch to next chirp.
            6.  Restart data acquisition.

        Parameters:
            setup (str):
                '2-8 GHz:     1, 2, 4 microsecond'
                '2-8 GHz:     4, 2, 1 microsecond'
                '6-18 GHz:     1, 2, 4 microsecond'
                '6-18 GHz:     4, 2, 1 microsecond'
        """
        seq_dict = {
            '2-8 GHz:     1, 2, 4 microsecond':
                ['2_8_GHz_1mus_8_frames.txt',
                 '2_8_GHz_2mus_8_frames.txt',
                 '2_8_GHz_4mus_8_frames.txt'],
            '2-8 GHz:     4, 2, 1 microsecond':
                ['2_8_GHz_4mus_8_frames.txt',
                 '2_8_GHz_2mus_8_frames.txt',
                 '2_8_GHz_1mus_8_frames.txt'],
            '6-18 GHz:     1, 2, 4 microsecond':
                ['3_9_GHz_1mus_8_frames.txt',
                 '2_8_GHz_2mus_8_frames.txt',
                 '2_8_GHz_4mus_8_frames.txt'],
            '6-18 GHz:     4, 2, 1 microsecond':
                ['3_9_GHz_4mus_8_frames.txt',
                 '2_8_GHz_2mus_8_frames.txt',
                 '2_8_GHz_1mus_8_frames.txt']}

        dur_dict = {'2-8 GHz:     1, 2, 4 microsecond': ['1', '2', '4'],
                    '2-8 GHz:     4, 2, 1 microsecond': ['4', '2', '1'],
                    '6-18 GHz:     1, 2, 4 microsecond': ['1', '2', '4'],
                    '6-18 GHz:     4, 2, 1 microsecond': ['4', '2', '1']}
        chirps = seq_dict[setup]
        durs = dur_dict[setup]

        self.scope_module.event.set()
        self.scope_module.event.clear()
        self.temp_module.event.set()
        self.temp_module.event.clear()
        self.event.clear()

        fftbool = False
        for x in range(len(chirps)):
            self.chirpdur.set(durs[x])
            self.seq_current.set(durs[x])
            if x == 0:
                self.seq_next.set(durs[x + 1])
            if x == 1:
                self.seq_previous.set(durs[x - 1])
                self.seq_next.set(durs[x + 1])
            if x == 2:
                self.seq_previous.set(durs[x - 1])
                self.seq_next.set('Complete')
            if self.event.is_set():
                break
            else:
                self.awg_module.output_wf.set(chirps[x])
                self.awg_module.load_wf()
                self.awg_module.run()
                self.scope_module.run(feedback=False)
                if fftbool:  # fft for previous iteration is executed, after restarting scope.
                    self.auto_save_fft()
            fftbool = self.fftbool.get()
            # trigger_save = False
            trigger_save = self.fid_averaging()
            if trigger_save:
                self.scope_module.stop()
                self.auto_save_fid()
                self.scope_module.clear()
            else:
                fftbool = False
                break
        if fftbool:
            self.auto_save_fft()
            self.scope_module.stop()
            self.scope_module.clear()
            self.awg_module.stop()

    def auto_save_fid(self, temp=None):
        """
        Save waveform in self.pickett_dir folder. File is named using information from GUI.

        Naming convention:
        {time}_{sample}_{setup}_{# FIDs}k_{temp}C_{chirp dur}us_{pressure}psig_.{ext}
            time: timestamp format: %H_%M_%S
            sample: self.fname
            setup: self.instsetup
            number FIDS: self.save_every
            temperature: self.temp
            chirp duration: self.chirpdur
            pressure: self.pressure
            ext: file extension. *.txt
        """
        directory = self.dir.get()
        sample_name = self.fname.get()
        inst = self.instsetup.get()
        save_every = int(self.save_every.get())
        if temp is None:
            temp = self.temp.get()
        chirp = self.chirpdur.get()
        pressure = self.pressure.get()
        if inst == '2-8':
            inst = '2to8'
        elif inst == '6-18':
            inst = '6to18'
        if save_every < 1000:
            avg_k = int(save_every)
            k = 'fid'
        else:
            avg_k = int(save_every / 1000)
            k = 'k'
        fname = '{t}_{name}_{setup}_{avg}{k}_{temp}C_{chirp}us_{pressure}psig_{ext}'
        fname = fname.format(
            t=time.strftime('%H_%M_%S'), name=sample_name, setup=inst, avg=avg_k, k=k, temp=temp,
            chirp=chirp, pressure=pressure, ext='.txt')
        os.chdir(directory)
        self.scope_module.save_fid(fname=fname)

    def auto_save_fft(self):
        """
        Calculate FFT of most recent waveform saved in self.pickett_dir. Naming convention given below.

        Naming Convention:
        {waveform name}_FF{FID fraction}_KB{Kaiser-Bessel}_TRL{total record length}_.{ext}
            waveform name:
                mirrors name of waveform file without *.txt extension.
            FID fraction:
                Fraction of the FID used in the FFT. To avoid decimals, the fraction is
                multiplied by 10.
            Kaiser-Bessel:
                Window filter parameter. To avoid decimals, parameter is multiplied by 10.
            total record length:
                Length of zero-padded waveform.
                Units: microseconds.
            ext:
                file extension. *.ft
        """
        directory = self.dir.get()
        sr = self.sr.get() * 1E9
        ff = self.ff.get()
        kb = self.kb.get()
        trl = self.trl.get()
        fftlower = self.fftlower.get()
        fftupper = self.fftupper.get()

        cwd_file_list = glob.glob(directory + '/*.txt')
        newest_file = max(cwd_file_list, key=os.path.getctime)
        waveform = os.path.join(directory, newest_file)
        fid_fname = os.path.basename(waveform)
        fid_fname = os.path.splitext(fid_fname)[0]
        fft_fname = '{fname}_FF{ff}_KB{kb}_TRL{zpl}_{ext}'
        fft_fname = fft_fname.format(
            fname=fid_fname, ff=str(round(ff * 10)), kb=str(round(kb * 10)), zpl=str(round(trl)),
            ext='.ft')
        fid = Spectrum.FID(waveform, srate=sr)
        fft = fid.quick_fft(frac=ff, kb=kb, total_time=trl, fstart=fftlower, fstop=fftupper)
        os.chdir(directory)
        np.savetxt(fft_fname, fft, fmt='%.4f, %.8f', delimiter=' ')
