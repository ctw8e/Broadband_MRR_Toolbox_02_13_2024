"""
Author: Channing West
Changelog: 5/21/2022
"""

import numpy as np
import pyvisa as visa
from tkinter.messagebox import askokcancel

IP = 'TCPIP::169.254.27.62'  # 'TCPIP0::169.254.27.62::inst0::INSTR'
TIMEOUT = 10000
DATA_SOURCE = 'MATH2'
DATA_FORMAT = 'ASCI'
FRAME_START = 9
FRAME_STOP = 9
DATA_START = 1
DATA_STOP = 1000000
DELAY = 3.0E-6

SAMPLE_RATE_2_8 = 25E9
ACQ_TIME_2_8 = 40E-6
CURSOR1_POS_2_8 = 2000E6
CURSOR2_POS_2_8 = 8000E6
MATH1_CENTER_2_8 = 5E9
MATH1_SPAN_2_8 = 6E9

SAMPLE_RATE_6_18 = 50E9
ACQ_TIME_6_18 = 20E-6
CURSOR1_POS_6_18 = 6000E6
CURSOR2_POS_6_18 = 18000E6
MATH1_CENTER_6_18 = 12.5E9
MATH1_SPAN_6_18 = 25E9


class OscilloscopeDriver:
    """
    Control Tektronix DPO 73304 over LAN connection using TCP/IP and SCPI commands.
    See Programmer's manual for more info on accepcted SCPI commands.

    Parameters:
        ip (str):
            Oscilloscope IP address.
            Default: None
        timeout (int):
            Communication timeout.
            Units: ms
            Default: None
    Attributes:
        self._ip (str):
            Oscilloscope IP address.
            Default: 'TCPIP::169.254.27.62'
        self._timeout (int):
            Communication timeout.
            Units: ms
            Default: 10000
        self.rm (visa.ResourceManager object):
            visa.ResourceManager() object
        self.open_scope (self.rm.open_resource(self._ip) object):
            Open connection between scope and PC. Use self.open_scope to query oscilloscope and
            send settings to the oscilloscope.
        self._idn (str):
            Return value of '*IDN?' query. Instrument identification.
        self._run_state (str):
            Running state: RUN or STOP
        self._numavgs (int):
            Number of FastFrame FID acquisitions signal averaged.
        self._acq_duration (float):
            FID acquisition time.
            Units: seconds
            Default 2-8 GHz: 40E-6
            Default 6-18 GHz: 20E-6
        self._sampling_rate (int):
            Waveform sampling rate.
            Units: (samples/second)
            Default 2-8 GHz: 25E9
            Default 6-18 GHz: 50E9
        self._horizontal_delay (float):
            Time between trigger and start of FID acquisition.
            Units: seconds
            Default: 3.0E-6
        self._data_source (str):
            Data channel transferred from oscilloscope to PC when a CURVe? query is executed.
            Options: CH1, CH2, CH3, CH4, MATH1, MATH2
                CH1: Not used
                CH2: 2-8 GHz input
                CH3: 6-18 GHz input
                CH4: Not used
                MATH1: Rough Fourier Transform shown on oscilloscope.
                MATH2: Signal averaged FID (from either CH1 or CH2)
            Default: 'MATH2'
        self._data_format (str):
            Options: ASCIi, FAStest, RIBinary, RPBinary, FPBinary, SRIbinary, SRPbinary, SFPbinary
            Default: 'ASCI'
        self._frame_start (int):
            Frames 1-8 are unique and frame 9 is the average of frames 1-8.
            Default: 9
        self._frame_stop (int):
            Frames 1-8 are unique and frame 9 is the average of frames 1-8.
            Default: 9
        self._data_start (int):
            Starting index of waveform when waveform is queried.
            Default: 1
        self._data_stop (int):
            Ending index of waveform when waveform is queried.
            Default: 1000000
        self._math2_memory (int):
            1/8 the number of FID acquisitions held in memory.
        self._math1_center (int):
            Center frequency of the Math1 channel, which is the FFT, on scope display.
            Units: Hz
            Default 2-8 GHz: 5E9
            Default 6-18 GHz: 12.5E9
        self._math1_span (int):
            Frequency span of the Math1 channel, which is the FFT, on scope display.
            Units: Hz
            Default 2-8 GHz: 6E9
            Default 6-18 GHz: 25E9
        self._cursor1_pos (float):
            vertical cursor position.
            Units: Hz
            Default 2-8 GHz: 2000E6
            Default 6-18 GHz: 6000E6
        self._cursor2_pos (float):
            vertical cursor position.
            Units: Hz
            Default 2-8 GHz: 8000E6
            Default 6-18 GHz: 18000E6
        self._cursor_max (float):
            Intensity of the strongest signal observed between self._cursor1_pos and
            self._cursor2_pos.
            Units: mV
    Methods:
        getter and setter methods for attributes.
        recall_setup(fname)
            Load previously saved oscilloscope setup. Switch between 2-8 GHz and 6-18 GHz setups.
        send_instsetup_defaults(setup)
            Load settings for particular spectral region (2-8 GHz or 6-18 GHz).
        send_data_transfer_defaults()
            Load settings that are not specific to a spectral region.
        run_check()
            Check if important settings match expected values. Warn user of inconsistencies.
        run()
            Set oscilloscope state to run, starting data collection.
        stop()
            Set oscilloscope run state to stop, ending/pausing data collection.
        clear()
            Clear data from oscilloscope.
        get_waveform()
            Return waveform from oscilloscope.
        close()
            Close connection between oscilloscope and controller.
    """
    def __init__(self, ip=None, timeout=None):
        self._ip = ip if ip is not None else IP
        self._timeout = timeout if timeout is not None else TIMEOUT

        self.rm = visa.ResourceManager()
        self.open_scope = self.rm.open_resource(self._ip)
        self.open_scope.timeout = self._timeout

        self._idn = self.open_scope.query('*IDN?')

        self._run_state = self.open_scope.query('ACQuire:STATE?')
        self._numavgs = self.open_scope.query('ACQuire:NUMFRAMESACQuired?')

        self._acq_duration = self.open_scope.query('HORizontal:ACQDURATION?')
        self._sampling_rate = self.open_scope.query('HORizontal:MODe:SAMPLERate?')
        self._horizontal_delay = self.open_scope.query('HORIZONTAL:DELAY:TIME?')

        self._data_source = self.open_scope.query('DATa:SOUrce?')
        self._data_format = self.open_scope.query('DATa:ENCdg?')
        self._frame_start = self.open_scope.query('DATa:FRAMESTARt?')
        self._frame_stop = self.open_scope.query('DATa:FRAMESTOP?')
        self._data_start = self.open_scope.query('DATa:STARt?')
        self._data_stop = self.open_scope.query('DATa:STOP?')

        self._math2_memory = self.open_scope.query('MATH2:NUMAVg?')
        self._math1_center = self.open_scope.query('MATH1:SPECTral:CENTER?')
        self._math1_span = self.open_scope.query('MATH1:SPECTral:SPAN?')

        self._cursor1_pos = self.open_scope.query('CURSor:VBArs:POS1?')
        self._cursor2_pos = self.open_scope.query('CURSor:VBArs:POS2?')
        self._cursor_max = self.open_scope.query('MEASUrement:MEAS1:MAXimum?')

    @property
    def run_state(self):
        """ Return running state of the oscilloscope. ON = 1 = RUN, OFF = 0 = STOP. """
        return self._run_state.strip()

    @run_state.setter
    def run_state(self, val):
        """ Set running state of the oscilloscope. ON = 1 = RUN, OFF = 0 = STOP. """
        self.open_scope.write('ACQuire:STATE %s' % val)
        self._run_state = self.open_scope.query('ACQuire:STATE?')

    @property
    def math1_center(self):
        """ Return center frequency of Math1 channel, which is the FFT shown on the scope. """
        return self._math1_center.strip()

    @math1_center.setter
    def math1_center(self, freq):
        """ Set the center frequency of the Math1 channel, which is the FFT shown on the scope. """
        self.open_scope.write('MATH1:SPECTral:CENTER %s' % freq)
        self._math1_center = self.open_scope.query('MATH1:SPECTral:CENTER?')

    @property
    def math1_span(self):
        """ Return the frequency span of the Math1 channel, which is the FFT shown on the scope. """
        return self._math2_center.strip()

    @math1_span.setter
    def math1_span(self, freq):
        """ Set the frequency span of the Math1 channel, which is the FFT shown on the scope. """
        self.open_scope.write('MATH2:SPECTral:SPAN %s' % freq)
        self._math2_center = self.open_scope.query('MATH2:SPECTral:SPAN?')

    @property
    def idn(self):
        """ _idn getter. Return the identity of the oscilloscope."""
        return self._idn.strip()

    @property
    def sampling_rate(self):
        """ _sampling_rate getter. Return sampling rate."""
        return self._sampling_rate.strip()

    @sampling_rate.setter
    def sampling_rate(self, rate):
        """
        _sampling_rate setter. Set sampling rate.

        Use 'MATH1:SPECTral:CENTER 5E9' and 'MATH1:SPECTral:SPAN 6E9' with
        'HORizontal:MODe:SAMPLERate 25E9'

        Use 'MATH1:SPECTral:CENTER 12.5E9' and 'MATH1:SPECTral:SPAN 25E9' with
        'HORizontal:MODe:SAMPLERate 50E9'

        Parameters:
            rate (int):
                Sampling rate
                Units: (samples/second)
        """
        self.open_scope.write('HORizontal:MODe:SAMPLERate %s' % rate)
        self._sampling_rate = self.open_scope.query('HORizontal:MODe:SAMPLERate?')

    @property
    def acq_duration(self):
        """ _acq_duration getter. Return duration of FID acquisition. """
        return self._acq_duration.strip()

    @acq_duration.setter
    def acq_duration(self, time):
        """
        _acq_duration setter. Set duration of FID acquisition.
        Units: seconds
        """
        self.open_scope.write('HORizontal:ACQDURATION %s' % time)
        self._acq_duration = self.open_scope.query('HORizontal:ACQDURATION?')

    @property
    def data_source(self):
        """ _data_source getter. Return the data channel transferred with a CURVe? query. """
        return self._data_source.strip()

    @data_source.setter
    def data_source(self, source):
        """
         _data_source setter. Return the data channel transferred with a CURVe? query.
         Options:
            CH1, CH2, CH3, CH4, MATH1, MATH2
         """
        self.open_scope.write('DATa:SOUrce %s' % source)
        self._data_source = self.open_scope.query('DATa:SOUrce?')

    @property
    def data_format(self):
        """ _data_format getter """
        return self._data_format.strip()

    @data_format.setter
    def data_format(self, fmt):
        """
        _data_format setter.
        Options:
            ASCIi|FAStest|RIBinary|RPBinary|FPBinary|SRIbinary|SRPbinary|SFPbinary
        """
        self.open_scope.write('DATa:ENCdg %s' % fmt)
        self._data_format = self.open_scope.query('DATa:ENCdg?')

    @property
    def frame_start(self):
        """
        _frame_start getter. Nine total frames collected.
        Frames 1-8 are unique and frame 9 is a summary frame.
        """
        return self._frame_start.strip()

    @frame_start.setter
    def frame_start(self, frame):
        """
        _frame_start setter. Options: 1-9.
        Frames 1-8 are unique and frame 9 is a summary frame of 1-8.
        """
        self.open_scope.write('DATa:FRAMESTARt %s' % frame)
        self._frame_start = self.open_scope.query('DATa:FRAMESTARt?')

    @property
    def frame_stop(self):
        """
        _frame_stop getter. Nine total frames collected.
        Frames 1-8 are unique and frame 9 is a summary frame.
        """
        return self._frame_stop.strip()

    @frame_stop.setter
    def frame_stop(self, frame):
        """
        _frame_stop setter.
        Options: 1-9. Frames 1-8 are unique and frame 9 is a summary frame of 1-8.
        """
        self.open_scope.write('DATa:FRAMESTOP %s' % frame)
        self._frame_stop = self.open_scope.query('DATa:FRAMESTOP?')

    @property
    def data_start(self):
        """ _data_start getter """
        return self._data_start.strip()

    @data_start.setter
    def data_start(self, num):
        """ _data_start setter. Options: counting numbers """
        self.open_scope.write('DATa:STARt %s' % num)
        self._data_start = self.open_scope.query('DATa:STARt?')

    @property
    def data_stop(self):
        """ _data_stop getter """
        return self._data_stop.strip()

    @data_stop.setter
    def data_stop(self, num):
        """ _data_stop setter. Options: counting numbers """
        self.open_scope.write('DATa:STOP %s' % num)
        self._data_stop = self.open_scope.query('DATa:STOP?')

    @property
    def math2_memory(self):
        """
        _math2_memory getter.
        Return a value that represents 1/8 the number of FID acquisitions held in memory.
        """
        return self._math2_memory.strip()

    @math2_memory.setter
    def math2_memory(self, num):
        """
        _math2_memory setter.
        Number should be at least one eighth desired number of acquisitions.
        """
        self.open_scope.write('MATH2:NUMAVg %s' % num)
        self._math2_memory = self.open_scope.query('MATH2:NUMAVg?')

    @property
    def horizontal_delay(self):
        """
        _horizontal_delay getter.
        Time between trigger pulse and start of waveform acquisition.
        Units: seconds.
        """
        return self._horizontal_delay.strip()

    @horizontal_delay.setter
    def horizontal_delay(self, time):
        """ _horizontal_delay setter. Units: seconds. """
        self.open_scope.write('HORIZONTAL:DELAY:TIME %s' % time)
        self._horizontal_delay = self.open_scope.query('HORIZONTAL:DELAY:TIME?')

    @property
    def cursor1_pos(self):
        """ _cursor1_pos getter. Position of cursor 1 on Math1. Units: Hz """
        return self._cursor1_pos.strip()

    @cursor1_pos.setter
    def cursor1_pos(self, freq):
        """ _cursor1_pos setter. Position of cursor 1 on Math1. Units: Hz. """
        freq = float(freq)  # * 1E6
        self.open_scope.write('CURSor:VBArs:POS1 %s' % freq)
        self._cursor1_pos = self.open_scope.query('CURSor:VBArs:POS1?')

    @property
    def cursor2_pos(self):
        """ _cursor2_pos getter. Position of cursor 2 on Math1. Units: Hz """
        return self._cursor2_pos.strip()

    @cursor2_pos.setter
    def cursor2_pos(self, freq):
        """ _cursor2_pos setter. Position of cursor 2 on Math1. Units: Hz. """
        freq = float(freq)  # * 1E6
        self.open_scope.write('CURSor:VBArs:POS2 %s' % freq)
        self._cursor2_pos = self.open_scope.query('CURSor:VBArs:POS2?')

    @property
    def numavgs(self):
        """ Return the number of FastFrame FID acquisitions. """
        self._numavgs = self.open_scope.query('ACQuire:NUMFRAMESACQuired?')
        return self._numavgs.strip()

    @property
    def cursor_max(self):
        """
        _cursor_max getter. Return the maximum intensity found between the cursors.
        Units: mV
        """
        self._cursor_max = self.open_scope.query('MEASUrement:MEAS1:MAXimum?')
        return self._cursor_max.strip()

    def recall_setup(self, fname):
        """
        Load previously saved oscilloscope setup.
        Use to switch between 2-8 GHz and 6-18 GHz instrument setups.

        Parameters:
            fname (str):
                setup file name.
        """
        self.open_scope.write('RECAll:SETUp "%s"' % fname)
        self.send_data_transfer_defaults()

    def send_instsetup_defaults(self, setup):
        """
        Send default settings that vary depending on the spectral region being observed.

        Parameters:
            setup (str):
                '2to8' or '6to18'
        """
        self.horizontal_delay = DELAY
        if setup == '2to8':
            self.sampling_rate = SAMPLE_RATE_2_8
            self.math1_center = MATH1_CENTER_2_8
            self.math1_span = MATH1_SPAN_2_8
            self.cursor1_pos = CURSOR1_POS_2_8
            self.cursor2_pos = CURSOR2_POS_2_8
            self.acq_duration = ACQ_TIME_2_8

        elif setup == '6to18':
            self.sampling_rate = SAMPLE_RATE_6_18
            self.math1_center = MATH1_CENTER_6_18
            self.math1_span = MATH1_SPAN_6_18
            self.cursor1_pos = CURSOR1_POS_6_18
            self.cursor2_pos = CURSOR2_POS_6_18
            self.acq_duration = ACQ_TIME_6_18

    def send_data_transfer_defaults(self):
        """ Send default settings that are consistent for the two different spectral regions. """
        self.data_source = DATA_SOURCE
        self.data_format = DATA_FORMAT
        self.frame_start = FRAME_START
        self.frame_stop = FRAME_STOP
        self.data_start = DATA_START
        self.data_stop = DATA_STOP

    def run_check(self):
        """
        Check if important settings match expected values. If they do not, warn the user before
        proceeding.
        """
        unexpected = []
        if self.data_source != DATA_SOURCE:
            unexpected.append(' data source,')
        if float(self.horizontal_delay) != DELAY:
            unexpected.append(' horizontal delay,')
        if float(self.sampling_rate) == 25E9:
            if float(self.acq_duration) != 40E-6:
                unexpected.append(' acquisition duration or sample rate,')
        elif float(self.sampling_rate) == 50E9:
            if float(self.acq_duration) != 20E-6:
                unexpected.append(' acquisition duration or sample rate,')
        if self.data_format != str(DATA_FORMAT):
            unexpected.append(' data format,')
        if self.frame_start != str(FRAME_START):
            unexpected.append(' starting frame,')
        if self.frame_stop != str(FRAME_STOP):
            unexpected.append(' ending frame,')
        if self.data_start != str(DATA_START):
            unexpected.append(' starting data point,')
        if self.data_stop != str(DATA_STOP):
            unexpected.append(' ending data point,')

        if unexpected:
            err_msg = 'Unexpected oscilloscope setting(s): '
            for x in unexpected:
                err_msg = err_msg + str(x)
            err_msg = err_msg + \
                      '.\nProceeding could result in data loss or harm to the instrument.'\
                      '\nWould you like to proceed?'
            if askokcancel('Oscilloscope Unexpected Settings', message=err_msg):
                return True
            else:
                return False
        else:
            return True

    def run(self):
        """ Set oscilloscope state to run, starting data collection. """
        check = self.run_check()
        if check:
            self.run_state = 'RUN'

    def stop(self):
        """ Set oscilloscope run state to stop, ending/pausing data collection. """
        self.run_state = 'STOP'

    def clear(self):
        """ Clear waveform from oscilloscope. """
        self.open_scope.write('CLEAR ALL')

    def get_waveform(self):
        """
        Return waveform from oscilloscope.

        Returns:
            intensity_array (np.array):
                1-D array of FID.
        """
        intensity = self.open_scope.query('CURVe?').strip().split(',')
        intensity_array = np.array(intensity).reshape((len(intensity), 1))
        return intensity_array

    def close(self):
        """ Close connection between oscilloscope and controller. """
        self.open_scope.close()


# instance = OscilloscopeDriver()
# print(instance.idn,
#       instance.data_source,
#       instance.data_start,
#       instance.data_stop,
#       instance.frame_start,
#       instance.frame_stop,
#      instance.sampling_rate,
#      instance.cursor_max,
#      instance.acq_duration,
#      instance.cursor1_pos,
#      instance.cursor2_pos,
#      instance.horizontal_delay,
#      instance.math2_memory,
#      instance.numavgs)
