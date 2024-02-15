"""
Author: Channing West
Changelog: 11/17/2020
"""
import numpy as np
import pyvisa as visa
import pandas as pd
from tkinter.messagebox import askokcancel

IP = 'TCPIP::169.254.246.32'
TIMEOUT = 5000
INTERLEAVE = 1
ZEROING = 1
SAMPLING_RATE = 24000000000
RUN_MODE = 'TRIG'
CLOCK_SOURCE = 'INT'
REF_SOURCE = 'EXT'


class AWGDriver:
    """
    Control Tektronix AWG 7122 over LAN connection using TCP/IP and SCPI commands.
    See Programmer's manual for more info on accepcted SCPI commands.

    Parameters:
        ip (str):
            AWG IP address
            Default: None
        timeout (int):
            Communication timeout.
            Units: ms
            Default: None
        interleave (int):
            Interleave CH1 and CH2 for higher sampling rate.
            Default: None
        zeroing (int):
            Zeroing control.
            Default: None
        sampling_rate (int):
            Waveform sampling rate.
            Units: Samples/second
            Default: None
        run_mode (str):
            Run mode: CONTiunous or TRIGgered
            Default: None
        clock_source (str):
            Clock source: INTernal or EXTernal
            Default: None
        ref_source (str):
            Clock reference source: INTernal or EXTernal
            Default: None
    Attributes:
        self._ip (str):
            AWG IP address
            Default: TCPIP::169.254.246.32
        self._timeout (int):
            Communication timeout.
            Units: ms
            Default: 5000
        self._interleave (int):
            Interleave CH1 and CH2 for higher sampling rate.
            Default: 1
        self._zeroing (int):
            Zeroing control.
            Default: 1
        self._sampling_rate (int):
            Waveform sampling rate.
            Units: Samples/second
            Default: 24000000000
        self._run_mode (str):
            Run mode: CONTiunous or TRIGgered
            Default: TRIG
        self._clock_source (str):
            Clock source: INTernal or EXTernal
            Default: INT
        self._ref_source (str):
            Clock reference source: INTernal or EXTernal
            Default: EXT
        self.rm (visa.ResourceManager object):
            visa.ResourceManager() instance
        self.open_awg (self.rm.open_resource(self._ip) object):
            Open connection between AWG and PC. Use self.open_awg to query AWG and
            send settings to the AWG.
        self._idn (str):
            Return value of '*IDN?' query. Instrument identification.
        self._waveform (str):
            File name of the active waveform
        self._ch1_output (int):
            State of CH1: 0 or 1
            Must be 1 for waveform output
    Methods:
        getter and setter methods for attributes.
        run_check()
            Warn user if important settings do not match expected values.
        run()
            Start waveform output if self.run_check() passes.
        stop()
            Stop waveform output.
        import_waveform(fname)
            Load *.txt waveform file from AWG hard drive into AWG application.
        import_setup(fname)
            Load 'fname.awg' AWG setup file from AWG hard drive into AWG application.
        active_waveform(fname)
            Switch active waveform to fname.
        close()
            Close connection to AWG.
    """

    def __init__(self, ip=None, timeout=None, interleave=None, zeroing=None, sampling_rate=None,
                 run_mode=None, clock_source=None, ref_source=None):
        self._ip = IP if ip is None else ip
        self._timeout = TIMEOUT if timeout is None else timeout
        self._interleave = INTERLEAVE if interleave is None else interleave
        self._zeroing = ZEROING if zeroing is None else zeroing
        self._sampling_rate = SAMPLING_RATE if sampling_rate is None else sampling_rate
        self._run_mode = RUN_MODE if run_mode is None else run_mode
        self._clock_source = CLOCK_SOURCE if clock_source is None else clock_source
        self._ref_source = REF_SOURCE if ref_source is None else ref_source

        self.rm = visa.ResourceManager()
        self.open_awg = self.rm.open_resource(self._ip)
        self.open_awg.timeout = self._timeout

        self.open_awg.write('AWGControl:INTerleave %s' % self._interleave)
        self.open_awg.write('AWGControl:INTerleave:ZERoing %s' % self._zeroing)
        self.open_awg.write('SOURCE1:FREQUENCY %s' % self._sampling_rate)
        self.open_awg.write('AWGControl:RMODe %s' % self._run_mode)
        self.open_awg.write('AWGControl:CLOCk:SOURce %s' % self._clock_source)
        self.open_awg.write('SOURCE1:ROSCillator:SOURCE %s' % self._ref_source)

        self._idn = self.open_awg.query('*IDN?')
        self._interleave = self.open_awg.query('AWGControl:INTerleave?')
        self._zeroing = self.open_awg.query('AWGControl:INTerleave:ZERoing?')
        self._sampling_rate = self.open_awg.query('SOURCE1:FREQUENCY?')
        self._run_mode = self.open_awg.query('AWGControl:RMODe?')
        self._clock_source = self.open_awg.query('AWGControl:CLOCk:SOURce?')
        self._ref_source = self.open_awg.query('SOURCE1:ROSCillator:SOURCE?')
        self._waveform = self.open_awg.query('SOURce1:WAVeform?')
        self._ch1_output = self.open_awg.query('OUTPUT1:STATE?')

    @property
    def ch1_output(self):
        """ _ch1_output getter """
        return self._ch1_output
    @ch1_output.setter
    def ch1_output(self, state):
        """ _ch1_output setter. State of CH1: 0 or 1. """
        self.open_awg.write('OUTPUT1:STATE %s' % state)
        self._ch1_output = self.open_awg.query('OUTPUT1:STATE?')

    @property
    def idn(self):
        """ _idn getter. """
        return self._idn

    @property
    def interleave(self):
        """ _interleave getter """
        return self._interleave.strip()
    @interleave.setter
    def interleave(self, val):
        """ _interleave setter. ON = 1, OFF = 0 """
        self.open_awg.write('AWGControl:INTerleave %s' % val)
        self._interleave = self.open_awg.query('AWGControl:INTerleave?')

    @property
    def zeroing(self):
        """ _zeroing getter """
        return self._zeroing.strip()
    @zeroing.setter
    def zeroing(self, val):
        """ _zeroing setter. ON = 1, OFF = 0 """
        self.open_awg.write('AWGControl:INTerleave:ZERoing %s' % val)
        self._zeroing = self.open_awg.query('AWGControl:INTerleave:ZERoing?')

    @property
    def sampling_rate(self):
        """ _sampling_rate getter """
        return int(float(self._sampling_rate.strip()))
    @sampling_rate.setter
    def sampling_rate(self, val):
        """ _sampling_rate setter. Samples/second. """
        self.open_awg.write('SOURCE1:FREQUENCY %s' % val)
        self._sampling_rate = self.open_awg.query('SOURCE1:FREQUENCY?')

    @property
    def run_mode(self):
        """ _run_mode getter """
        return self._run_mode.strip()
    @run_mode.setter
    def run_mode(self, mode):
        """
        _run_mode setter. Default: TRIGgered.
        Options: CONTinuous|TRIGgered|GATed|SEQuence|ENHanced
        """
        self.open_awg.write('AWGControl:RMODe %s' % mode)
        self._run_mode = self.open_awg.query('AWGControl:RMODe?')

    @property
    def clock_source(self):
        """ _clock_source getter """
        return self._clock_source.strip()
    @clock_source.setter
    def clock_source(self, source):
        """ _clock_source setter. Default: EXTernal. Options: EXTernal|INTernal """
        self.open_awg.write('AWGControl:CLOCk:SOURce %s' % source)
        self._clock_source = self.open_awg.query('AWGControl:CLOCk:SOURce?')

    @property
    def ref_source(self):
        """ _ref_source getter """
        return self._ref_source.strip()
    @ref_source.setter
    def ref_source(self, source):
        """ _ref_source setter. Default: EXTernal. Options: EXTernal|INTernal """
        self.open_awg.write('SOURCE1:ROSCillator:SOURCE %s' % source)
        self._clock_source = self.open_awg.query('SOURCE1:ROSCillator:SOURCE?')

    @property
    def waveform(self):
        """ waveform getter """
        return self._waveform.strip()
    @waveform.setter
    def waveform(self, fname):
        """ waveform setter. """
        self.open_awg.write('SOURce1:WAVeform "%s"' %fname)
        self._waveform = self.open_awg.query('SOURce1:WAVeform?')

    def run_check(self):
        """ Warn user if important settings do not match expected values."""
        unexpected = []
        if not self.zeroing:
            unexpected.append(' zeroing')
        if not self.interleave:
            unexpected.append(' interleave')
        if float(self.sampling_rate) != 24E9:
            unexpected.append(' sample rate')
        if self.run_mode != 'TRIG':
            unexpected.append(' run mode')
        if self.clock_source != 'INT':
            unexpected.append(' clock source')
        if self.ref_source != 'EXT':
            unexpected.append(' reference source')

        if unexpected:
            err_msg = 'Unexpected AWG setting(s): '
            for x in unexpected:
                err_msg = err_msg + str(x) + ','
            err_msg = err_msg + '.\nProceeding could result in harm to the instrument. ' \
                                'Would you like to proceed?'
            if askokcancel('AWG Unexpected Settings', message=err_msg):
                self.zeroing = 1
                self.interleave = 1
                self.sampling_rate = 24E9
                self.run_mode = 'TRIGgered'
                self.clock_source = 'INTernal'
                self.ref_source = 'EXTernal'

    def run(self):
        """ Start waveform output if self.run_check() passes. """
        self.run_check()
        self.open_awg.write('AWGControl:RUN')

    def stop(self):
        """ Stop waveform output. """
        self.open_awg.write('AWGControl:STOP')

    def import_waveform(self, fname):
        """ Load *.txt waveform file from AWG hard drive into AWG application. """
        self.open_awg.write('MMEMory:IMPort %s' % fname)

    def import_setup(self, fname):
        """ Load 'fname.awg' AWG setup file from AWG hard drive into AWG application. """
        self.open_awg.write('AWGControl:SREStore "%s"' % fname)

    def active_waveform(self, fname):
        """
        Switch active waveform to fname.

        The active waveform is the output of the AWG when running. fname must be loaded
        using import_waveform() before it can be set to the active waveform.
        """
        self.stop()
        self.waveform = fname

    def close(self):
        """ Close connection to AWG. """
        self.open_awg.close()


# i = AWGDriver()  # ip='TCPIP::169.254.246.32')  #ip='TCPIP0::169.254.246.32::INSTR')
#i.import_setup("C:\\Documents and Settings\\OEM\\Desktop\\Standard_Chirps_Setup_2020.awg")
#i.import_setup("C:\\Documents and Settings\\OEM\\Desktop\\Setup1.awg")

class Waveform:
    """
    Load and characterize linear chirp waveform file, like those used on Tektronix AWG7122B.

    Not intended for waveforms other than broadband linear chirps.

    Parameters:
        file (str):
            Path to *.txt file containing waveform and markers in 3 column array.
        sample_rate (int):
            Waveform sample rate.
            Units: samples/second
    Attributes:
        self.sample_rate (int):
            Waveform sampling rate.
            Units: samples/second
        self.waveform (np.array):
            Single column array. Waveform amplitude.
        self.marker1 (np.array):
            Single column array. Marker leading waveform. TTL signal.
        self.marker2 (np.array):
            Single column array. Marker trailing waveform. TTL signal.
        self.wf_switches (list):
            Array indices immediately before and immediately after linear chirp.
        self.m1_switches (list):
            First and last TTL high indices.
        self.m2_switches (list):
            First and last TTL high indices.
        self.chirp_width (float):
            Chirp duration.
            Units: seconds
        self.chirp_delay (float):
            Time before first linear chirp begins.
            Units: seconds
        self.m1_width (float):
            Marker1 duration.
            Units: seconds
        self.m2_width (float):
            Marker2 duration.
            Units: seconds
        self.m1_buffer (float):
            Time between end of marker1 and beginning of waveform.
            Units: seconds
        self.m2_buffer (float):
            Time between end of waveform and beginning of marker2.
            Units: seconds
        self.end_buffer (float):
            Time between end of marker2 and end of frame and beginning of next frame.
    Methods:
        chirp_on()
            Return array of indices immediately before all linear chirps.
        chirp_off()
            Return array of x indices immediately after all linear chirps.
        m1_low_to_high()
            Return array of first indices when marker1 TTL goes high.
        m1_high_to_low()
            Return array of last indices before marker2 TTL goes low.
        m2_low_to_high()
            Return array of first indices when marker2 TTL goes high.
        m2_high_to_low()
            Return array of last x indices before marker2 TTL goes low.
    """
    def __init__(self, file, sample_rate):
        file_array = np.array(pd.read_csv(file, sep='\t', header=None))
        self.sample_rate = sample_rate
        self.waveform = file_array[:, 0]
        self.marker1 = file_array[:, 1]
        self.marker2 = file_array[:, 2]
        self.wf_switches = []
        self.m1_switches = []
        self.m2_switches = []

        for x in range(len(self.marker1)-1):
            if self.waveform[x] != 0.:
                try:
                    if self.waveform[x - 1] == 0. and self.waveform[x + 1] != 0:
                        self.wf_switches.append(x - 1)
                    if self.waveform[x - 1] != 0. and self.waveform[x + 1] == 0:
                        self.wf_switches.append(x + 1)
                except IndexError:
                    pass
            if self.marker1[x] != self.marker1[x+1]:
                if self.marker1[x] != 0:
                    self.m1_switches.append(x)
                else:
                    self.m1_switches.append(x + 1)
            if self.marker2[x] != self.marker2[x+1]:
                if self.marker2[x] != 0:
                    self.m2_switches.append(x)
                else:
                    self.m2_switches.append(x + 1)

        chirp_on = np.array(self.wf_switches[::2])
        chirp_off = np.array(self.wf_switches[1::2])
        self.chirp_width = np.round((chirp_off - chirp_on) / self.sample_rate, decimals=11)
        if len(set(self.chirp_width)) == 1:
            self.chirp_width = self.chirp_width[0]
        self.chirp_delay = chirp_on[0] / self.sample_rate

        m1_low_to_high = np.array(self.m1_switches[::2])
        m1_high_to_low = np.array(self.m1_switches[1::2]) + 1
        self.m1_width = np.round(
            (m1_high_to_low - m1_low_to_high) / self.sample_rate, decimals=11)[0]
        self.m1_buffer = np.round((chirp_on - m1_high_to_low) / self.sample_rate, decimals=11)[0]

        m2_low_to_high = np.array(self.m2_switches[::2])
        m2_high_to_low = np.array(self.m2_switches[1::2]) + 1
        self.m2_width = np.round(
            (m2_high_to_low - m2_low_to_high) / self.sample_rate, decimals=11)[0]
        self.m2_buffer = np.round((m2_low_to_high - chirp_off) / self.sample_rate, decimals=11)[0]

        x = (chirp_on[1]/self.sample_rate)
        y = (m2_high_to_low[0]/self.sample_rate)
        self.end_buffer = x - y - self.chirp_delay

    def chirp_on(self):
        """ Return array of indices immediately before all linear chirps. """
        c_on = np.array(self.wf_switches[::2])
        return c_on

    def chirp_off(self):
        """ Return array of indices immediately after all linear chirps. """
        c_off = np.array(self.m1_switches[1::2]) + 1
        return c_off

    def m1_low_to_high(self):
        """ Return array of first indices when marker1 TTL goes high. """
        m1_L2H = np.array(self.m1_switches[::2])
        return m1_L2H

    def m1_high_to_low(self):
        """ Return array of last indices before marker2 TTL goes low. """
        m1_H2L = np.array(self.m1_switches[1::2]) + 1
        return m1_H2L

    def m2_low_to_high(self):
        """ Return array of first indices when marker2 TTL goes high. """
        m2_L2H = np.array(self.m2_switches[::2])
        return m2_L2H

    def m2_high_to_low(self):
        """ Return array of last indices before marker2 TTL goes low. """
        m2_H2L = np.array(self.m2_switches[1::2]) + 1
        return m2_H2L

    def transfer_to_awg(self):
        pass


def linear_chirp(sample_rate, freq_start, freq_stop, chirp_length):
    """
    Return linear frequency sweep.

    Parameters:
        sample_rate (int):
            Waveform sample rate.
            Units: samples/second
        freq_start (float):
            Starting frequency.
            Units: Hz.
        freq_stop (float):
            Ending frequency.
            Units: Hz.
        chirp_length (float):
            Chirp duration.
            Units: seconds
    Return:
        chirp (np.array):
            Single column array. Linear frequency sweep.
    """
    len_chirp = sample_rate * chirp_length
    chirp = np.linspace(0, chirp_length, len_chirp)
    chirp_squared = chirp ** 2
    first_term = 2 * np.pi * freq_start * chirp
    second_term = 2 * np.pi * (freq_stop - freq_start) * (chirp_squared / (2 * chirp_length))
    chirp = np.sin(first_term + second_term)
    chirp = np.reshape(chirp, (len(chirp), 1))
    return chirp


def generate_waveform(sample_rate, freq_start, freq_stop, chirp_duration,
                      delay=None, m1_buffer=None, m2_buffer=None, m1_duration=None,
                      m2_duration=None, end_buffer=None, num_frames=None):
    """
    Generate broadband chirps.

    Parameters:
        sample_rate (int):
            Waveform sampling rate.
            Units: samples/second
        freq_start (float):
            Starting frequency.
            Units: Hz.
        freq_stop (float):
            Ending frequency.
            Units: Hz.
        chirp_duration (float):
            Chirp duration.
            Units: seconds
        delay (float):
            Time before chirp begins.
            Units: seconds
            Default: 1.5E-6 + (4.E-6 - chirp_duration)
        m1_duration (float):
            Marker1 duration.
            Units: seconds
            Default: 1.0E-6
        m2_duration (float):
            Marker2 duration.
            Units: seconds
            Default: 1.0E-6
        m1_buffer (float):
            Time between end of marker1 and beginning of linear chirp.
            Units: seconds
            Default: 0.5E-6
        m2_buffer (float):
            Time between end of linear chirp and beginning of marker2.
            Units: seconds
            Default: 0.5E-6
        end_buffer (float):
            Time between end of marker2 and end of frame and/or beginning of next frame.
            Units: seconds
            Default: 45.0E-6
        num_frames (int):
            Number of identical frames stacked back to back.
            Default: 8
    Return
        wf (array):
            Three column array.
            col[0] -> waveform. col[1] -> marker1. col[2] -> marker2.
    """
    if delay is None:
        delay = 1.5E-6 + (4.E-6 - chirp_duration)
    else:
        delay = delay + (4.E-6 - chirp_duration)
    if m1_buffer is None:
        m1_buffer = 0.5E-6
    if m2_buffer is None:
        m2_buffer = 0.5E-6
    if m1_duration is None:
        m1_duration = 1.0E-6
    if m2_duration is None:
        m2_duration = 1.0E-6
    if end_buffer is None:
        end_buffer = 45.0E-6
    if num_frames is None:
        num_frames = 8
    delay_num_rows = delay * sample_rate
    m1_buffer_num_rows = m1_buffer * sample_rate
    m2_buffer_num_rows = m2_buffer * sample_rate
    m1_duration_num_rows = m1_duration * sample_rate
    m2_duration_num_rows = m2_duration * sample_rate
    end_buffer_num_rows = end_buffer * sample_rate

    t_single_frame = (delay + chirp_duration + m2_buffer + m2_duration + end_buffer)
    num_rows_single_frame = t_single_frame * sample_rate

    t_full_wf = round(t_single_frame * num_frames, 11)
    num_rows_full_wf = int(t_full_wf * sample_rate)

    wf = np.zeros((num_rows_full_wf, 3))
    chirp = linear_chirp(sample_rate, freq_start, freq_stop, chirp_duration)

    for f in range(0, num_frames):
        frame_mult = f * num_rows_single_frame

        chirp_row_start = int(delay_num_rows + frame_mult)
        chirp_row_stop = int(chirp_row_start + len(chirp))

        m1_row_start = int(chirp_row_start - m1_buffer_num_rows - m1_duration_num_rows)
        if m1_row_start < 2400:
            m1_row_start = 2400
        m1_row_stop = int(chirp_row_start - m1_buffer_num_rows)
        if m1_row_stop < 26400:
            m1_row_stop = 26400

        m2_row_start = int(chirp_row_stop + m2_buffer_num_rows)
        m2_row_stop = int(m2_row_start + m2_duration_num_rows)

        wf[chirp_row_start: chirp_row_stop, 0] = chirp[:, 0]
        m1 = np.ones((m1_row_stop - m1_row_start, 1))
        m2 = np.ones((m2_row_stop - m2_row_start, 1))
        wf[m1_row_start: m1_row_stop, 1] = m1[1]
        wf[m2_row_start: m2_row_stop, 2] = m2[1]
    return wf

# import matplotlib.pyplot as plt
# f = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\2.0_8.0_GHz_chirp_1000.0ns_length_string_of_8.txt'
# chirp = Waveform(f, 24000000000)
# plt.plot(chirp.waveform)
# plt.plot(chirp.wf_switches, chirp.waveform[chirp.wf_switches], 'o')
# # plt.plot(chirp.marker1)
# # plt.plot(chirp.m1_switches, chirp.marker1[chirp.m1_switches], 'o')
# # plt.plot(chirp.marker2)
# # plt.plot(chirp.m2_switches, chirp.marker2[chirp.m2_switches], 'o')
# plt.show()
# # print(chirp.wf_switches, chirp.m1_switches, chirp.m2_switches, '\n\n',
#       chirp.chirp_width, chirp.chirp_delay, chirp.m1_width, chirp.m1_buffer, chirp.end_buffer)