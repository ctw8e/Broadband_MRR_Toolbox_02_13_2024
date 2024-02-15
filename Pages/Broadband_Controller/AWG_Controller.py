"""
Author: Channing West
Changelog: 1/4/2020

"""

import tkinter as tk
import tkinter.ttk as ttk
from threading import Thread, Event
import Pages.PageFormat as page_funcs
import os
import time
from Instrument_Drivers.AWG_Driver import AWGDriver, generate_waveform
import numpy as np
import pyvisa

label_fmt = {'justify': 'right', 'style': 'h10b.TLabel', 'width': 17, 'anchor': 'e'}


class AWGController(ttk.Frame):
    """
    Generate GUI to control the Tektronix AWG 7122.

    See AWG 7122 programmer manual for accepted SCPI commands.
    AWG startup placed on dedicated thread. See main_controller.py for more info on threading.

    Parameters:
        master (ttk.Frame)
    Attributes:
        self.setup (tk.StringVar):
            File path to AWG setup file. This file lives on the AWG, not the controller.
            Default: Standard_Chirps_Setup_2020.awg
        self.conn (tk.StringVar):
            Displays connection status
            Default: Closed
        self.state (tk.StringVar):
            Displays running state
            Default: searching. . .
        self.output_wf (tk.StringVar):
            File containing waveform currently loaded on the AWG. Ready to output.
            Default: 2_8_GHz_4mus_8_frames.txt
        self.sampling_rate (tk.StringVar):
            Sampling rate.
            Units: GSa./sec.
            Default: 24
        self.interleave (tk.IntVar):
            0 -> interleave off. 1 -> interleave active.
            Default: 1
        self.zeroing (tk.IntVar):
            0 -> zeroing off. 1 -> zeroing active.
            Default: 1
        self.runmode (tk.StringVar):
            AWG running mode.
            Default: TRIG
        self.clocksource (tk.StringVar):
            Clock source.
            Default: INT
        self.refsource (tk.StringVar):
            Reference source.
            Default: EXT

        self.write_sr (tk.StringVar):
            Sampling rate.
            Units: GSa./sec.
            Default: 24
        self.fstart (tk.StringVar):
            Starting frequency.
            Units: MHz
            Default: 2000
        self.fstop (tk.StringVar):
            Ending frequency.
            Units: MHz
            Default: 8000
        self.chirpdur (tk.StringVar):
            Chirp duration
            Units: microseconds
            Default: 4
        self.delay (tk.StringVar):
            Initial chirp delay
            Units: microseconds
            Default: 1.5
        self.m1_buffer (tk.StringVar):
            marker 1 buffer
            Units: microseconds
            Default: 0.5
        self.m2_buffer (tk.StringVar):
            marker 2 buffer
            Units: microseconds
            Default: 0.5
        self.m1_dur (tk.StringVar):
            marker 1 duration
            Units: microseconds
            Default: 1.0
        self.m2_dur (tk.StringVar):
            marker 2 duration
            Units: microseconds
            Default: 1.0
        self.end_buffer (tk.StringVar):
            Buffer after chirp
            Units: microseconds
            Default: 45
        self.num_frames (tk.StringVar):
            number of identical frames to create and concatenate using values from above.
            Default: 8
    Methods:
        connect()
            Connect to Tek AWG7122. Update self.conn.
        get_settings()
            Query AWG for current settings and update GUI.
        send_settings()
            Send settings from GUI to AWG.
        run()
            Open connection -> Send GUI settings to AWG -> Set AWG to RUN ->
            Update self.state and self.conn.
        stop()
            Open connection -> Set AWG to STOP -> Update self.state and self.conn.
        load_setup()
            Load AWG setup from *.awg file.
        load_wf()
            Switch active waveform, which is the output of the AWG when set to RUN.
        generate_wf()
            Generate and save waveform on dedicated thread.

    BUTTONS
    CONNECT
        Run self.get_settings(), which attempts to connect with Tek DPO73304,
        pulls current settings, and updates GUI.
    RECALL
        Load previously saved AWG setup. AWG setups are saved as *.awg files on the AWG,
        not the controller.
    SET OPTIONS
        Run self.send_settings(). Send settings to AWG.
    RUN
        run self.run(). Equivalent to putitng AWG into the 'AWGControl:RUN' state using the
        physical button on the AWG. No need to CONNECT to AWG before pressing RUN. Settings
        are sent from GUI to AWG when RUN is pressed.
    STOP
        Run self.stop(). Equivalent to putitng AWG into the 'AWGControl:STOP' state using the
        physical button on the AWG.
    WRITE CHIRP
        Generate waveform and save in *.txt file. Waveform generated using parameters from GUI.
    """
    default = {'connection': 'Closed',
               'state': 'searching. . .',
               'setup': 'Standard_Chirps_Setup_2020.awg',
               'output_waveform': '2_8_GHz_4mus_8_frames.txt',
               'sampling_rate': '24',
               'chirp_list': 'None',
               'interleave': 1,
               'zeroing': 1,
               'runmode': 'TRIG',
               'clocksource': 'INT',
               'refsource': 'EXT',

               'write_sr': '24',
               'fstart': '2000',
               'fstop': '8000',
               'chirpdur': '4',
               'delay': '1.5',
               'm1_buffer': '0.5',
               'm2_buffer': '0.5',
               'm1_duration': '1.0',
               'm2_duration': '1.0',
               'end_buffer': '45',
               'num_frames': '8'}

    setup_dict = {
        'Standard_Chirps_Setup_2020.awg':
            'C:\\Documents and Settings\\OEM\\Desktop\\Standard_CHIrps_Setup_2020.awg'}

    def __init__(self, master):
        self.setup = tk.StringVar()
        self.conn = tk.StringVar()
        self.state = tk.StringVar()
        self.output_wf = tk.StringVar()
        self.sampling_rate = tk.StringVar()
        self.interleave = tk.IntVar()
        self.zeroing = tk.IntVar()
        self.runmode = tk.StringVar()
        self.clocksource = tk.StringVar()
        self.refsource = tk.StringVar()
        self.setup.set(AWGController.default['setup'])
        self.conn.set(AWGController.default['connection'])
        self.output_wf.set(AWGController.default['output_waveform'])
        self.sampling_rate.set(AWGController.default['sampling_rate'])
        self.state.set(AWGController.default['state'])
        self.interleave.set(AWGController.default['interleave'])
        self.zeroing.set(AWGController.default['zeroing'])
        self.runmode.set(AWGController.default['runmode'])
        self.clocksource.set(AWGController.default['clocksource'])
        self.refsource.set(AWGController.default['refsource'])
        self.write_sr = tk.StringVar()
        self.fstart = tk.StringVar()
        self.fstop = tk.StringVar()
        self.chirpdur = tk.StringVar()
        self.delay = tk.StringVar()
        self.m1_buffer = tk.StringVar()
        self.m2_buffer = tk.StringVar()
        self.m1_dur = tk.StringVar()
        self.m2_dur = tk.StringVar()
        self.end_buffer = tk.StringVar()
        self.num_frames = tk.StringVar()
        self.write_sr.set(AWGController.default['write_sr'])
        self.fstart.set(AWGController.default['fstart'])
        self.fstop.set(AWGController.default['fstop'])
        self.chirpdur.set(AWGController.default['chirpdur'])
        self.delay.set(AWGController.default['delay'])
        self.m1_buffer.set(AWGController.default['m1_buffer'])
        self.m2_buffer.set(AWGController.default['m2_buffer'])
        self.m1_dur.set(AWGController.default['m1_duration'])
        self.m2_dur.set(AWGController.default['m2_duration'])
        self.end_buffer.set(AWGController.default['end_buffer'])
        self.num_frames.set(AWGController.default['num_frames'])

        h14bL_r_width11_anchorw = {
            'justify': 'right', 'anchor': 'w', 'style': 'h14b.TLabel', 'width': 11}
        h12bL_r_width11_anchorw = {
            'justify': 'right', 'anchor': 'w', 'style': 'h12b.TLabel', 'width': 11}
        h8bB_width11 = {'style': 'h8b.TButton', 'width': 11}
        x4y3w = {'padx': 4, 'pady': 3, 'sticky': 'w'}
        h8bB_width8 = {'style': 'h8b.TButton', 'width': 8}
        h10bB_width10 = {'style': 'h10b.TButton', 'width': 10}
        h10bL_r = {'style': 'h10b.TLabel', 'justify': 'right'}
        width25_c = {'justify': 'center', 'width': 25}
        x4y3 = {'padx': 4, 'pady': 3}

        frame = ttk.Frame(master)
        buttons_frame = ttk.Frame(frame)
        frame.grid(row=0, column=0, padx=20, pady=3, sticky='w')
        buttons_frame.grid(row=17, column=0, columnspan=4)

        awg_section_L = ttk.Label(frame, text='AWG', **h14bL_r_width11_anchorw)
        awg_section_L.grid(row=0, column=0, padx=0, pady=3, sticky='w')

        conn_L = ttk.Label(frame, text='Connection', **label_fmt)
        state_L = ttk.Label(frame, text='Running State', **label_fmt)
        self.conn = ttk.Label(frame, text='Closed', style='red10b.TLabel')
        self.state_L = ttk.Label(frame, text='searching. . .', style='h10.TLabel')
        conn_L.grid(row=1, column=1, **x4y3)
        state_L.grid(row=2, column=1, **x4y3)
        self.conn.grid(row=1, column=2, **x4y3w)
        self.state_L.grid(row=2, column=2, **x4y3w)

        conn_B = ttk.Button(frame, text='Connect', **h8bB_width8, command=self.get_settings)
        conn_B.grid(row=1, column=0, **x4y3w)

        sep6 = ttk.Separator(frame, orient='horizontal')
        sep6.grid(row=3, column=1, columnspan=3, padx=5, pady=10, sticky='ew')

        setup_B = ttk.Button(frame, text='Recall', **h8bB_width11, command=self.load_setup)
        setup_L = ttk.Label(frame, text='Setup', **label_fmt)
        setup_CB = ttk.Combobox(frame, textvariable=self.setup, justify='center', width=30)
        setup_CB['values'] = ('Standard_Chirps_Setup_2020.awg')
        setup_B.grid(row=4, column=0, **x4y3w)
        setup_L.grid(row=4, column=1, **x4y3)
        setup_CB.grid(row=4, column=2, columnspan=2, **x4y3)

        sep7 = ttk.Separator(frame, orient='horizontal')
        sep7.grid(row=5, column=1, columnspan=3, padx=5, pady=10, sticky='ew')

        wf_B = ttk.Button(frame, text='Set Options', **h8bB_width11, command=self.send_settings)
        wf_L = ttk.Label(frame, text='Waveform', **label_fmt)

        sr_L = ttk.Label(frame, text='Sampling Rate', **label_fmt)
        sr_CB = ttk.Combobox(frame, textvariable=self.sampling_rate, justify='center', width=15)
        sr_CB['values'] = (24, 12)
        sr_units = ttk.Label(frame, text='GSa./s', **h10bL_r)

        interleave_L = ttk.Label(frame, text='Interleave', **label_fmt)
        interleave_CButton = ttk.Checkbutton(frame, variable=self.interleave)

        zeroing_L = ttk.Label(frame, text='Zeroing', **label_fmt)
        zeroing_CButton = ttk.Checkbutton(frame, variable=self.zeroing)

        runmode_L = ttk.Label(frame, text='Run Mode', **label_fmt)
        trig_RB = ttk.Radiobutton(
            frame, text='Triggered', style='h8.TRadiobutton', variable=self.runmode, value='TRIG')
        cont_RB = ttk.Radiobutton(
            frame, text='Continuous', style='h8.TRadiobutton', variable=self.runmode, value='CONT')

        clocksource_L = ttk.Label(frame, text='Clock Source', **label_fmt)
        clock_ext_RB = ttk.Radiobutton(
            frame, text='External', style='h8.TRadiobutton', variable=self.clocksource, value='EXT')
        clock_int_RB = ttk.Radiobutton(
            frame, text='Internal', style='h8.TRadiobutton', variable=self.clocksource, value='INT')

        refsource_L = ttk.Label(frame, text='Reference', **label_fmt)
        ref_ext_RB = ttk.Radiobutton(
            frame, text='External', style='h8.TRadiobutton', variable=self.refsource, value='EXT')
        ref_int_RB = ttk.Radiobutton(
            frame, text='Internal', style='h8.TRadiobutton', variable=self.refsource, value='INT')

        wf_CB = ttk.Combobox(frame, textvariable=self.output_wf, justify='center', width=30)
        wf_CB['values'] = (
            '2_8_GHz_4mus_8_frames.txt', '2_8_GHz_2mus_8_frames.txt', '2_8_GHz_1mus_8_frames.txt',
            '6_18_GHz_4mus_8_frames.txt', '6_18_GHz_2mus_8_frames.txt',
            '6_18_GHz_1mus_8_frames.txt')
        wf_B.grid(row=6, column=0, **x4y3w)
        wf_L.grid(row=6, column=1, **x4y3)
        sr_L.grid(row=7, column=1, **x4y3)
        sr_CB.grid(row=7, column=2, **x4y3)
        sr_units.grid(row=7, column=3, **x4y3)
        interleave_L.grid(row=8, column=1, **x4y3)
        zeroing_L.grid(row=9, column=1, **x4y3)
        runmode_L.grid(row=10, column=1, **x4y3)
        clocksource_L.grid(row=12, column=1, **x4y3)
        refsource_L.grid(row=14, column=1, **x4y3)
        wf_CB.grid(row=6, column=2, columnspan=2, **x4y3)
        interleave_CButton.grid(row=8, column=2, **x4y3w)
        zeroing_CButton.grid(row=9, column=2, **x4y3w)

        trig_RB.grid(row=10, column=2, **x4y3w)
        cont_RB.grid(row=11, column=2, **x4y3w)

        clock_ext_RB.grid(row=12, column=2, **x4y3w)
        clock_int_RB.grid(row=13, column=2, **x4y3w)

        ref_ext_RB.grid(row=14, column=2, **x4y3w)
        ref_int_RB.grid(row=15, column=2, **x4y3w)

        sep9 = ttk.Separator(frame, orient='horizontal')
        sep9.grid(row=16, column=1, columnspan=3, padx=5, pady=10, sticky='ew')
        sep10 = ttk.Separator(frame, orient='horizontal')
        sep10.grid(row=18, column=1, columnspan=3, padx=5, pady=10, sticky='ew')

        # ______________________________________________________________________________________________________________
        write_F = ttk.Frame(frame)
        write_F.grid(row=19, column=0, columnspan=4)

        write_section_L = ttk.Label(write_F, text='Write Chirps', **h12bL_r_width11_anchorw)
        write_section_L.grid(row=0, column=0, **x4y3)

        write_sr_L = ttk.Label(write_F, text='Sampling Rate', **label_fmt)
        fstart_L = ttk.Label(write_F, text='Start Freq.', **label_fmt)
        fstop_L = ttk.Label(write_F, text='Stop Freq.', **label_fmt)
        chirpdur_L = ttk.Label(write_F, text='Chirp Duration', **label_fmt)
        delay = ttk.Label(write_F, text='Delay', **label_fmt)
        m1_buffer_L = ttk.Label(write_F, text='M1 Buffer', **label_fmt)
        m2_buffer_L = ttk.Label(write_F, text='M2 Buffer', **label_fmt)
        m1_dur_L = ttk.Label(write_F, text='M1 Duration', **label_fmt)
        m2_dur_L = ttk.Label(write_F, text='M2 Duration', **label_fmt)
        end_buffer_L = ttk.Label(write_F, text='End Buffer', **label_fmt)
        num_frames_L = ttk.Label(write_F, text='Frames', **label_fmt)
        write_sr_L.grid(row=1, column=1, **x4y3)
        fstart_L.grid(row=2, column=1, **x4y3)
        fstop_L.grid(row=3, column=1, **x4y3)
        chirpdur_L.grid(row=4, column=1, **x4y3)
        delay.grid(row=5, column=1, **x4y3)
        m1_buffer_L.grid(row=6, column=1, **x4y3)
        m2_buffer_L.grid(row=7, column=1, **x4y3)
        m1_dur_L.grid(row=8, column=1, **x4y3)
        m2_dur_L.grid(row=9, column=1, **x4y3)
        end_buffer_L.grid(row=10, column=1, **x4y3)
        num_frames_L.grid(row=11, column=1, **x4y3)

        write_sr_CB = ttk.Combobox(write_F, textvariable=self.write_sr, **width25_c)
        fstart_CB = ttk.Combobox(write_F, textvariable=self.fstart, **width25_c)
        fstop_CB = ttk.Combobox(write_F, textvariable=self.fstop, **width25_c)
        chirpdur_CB = ttk.Combobox(write_F, textvariable=self.chirpdur, **width25_c)
        delay_E = ttk.Entry(write_F, textvariable=self.delay, **width25_c)
        m1_buffer_E = ttk.Entry(write_F, textvariable=self.m1_buffer, **width25_c)
        m2_buffer_E = ttk.Entry(write_F, textvariable=self.m2_buffer, **width25_c)
        m1_duration_E = ttk.Entry(write_F, textvariable=self.m1_dur, **width25_c)
        m2_duration_E = ttk.Entry(write_F, textvariable=self.m2_dur, **width25_c)
        end_buffer_E = ttk.Entry(write_F, textvariable=self.end_buffer, **width25_c)
        num_frames_E = ttk.Entry(write_F, textvariable=self.num_frames, **width25_c)
        write_sr_CB['values'] = ('24', '12')
        fstart_CB['values'] = ('2000', '3000', '8000', '9000')
        fstop_CB['values'] = ('8000', '9000', '2000', '3000')
        chirpdur_CB['values'] = ('4', '2', '1')
        write_sr_CB.grid(row=1, column=2, **x4y3w)
        fstart_CB.grid(row=2, column=2, **x4y3w)
        fstop_CB.grid(row=3, column=2, **x4y3w)
        chirpdur_CB.grid(row=4, column=2, **x4y3w)
        delay_E.grid(row=5, column=2, **x4y3w)
        m1_buffer_E.grid(row=6, column=2, **x4y3w)
        m2_buffer_E.grid(row=7, column=2, **x4y3w)
        m1_duration_E.grid(row=8, column=2, **x4y3w)
        m2_duration_E.grid(row=9, column=2, **x4y3w)
        end_buffer_E.grid(row=10, column=2, **x4y3w)
        num_frames_E.grid(row=11, column=2, **x4y3w)

        write_sr_units = ttk.Label(write_F, text='GSa./s', **h10bL_r)
        fstart_units = ttk.Label(write_F, text='MHz', **h10bL_r)
        fstop_units = ttk.Label(write_F, text='MHz', **h10bL_r)
        chirpdur_units = ttk.Label(write_F, text='\u03BCs', **h10bL_r)
        delay = ttk.Label(write_F, text='\u03BCs', **h10bL_r)
        m1_buffer_units = ttk.Label(write_F, text='\u03BCs', **h10bL_r)
        m2_buffer_units = ttk.Label(write_F, text='\u03BCs', **h10bL_r)
        m1_dur_units = ttk.Label(write_F, text='\u03BCs', **h10bL_r)
        m2_dur_units = ttk.Label(write_F, text='\u03BCs', **h10bL_r)
        end_buffer_units = ttk.Label(write_F, text='\u03BCs', **h10bL_r)
        write_sr_units.grid(row=1, column=3, **x4y3w)
        fstart_units.grid(row=2, column=3, **x4y3w)
        fstop_units.grid(row=3, column=3, **x4y3w)
        chirpdur_units.grid(row=4, column=3, **x4y3w)
        delay.grid(row=5, column=3, **x4y3w)
        m1_buffer_units.grid(row=6, column=3, **x4y3w)
        m2_buffer_units.grid(row=7, column=3, **x4y3w)
        m1_dur_units.grid(row=8, column=3, **x4y3w)
        m2_dur_units.grid(row=9, column=3, **x4y3w)
        end_buffer_units.grid(row=10, column=3, **x4y3w)

        write_B = ttk.Button(
            write_F, text='Write Chirp', **h8bB_width11, command=self.generate_waveform)
        write_B.grid(row=1, column=0, **x4y3w)

        run = ttk.Button(buttons_frame, text='Run', **h10bB_width10, command=self.run)
        stop = ttk.Button(buttons_frame, text='Stop', **h10bB_width10, command=self.stop)
        run.grid(row=0, column=1, padx=4, pady=10)
        stop.grid(row=0, column=2, padx=4, pady=10)

    def connect(self):
        """ Connect to Tek AWG7122. Update self.conn. """
        try:
            awg = AWGDriver()
            self.conn.configure(text='Connected', foreground='green3')
            return awg
        except pyvisa.errors.VisaIOError:
            self.conn.configure(
                text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))

    def get_settings(self):
        """ Query AWG for current settings and update GUI. """
        awg = self.connect()
        awg.ch1_output = 1

        self.sampling_rate.set(str(int(float(awg.sampling_rate) * 1E-9)))
        self.zeroing.set(str(int(awg.zeroing)))
        self.interleave.set(str(int(awg.interleave)))
        self.runmode.set(str(awg.run_mode))
        self.clocksource.set(str(awg.clock_source))
        self.refsource.set(str(awg.ref_source))
        waveform = awg.waveform
        self.output_wf.set(str(waveform.replace('"', '')))

    def send_settings(self):
        """ Send settings from GUI to AWG. """
        awg = self.connect()
        awg.ch1_output = 1
        awg.sampling_rate = int(float(self.sampling_rate.get()) * 1E9)
        awg.zeroing = self.zeroing.get()
        awg.interleave = self.interleave.get()
        awg.run_mode = self.runmode.get()
        awg.clock_source = self.clocksource.get()
        awg.ref_source = self.refsource.get()
        awg.waveform = self.output_wf.get()

    def run(self):
        """
        Open connection -> Send GUI settings to AWG -> Set AWG to RUN ->
        Update self.state and self.conn.
        """
        def thread_func():
            awg = self.connect()
            self.send_settings()
            if int(awg.ch1_output) == 0:
                awg.ch1_output = 1
            awg.run()
            self.state_L.configure(
                text='Running', foreground='green3', font=('Helvetica', '10', 'bold'))
        t = Thread(name='awg run', target=thread_func)
        t.start()

    def stop(self):
        """ Open connection -> Set AWG to STOP -> Update self.state and self.conn. """
        # Changed this to be threaded 5/30/21
        awg = self.connect()

        def thread_func():
            awg.stop()
            self.state_L.configure(
                text='Stopped', foreground='red', font=('Helvetica', '10', 'bold'))
            # self.conn.configure(text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))
        t = Thread(name='awg stop', target=thread_func)
        t.start()

    def load_setup(self):
        """
        Load AWG setup from *.awg file. Setup files contain settings and load a list of waveforms
        into memory. Only one setup currently supported.
        """
        fname = AWGController.setup_dict[self.setup.get()]
        awg = self.connect()
        awg.import_setup(fname)
        time.sleep(30)
        awg = self.connect()

    def load_wf(self):
        """ Switch active waveform, which is the output of the AWG when set to RUN. """
        wf = self.output_wf.get()
        awg = self.connect()  # waveform=wf)  # todo probably have to pass wf as arg here to avoid overwriting with scope query
        awg.active_waveform(wf)

    def generate_waveform(self):
        """
        Generate and save waveform on dedicated thread.

        Run AWG_Driver.generate_waveform() using data from GUI entry fields.
        Save to file using naming convention: '{fstart}_{fstop}MHz_{dur}mus_{num_frames}frames.txt'
        """
        fstart = self.fstart.get()
        fstop = self.fstop.get()
        dur = self.chirpdur.get()
        num_frames = int(self.num_frames.get())
        fname_outer = str(fstart) + '_' + str(fstop) + 'MHz_' + str(dur) + \
                      'mus_' + str(num_frames) + 'frames.txt'
        sr = int(self.write_sr.get()) * 1E9
        fstart = float(fstart) * 1E6
        fstop = float(fstop) * 1E6
        dur = float(dur) * 1E-6
        delay = float(self.delay.get()) * 1E-6
        m1_buffer = float(self.m1_buffer.get()) * 1E-6
        m2_buffer = float(self.m2_buffer.get()) * 1E-6
        m1_dur = float(self.m1_dur.get()) * 1E-6
        m2_dur = float(self.m2_dur.get()) * 1E-6
        end_buffer = float(self.end_buffer.get()) * 1E-6

        def thread_func():
            wf = generate_waveform(
                sr, fstart, fstop, dur, delay=delay, m1_buffer=m1_buffer, m2_buffer=m2_buffer,
                m1_duration=m1_dur, m2_duration=m2_dur, end_buffer=end_buffer,
                num_frames=num_frames)
            fname = page_funcs.save_file(
                initialfile=fname_outer, ftype='.txt', defaultextension='.txt')
            if fname:
                np.savetxt(fname, wf, fmt='%s')
            else:
                pass
        t = Thread(name='write chirp', target=thread_func)
        t.start()
