"""
Author: Channing West
Changelog: 12/23/2020
"""

from Instrument_Drivers.Oscilloscope_Driver import OscilloscopeDriver
import Instrument_Drivers.Oscilloscope_Driver as scope_driver
from Instrument_Drivers.AWG_Driver import AWGDriver
import Instrument_Drivers.AWG_Driver as awg_driver

from Instrument_Drivers.Temp_Cont_Driver import TemperatureController
import Instrument_Drivers.Temp_Cont_Driver as temp_driver
# from tkinter.messagebox import askokcancel, askyesnocancel, showerror
# from tkinter import simpledialog
from threading import Thread
import time
import glob
import numpy as np
import scipy
import os


def auto_save_fid(directory=None, scope=None, sample_name=None, inst_setup=None, save_every=None,
                  temp=None, chirp=None, pressure=None):
    """
    Transfer FID waveform from oscilloscope to PC controller and save.

    Parameters:
        directory (str):
            path to folder containing the time-domain file.
        sample_name (str):
            name of the chemical compound
        inst_setup (str):
            Setup of the broadband instrument.
            Either 2to8 or 6to18.
        save_every (int):
            Number of FID averages the file represents.
        temp (int):
            Nozzle temperature.
            Units: Celsius
        chirp (int):
            Duration of the microwave chirp.
            Units: microseconds
        pressure (int):
            Backing pressure.
            Units: psig
        scope (OscilloscopeDriver):
            OscilloscopeDriver object can be given to communicate with the scope over a
            pre-existing connection.
    Returns:
          fname (str):
              File name.

    Waveform saved in desired directory and named according to the convention shown below.
    {pickett_dir}\{time}_{sample}_{setup}_{# FIDs}k_{temp}C_{chirp dur}us_{pressure}psig_.{ext}
        pickett_dir: directory
        time: Time stamp of when file is saved. %H_%M_%S
        sample: sample_name. Name of the chemical compound
        setup: inst_setup. Either 2to8 or 6to18.
        # FIDS: Number of FIDs averaged to generate waveform.
        temp: temp. Nozzle temperature. Units: Celsius.
        chirp dur: chirp. Duration of the microwave chirp. Units: microseconds.
        pressure: pressure. Backing pressure. Units: psig.
        ext: file extension. *.txt
    """
    if directory is None:
        directory = 'C:\\ROT'
    if scope is None:
        scope = OscilloscopeDriver()
    if sample_name is None:
        raise ValueError('Must provide sample_name.')
    if inst_setup is None:
        raise ValueError('Must provide inst_setup.')
    if save_every is None:
        raise ValueError('Must provide save_every.')
    if temp is None:
        raise ValueError('Must provide temp')
    if chirp is None:
        raise ValueError('Must provide chirp.')
    if pressure is None:
        raise ValueError('Must provide pressure.')

    avg_k = int(save_every / 1000)

    fname = '{t}_{name}_{setup}_{avg}k_{temp}C_{chirp}us_{pressure}psig_{ext}'
    fname = fname.format(
        t=time.strftime('%H_%M_%S'), name=sample_name, setup=inst_setup, avg=avg_k, temp=temp,
        chirp=chirp, pressure=pressure, ext='.txt')

    os.chdir(directory)
    np.savetxt(fname, scope.get_waveform(), fmt='%s')


def auto_save_fft(directory=None, sr=None, ff=None, kb=None, trl=None, fstart=None, fstop=None):
    """
    Open the newest FID in 'directory' and calculate FFT. Save FFT as *.ft file.

    Parameters:
        directory (str):
            directory containing time-domain file.
        ff (float):
            fraction of FID used to generate FFT.
            Between 0 and 1.
        kb (float):
            Kaiser-Bessel window parameter.
        trl (int):
            Total record length, including zero-padding.
            Units: microseconds.
        sr (int):
            Oscilloscope sampling rate.
            Units: GSa./sec.
        fstart (float):
            FFT lower bound frequency.
            Units: MHz.
        fstop (float):
            FFT upper bound frequency.
            Units: MHz.
    Returns:
        fft (array):
            FFT. Frequencies and intensities.
            Units: MHz and mV
    """
    if directory is None:
        directory = 'C:\\ROT'
    if sr is None:
        raise ValueError(
            'Sampling rate must be provided (GSa./s). For the 2-8 GHz instrument setup, '
            '25 GSa./s is typical, and 50 GSa./s is typical for the 6-18 GHz setup.')
    if ff is None:
        ff = 1
    if kb is None:
        kb = 9.5
    if trl is None:
        trl = 80
    if fstart is None:
        if sr == 25:
            fstart = 2000
        elif sr == 50:
            fstart = 6000
    if fstop is None:
        if sr == 25:
            fstop = 6000
        elif sr == 50:
            fstop = 18000

    cwd_file_list = glob.glob(directory + '/*.txt')
    newest_file = max(cwd_file_list, key=os.path.getctime)
    waveform = os.path.join(directory, newest_file)
    fid_fname = os.path.basename(waveform)
    fid_fname = os.path.splitext(fid_fname)[0]
    fft_fname = '{fname}_FF{ff}_KB{kb}_TRL{zpl}_{ext}'
    fft_fname = fft_fname.format(
        fname=fid_fname, ff=str(round(ff * 10)), kb=str(round(kb * 10)), zpl=str(round(trl)),
        ext='.ft')

    sr = sr * 1E9
    fid = []
    with open(waveform, 'r') as f:
        for row in f:
            fid.append(float(row.split()[-1]))
    fid = np.array(fid)

    # ________________________________time_domain_fraction__________________________
    halfway_index = round(len(fid) * ff)
    partial_fid = fid[0:halfway_index]

    # _______________________________kaiser_filering________________________________
    kaiser = np.kaiser(halfway_index, kb)
    window_function = np.multiply(partial_fid, kaiser)

    # _________________________________zero_padding_________________________________
    num_data_points = round(trl * 1E-6 * sr)
    zp_fid = np.zeros((num_data_points,))
    zp_fid[0:len(window_function)] = window_function

    fft = scipy.fftpack.fft(zp_fid) / 100
    freq = scipy.fftpack.fftfreq(len(zp_fid), d=(1 / sr)) / 1E6

    freqs = []
    ft_magnitude = []
    for i, row in enumerate(freq):
        if fstart <= row <= fstop:
            freqs.append('%.4f' % row)
            ft_magnitude.append(abs(fft[i]))

    fft = np.column_stack((freqs, ft_magnitude))
    os.chdir(directory)
    np.savetxt(fft_fname, fft, fmt='%s', delimiter=' ')
    # return fft


def single(save_every, scope=None, perform_fft=True, **kwargs):
    """
    Collect a single spectrum.

    Start oscilloscope waveform acquisition. Monitor number of FIDs collected until > save_every.
    Stop waveform acquisition. Save FID waveform to PC controller using auto_save_fid(). Clear
    FID waveform from the scope. Perform optional FFT using perform_fft()

    Parameters:
        save_every (int):
            Number of waveforms acquired before saving FID.
        scope:
            Instance of OscilloscopeDriver()
        perform_fft (bool):
            If True, FFT is calculated and saved
        kwargs: for auto_save_fid() and auto_save_fft()
            auto_save_fid: directory, scope, sample_name, inst_setup, save_every, temp, chirp,
                pressure
            auto_save_fft:  directory, sr, ff, kb, trl, fstart, fstop
    """
    if scope is None:
        scope = OscilloscopeDriver()
    scope.run()
    time.sleep(0.5)
    while scope.numavgs < save_every:
        time.sleep(0.5)
    scope.stop()
    auto_save_fid(save_every=save_every, scope=scope, **kwargs)
    scope.clear()
    if perform_fft:
        auto_save_fft(**kwargs)


def continuous(event, save_every, scope=None, perform_fft=True, **kwargs):
    """
    Collect spectra until interupted.

    Start oscilloscope waveform acquisition. Monitor number of FIDs collected until > save_every.
    Stop waveform acquisition. Save FID waveform to PC controller using auto_save_fid(). Clear
    FID waveform from the scope. Perform optional FFT using perform_fft(). Restart Oscilloscope
    waveform acquisition. When interrupted, stop waveform acquisition.

    Parameters:
        event:
            instance of Thread.Event()
        save_every (int):
            Number of waveforms acquired before saving FID waveform.
        scope:
            Instance of OscilloscopeDriver()
        perform_fft (bool):
            If True, FFT is calculated and saved
        kwargs: for auto_save_fid() and auto_save_fft()
            auto_save_fid: directory, scope, sample_name, inst_setup, save_every, temp, chirp,
                pressure
            auto_save_fft: directory, sr, ff, kb, trl, fstart, fstop
    """
    if scope is None:
        scope = OscilloscopeDriver()
    scope.run()
    time.sleep(0.5)
    while not event.is_set():
        while scope.numavgs < int(save_every):
            time.sleep(0.5)
        scope.stop()
        auto_save_fid(save_every=save_every, scope=scope, **kwargs)
        scope.clear()
        scope.run()
        if perform_fft:
            auto_save_fft(**kwargs)
    scope.stop()


def temperature_sequence(sequence, save_every, scope=None, **kwargs):
    """ Incomplete. """
    # todo
    # sequence = self.archive_temp_seq.get().split(',')
    for x in range(len(sequence)):
        sequence[x] = int(sequence[x])
    temps = np.arange(sequence[0], sequence[1] + sequence[2], sequence[2])

    for x in range(len(temps)):
        tc1, tc2, tc3 = TemperatureController()  # self.connect_temp_cont()
        tc1.write_setpoint_value(temps[x])
        tc2.write_setpoint_value(temps[x])
        tc3.write_setpoint_value(temps[x])

        if x == 0:  # todo
            self.archive_check_temp_tolerance(tolerance=3)

        scope.run()
        while scope.numavgs < int(save_every):  # self.archive_save_every):
            time.sleep(0.5)
    scope.stop()


def chirp_sequence(sequence, save_every, scope=None, awg=None, **kwargs):
    pass  # todo
