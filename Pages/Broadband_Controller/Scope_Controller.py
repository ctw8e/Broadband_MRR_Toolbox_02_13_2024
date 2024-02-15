"""
Author: Channing West
Changelog: 1/4/2020

"""

import tkinter as tk
import tkinter.ttk as ttk
import math
import threading
from threading import Thread, Event
import time
from Instrument_Drivers.Oscilloscope_Driver import OscilloscopeDriver
import numpy as np
import Pages.PageFormat as page_funcs


class ScopeController(ttk.Frame):
    """
    Generate GUI to control the Tektronix DPO 73304B.

    Communication acheived through SCPI commands. See DPO 73304B programmer manual for commands.

    Data acquisition begins when RUN is pressed. Osilloscope monitoring occurs on a dedicated
    thread. Number of FIDs signal averaged is checked periodically as well as the intensity of the
    strongest signal observed between cursor1 and cursor2. Values relayed to the GUI. An instance
    of threading.Event() controls when the thread is terminated. While event.clear(), data
    acquisition and GUI updates continue. When STOP is pressed, event.is_set() is triggered, which
    terminates the thread. See main_controller.py for more info on threading.

    Parameters:
        master (ttk.Frame)
    Attributes:
        self.conn (tk.StringVar):
            Displays connection status
            Default: Closed
        self.state (tk.StringVar):
            Displays running state
            Default: searching. . .
        self.setup (tk.StringVar):
            Instrument setup. Frequency region.
            Default: 2-8 GHz (CH2)
        self.channel (tk.StringVar):
            Waveform retrieved from this channel when SAVE is called.
            SCPI commands: CH1, CH2, CH3, CH4, MATH1, MATH2, etc. Default MATH2
            Default: MATH2
        self.acq_t (tk.StringVar):
            Waveform acquisition time.
            Units: microseconds.
            Default: 40
        self.delay_t (tk.StringVar):
            Horizontal dealy time.
            Units: microseconds.
            Default: 3
        self.sr (tk.StringVar):
            Sampling rate.
            Units: GSa./sec.
            Default: 25
        self.math2_mem (tk.IntVar):
            Number of FID waveforms held in memory.
            Default: 1000000
        self.cursor1 (tk.StringVar):
            Position of cursor1.
            Units: MHz.
            Default: 2000
        self.cursor2 (tk.StringVar):
            Position of cursor2.
            Units: MHz
            Default: 8000
        self.cursormax (tk.StringVar):
            Intensity of the strongest signal observed between cursor1 and cursor2.
            Units: mV
            Default: searching. . .
        self.numavgs (tk.StringVar):
            Number of waveforms collected since last CLEAR.
        self.event (threading.Event):
            self.event.is_set() to abort thread.
    Methods:
        connect()
            Establish connection with Tek DPO73304. Query oscilloscope for running state.
            Update connection status and running state.
        recall_setup()
            Recall previously saved setup located on oscilloscope hard drive with *.set extension.
        get_settings()
            Connect to oscilloscope. Query scope for current settings and update GUI.
        send_settings()
            Send settings from GUI to scope.
        get_numavgs_and_cursormax()
            Query scope for the number of FIDs recorded. Update self.numavgs and self.cursormax.
        run(feedback)
            Begin data acquisition. Monitor FID count and max intensity between cursors.
        stop()
            End data acquisition. Terminate self.event thread.
        save_fid(fname)
            Save waveform.
        clear()
            Clear all data from oscilloscope and update GUI.
    BUTTONS:
        CONNECT
            Run self.get_settings().
            Attempt connection with Tek DPO73304. Update self.conn and self.state.
            Update GUI with settings pulled from scope.
        RECALL
            Run self.recall_setup().
            Attempt connection with Tek DPO73304. Recall previously saved setup located on
            oscilloscope hard drive with *.set extension.
        SET OPTIONS
            Run self.send_settings().
            Send settings to oscilloscope.
        RUN
            Run self.run().
            Equivalent to pressing Run/Stop button on oscilloscope to begin acquiring
            data. No need to CONNECT to the instrument before hitting RUN. When RUN
            is pressed, all settings are sent from the GUI to the scope.
        STOP
            Run self.stop().
            Equivalent to pressing Run/Stop button on oscilloscope to stop acquiring data.
        SAVE
            Run self.save_fid().
            Save current waveform from oscilloscope.
        CLEAR
            Run self.clear().
            Equivalent to pressing Clear button on oscilloscope. Clear all waveforms from scope.
    """
    default = {'connection': 'Closed',
               'state': 'searching. . .',
               'setup': '2-8 GHz (CH2)',
               'channel': 'MATH2',
               'acq_time': '40',
               'delay': '3',
               'sampling_rate': '25',
               'math2avg': '1000000',
               'cursor1': '2000',
               'cursor2': '8000',
               'cursormax': 'searching. . .',
               'acqs': 'searching. . .'}

    setup_dict = {'2-8 GHz (CH2)': 'C:\\2-8GHzch2.set',
                  '6-18 GHz (CH3)': 'C:\\6-18GHz CH3 August 2019.set'}

    def __init__(self, master):
        self.conn = tk.StringVar()
        self.state = tk.StringVar()
        self.setup = tk.StringVar()
        self.channel = tk.StringVar()
        self.acq_t = tk.StringVar()
        self.delay_t = tk.StringVar()
        self.sr = tk.StringVar()
        self.math2_mem = tk.IntVar()
        self.cursor1 = tk.StringVar()
        self.cursor2 = tk.StringVar()
        self.cursormax = tk.StringVar()
        self.numavgs = tk.StringVar()
        self.conn.set(ScopeController.default['connection'])
        self.state.set(ScopeController.default['state'])
        self.setup.set(ScopeController.default['setup'])
        self.channel.set(ScopeController.default['channel'])
        self.acq_t.set(ScopeController.default['acq_time'])
        self.delay_t.set(ScopeController.default['delay'])
        self.sr.set(ScopeController.default['sampling_rate'])
        self.math2_mem.set(ScopeController.default['math2avg'])
        self.cursor1.set(ScopeController.default['cursor1'])
        self.cursor2.set(ScopeController.default['cursor2'])
        self.cursormax.set(ScopeController.default['cursormax'])
        self.numavgs.set(ScopeController.default['acqs'])

        self.event = Event()

        h = 'horizontal'
        label_fmt = {'justify': 'right', 'style': 'h10b.TLabel', 'width': 17, 'anchor': 'e'}
        x4y3 = {'padx': 4, 'pady': 3}
        x4y3w = {'padx': 4, 'pady': 3, 'sticky': 'w'}
        h8bB_width11 = {'style': 'h8b.TButton', 'width': 11}
        h8bB_width10 = {'style': 'h8b.TButton', 'width': 10}
        h8bB_width7 = {'style': 'h8b.TButton', 'width': 7}
        h8bB_width8 = {'style': 'h8b.TButton', 'width': 8}
        h10bL_r = {'style': 'h10b.TLabel', 'justify': 'right'}
        width25_c = {'justify': 'center', 'width': 25}

        frame = ttk.Frame(master)
        frame.grid(row=0, column=0, padx=20, pady=3, sticky='w')

        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=17, column=0, columnspan=4, padx=4, pady=10)

        section_L = ttk.Label(frame, text='Oscilloscope', anchor='w', style='h14b.TLabel', width=11)
        section_L.grid(row=0, column=0, pady=3, sticky='w')

        conn_L = ttk.Label(frame, text='Connection', **label_fmt)
        state_L = ttk.Label(frame, text='Running State', **label_fmt)
        conn_L.grid(row=1, column=1, **x4y3)
        state_L.grid(row=2, column=1, **x4y3)

        self.conn = ttk.Label(frame, text='Closed', style='red10b.TLabel')
        self.state_L = ttk.Label(frame, text='searching. . .', style='h10.TLabel')
        self.conn.grid(row=1, column=2, **x4y3w)
        self.state_L.grid(row=2, column=2, **x4y3w)

        sep1 = ttk.Separator(frame, orient=h)
        sep1.grid(row=3, column=1, columnspan=3, padx=5, pady=10, sticky='ew')

        # __________________________________________________________________________________________
        setup_L = ttk.Label(frame, text='Setup', style='h10b.TLabel')
        setup_L.grid(row=4, column=1, **x4y3, sticky='e')

        setup_B = ttk.Button(frame, text='Recall', **h8bB_width11, command=self.recall_setup)
        setup_B.grid(row=4, column=0, **x4y3w)

        setup_CB = ttk.Combobox(frame, textvariable=self.setup, **width25_c)
        setup_CB['values'] = ('2-8 GHz (CH2)', '6-18 GHz (CH3)')
        setup_CB.grid(row=4, column=2, **x4y3)

        sep2 = ttk.Separator(frame, orient=h)
        sep2.grid(row=5, column=1, columnspan=3, padx=5, pady=10, sticky='ew')

        # __________________________________________________________________________________________
        before_options = ttk.Button(
            frame, text='Set Options', **h8bB_width11, command=self.send_settings)
        before_run_L = ttk.Label(frame, text='Set these options\nbefore run', style='red10b.TLabel')
        before_options.grid(row=6, column=0, padx=4, sticky='w')
        before_run_L.grid(row=7, column=0, rowspan=3, padx=4, sticky='w')

        acq_time_L = ttk.Label(frame, text='Acquisition Time', **label_fmt)
        delay_time_L = ttk.Label(frame, text='Horizontal Delay', **label_fmt)
        sr_L = ttk.Label(frame, text='Sampling Rate', **label_fmt)
        math2_memory_L = ttk.Label(frame, text='Math2 Memory', **label_fmt)
        acq_time_L.grid(row=6, column=1, **x4y3)
        delay_time_L.grid(row=7, column=1, **x4y3)
        sr_L.grid(row=8, column=1, **x4y3)
        math2_memory_L.grid(row=9, column=1, **x4y3)

        acq_time_units = ttk.Label(frame, text='\u03BCs', **h10bL_r)
        delay_time_units = ttk.Label(frame, text='\u03BCs', **h10bL_r)
        sr_units = ttk.Label(frame, text='GSa./s', **h10bL_r)
        math2_memory_units = ttk.Label(frame, text='FIDs', **h10bL_r)
        acq_time_units.grid(row=6, column=3, padx=4, sticky='w')
        delay_time_units.grid(row=7, column=3, padx=4, sticky='w')
        sr_units.grid(row=8, column=3, padx=4, sticky='w')
        math2_memory_units.grid(row=9, column=3, **x4y3w)

        acq_time_CB = ttk.Combobox(frame, textvariable=self.acq_t, **width25_c)
        acq_time_CB['values'] = ('40', '20')
        sr_CB = ttk.Combobox(frame, textvariable=self.sr, **width25_c)
        sr_CB['values'] = ('25', '50')
        math2_mem_CB = ttk.Combobox(frame, textvariable=self.math2_mem, **width25_c)
        math2_mem_CB['values'] = ('1000000', '400000', '100000', '10000', '100')
        delay_E = ttk.Entry(frame, textvariable=self.delay_t, **width25_c)
        acq_time_CB.grid(row=6, column=2, **x4y3)
        delay_E.grid(row=7, column=2, **x4y3w)
        sr_CB.grid(row=8, column=2, **x4y3)
        math2_mem_CB.grid(row=9, column=2, **x4y3)

        sep1 = ttk.Separator(frame, orient=h)
        sep1.grid(row=10, column=1, columnspan=3, padx=5, pady=10, sticky='ew')

        # __________________________________________________________________________________________
        after_options = ttk.Button(
            frame, text='Set Options', **h8bB_width11, command=self.send_settings)
        # after_run_L = ttk.Label(F, text='Set before run', style='red10b.TLabel')
        after_options.grid(row=11, column=0, padx=4, sticky='w')
        # after_run_L.grid(             row=7, column=0, padx=4,  sticky='w')

        channel_L = ttk.Label(frame, text='Data Source', **label_fmt)
        cursor1_L = ttk.Label(frame, text='Cursor 1', **label_fmt)
        cursor2_L = ttk.Label(frame, text='Cursor 2', **label_fmt)
        channel_L.grid(row=11, column=1, **x4y3)
        cursor1_L.grid(row=12, column=1, **x4y3)
        cursor2_L.grid(row=13, column=1, **x4y3)

        channel_CB = ttk.Combobox(frame, textvariable=self.channel, **width25_c)
        channel_CB['values'] = ('MATH2', 'CH1', 'CH2')
        cursor1_E = ttk.Entry(frame, textvariable=self.cursor1, **width25_c)
        cursor2_E = ttk.Entry(frame, textvariable=self.cursor2, **width25_c)
        channel_CB.grid(row=11, column=2, **x4y3)
        cursor1_E.grid(row=12, column=2, padx=6, pady=3, sticky='w')
        cursor2_E.grid(row=13, column=2, padx=6, pady=3, sticky='w')

        cursor1_units = ttk.Label(frame, text='MHz', **h10bL_r)
        cursor2_units = ttk.Label(frame, text='MHz', **h10bL_r)
        cursor1_units.grid(row=12, column=3, **x4y3w)
        cursor2_units.grid(row=13, column=3, **x4y3w)

        sep3 = ttk.Separator(frame, orient=h)
        sep3.grid(row=14, column=1, columnspan=3, padx=5, pady=10, sticky='ew')
        # __________________________________________________________________________________________
        cursormax_L = ttk.Label(frame, text='Intensity Max.', **label_fmt)
        acqs_L = ttk.Label(frame, text='Acquisitions', **label_fmt)
        cursormax_L.grid(row=15, column=1, **x4y3)
        acqs_L.grid(row=16, column=1, **x4y3)

        cursormax = ttk.Label(frame, textvariable=self.cursormax, style='h10.TLabel')
        acqs = ttk.Label(frame, textvariable=self.numavgs, style='h10.TLabel')
        cursormax.grid(row=15, column=2, **x4y3)
        acqs.grid(row=16, column=2, **x4y3)

        cursormax_units = ttk.Label(frame, text='mV', **h10bL_r)
        acqs_units = ttk.Label(frame, text='FIDs', **h10bL_r)
        cursormax_units.grid(row=15, column=3, **x4y3w)
        acqs_units.grid(row=16, column=3, **x4y3w)
        # __________________________________________________________________________________________
        conn_B = ttk.Button(frame, text='Connect', **h8bB_width8, command=self.get_settings)
        run = ttk.Button(
            buttons_frame, text='Run', **h8bB_width10, command=lambda: self.run(feedback=True))
        stop = ttk.Button(buttons_frame, text='Stop', **h8bB_width10, command=self.stop)
        save = ttk.Button(buttons_frame, text='Save', **h8bB_width7, command=self.save_fid)
        clear = ttk.Button(buttons_frame, text='Clear', **h8bB_width10, command=self.clear)
        conn_B.grid(row=1, column=0, **x4y3w)
        run.grid(row=0, column=1, padx=4)
        stop.grid(row=0, column=2, padx=4)
        clear.grid(row=0, column=3, padx=4)
        save.grid(row=0, column=4, padx=4)

    def connect(self):
        """
        Establish connection with Tek DPO73304. Query oscilloscope for running state. 
        Update connection status and running state.
        """
        scope = OscilloscopeDriver()
        self.conn.configure(text='Connected', foreground='green3')

        run_state = int(scope.run_state)
        if run_state == 1:
            self.state_L.configure(text='Running', foreground='green3')
        else:
            self.state_L.configure(text='Stopped', foreground='red')
        return scope

    def recall_setup(self):
        """ 
        Recall previously saved setup located on oscilloscope hard drive with *.set extension. 
        """
        scope = self.connect()
        scope.recall_setup(ScopeController.setup_dict[self.setup.get()])
        self.get_settings()

    def get_settings(self):
        """ Connect to oscilloscope. Query scope for current settings and update GUI. """
        scope = self.connect()
        run_state = int(scope.run_state)
        if run_state == 0:
            self.state_L.configure(text='Stopped', foreground='red')
        elif run_state == 1:
            self.state_L.configure(text='Running', foreground='green3')
        self.channel.set(str(scope.data_source))
        self.acq_t.set(str(int(float(scope.acq_duration) * 1E6)))
        self.delay_t.set(str(int(float(scope.horizontal_delay) * 1E6)))
        self.sr.set(str(int(float(scope.sampling_rate) * 1E-9)))
        self.math2_mem.set(str(int(float(scope.math2_memory) * 8)))
        self.cursor1.set(str(int(float(scope.cursor1_pos) * 1E-6)))
        self.cursor2.set(str(int(float(scope.cursor2_pos) * 1E-6)))
        self.cursormax.set(str(float(scope.cursor_max)))
        self.numavgs.set(str(int(scope.numavgs)))

    def send_settings(self):
        """ Send settings from GUI to scope. """
        scope = self.connect()
        scope.data_source = self.channel.get()
        scope.acq_duration = '{:.6f}'.format(float(self.acq_t.get()) * 1E-6)
        scope.horizontal_delay = '{:.6f}'.format(float(self.delay_t.get()) * 1E-6)
        scope.sampling_rate = '{:.0f}'.format(int(self.sr.get()) * 1E9)
        scope.math2_memory = str(math.ceil(float(self.math2_mem.get())) / 8)
        scope.cursor1_pos = '{:.0f}'.format(float(self.cursor1.get()) * 1E6)
        scope.cursor2_pos = '{:.0f}'.format(float(self.cursor2.get()) * 1E6)

    def get_numavgs_and_cursormax(self):
        """ Query scope for the number of FIDs recorded. Update self.numavgs and self.cursormax. """
        scope = self.connect()
        num_avgs = scope.numavgs
        cursormax = scope.cursor_max
        self.numavgs.set(num_avgs)
        self.cursormax.set(cursormax)
        return num_avgs

    def run(self, feedback=True):
        """
        Begin data acquisition. Monitor FID count and max intensity between cursors on a dedicated 
        thread. If automated spectral collection is running, monitoring thread is not started.

        Parameters:
            feedback (bool):
                If true, FID count and max intensity monitored on GUI.
        """
        self.event.clear()
        scope = self.connect()
        scope.send_data_transfer_defaults()
        self.send_settings()
        scope.run()
        self.state_L.configure(
            text='Running', foreground='green3', font=('Helvetica', '10', 'bold'))
        # REMOVING FIXED THE PROBLEM
        def thread_func():
            while not self.event.is_set():
                time.sleep(1)
                self.get_numavgs_and_cursormax()
            # self.state_L.configure(text='Stopped', foreground='red', font=('Helvetica', '10', 'bold'))
        for thread in threading.enumerate():
            if thread.name == 'auto_run':
                feedback = False
        if feedback:
            t = Thread(name='scope run', target=thread_func)
            t.start()

    def stop(self):
        """ End data acquisition. Terminate self.event thread. """
        self.event.set()
        scope = self.connect()
        scope.stop()
        self.state_L.configure(text='Stopped', foreground='red')

    def save_fid(self, fname=None):
        """ Save waveform data to file with name of your choosing. """
        if fname is None:
            fname = page_funcs.save_file(ftype='.txt', defaultextension='.txt')
        else:
            fname = fname
        scope = self.connect()
        if not self.event.is_set():
            self.stop()
        fid = scope.get_waveform()
        np.savetxt(fname, fid, fmt='%s')

    def clear(self):
        """ Clear all data from oscilloscope and update GUI. """
        scope = self.connect()
        scope.clear()
        time.sleep(0.5)
        self.connect()
        # Repeat to return 0 acquisitions to the GUI. Otherwise, max intensity is reset, but # acqs. is not.
        time.sleep(0.5)
        self.connect()
        self.get_numavgs_and_cursormax()
        # self.get_cursormax()
