"""
Author: Channing West
Changelog: 12/5/2019, 2/1/2020

"""

import numpy as np
import math
import scipy
import scipy.signal
import os
import pandas as pd
# import Spectrum_Operations
from itertools import groupby
from operator import itemgetter

np.set_printoptions(edgeitems=20)


class FID:
    """
    Class for time domain free induction decay data.

    Accepted file types include: *.txt
        Default edtension of raw time data is *.txt

    Default parameters of this class reflect the most common parameters used in the Pate Group,
    25 GSa/sec 2-8 GHz, 50 GSa/sec 6-18 GHz.

    Attributes:
        fname (str): file path.
        fid (array):
            Single column array. col[0] -> electric field.
            May be 2 column array if older files are used.
            col[0] -> time, col[1] -> electric field.
        srate (int):
            sampling rate.
            Units: Samples/second
            Default: 25E9
        point_spacing (float):
            time spacing between samples.
            Units: MHz.
        ff_fid (array):
            Holds array after running gate().
            Default: None
        ff_kb_fid (array):
            Holds array after running kaiser_window().
            Default: None
        ff_kb_zp_fid (array):
            Holds array after running zeropad().
            Default: None
    Methods:
        add_time_column(fid, total_time, units)
            Returns 2 column array. col[0] -> time, col[1] -> electric field.
        gate(frac, fid)
            Returns a partial FID.
        kaiser_window(kb, fid, abs_norm)
            Returns array of FID filtered using a Kaiser-Bessel window.
        zeropad(fid, total_time, units))
            Returns array of the FID with zeropadding.
        gate_kaiser_zeropad(kw)
            Functions as a wrapper for gate(), kaiser_window(), and zeropad().
        fft(fid, fstart, fstop, full_ft)
            Performs a fast Fourier transform on a FID.
        quick_fft(frac, kb, total_time, units, fstart, fstop, full_ft)
            Full FID processing (gate, window filter, zeropad, fft) without creating copies at
            each step.
        time_column_fid(units):
            Add time column to self.fid. Useful for graphing.
        time_column_ff_fid(units):
            Add time column to self.ff_fid. Useful for graphing.
        time_column_ff_kb_fid(units):
            Add time column to self.ff_kb_fid. Useful for graphing.
        time_column_ff_kb_zp_fid(units):
            Add time column to self.ff_kb_zp_fid. Useful for graphing.
    """

    def __init__(self, file, srate=None):
        self.fname = file
        ext = os.path.splitext(file)[1]
        if ext == '.txt':
            self.fid = pd.read_csv(file, sep='\n', header=None).values
            # Following 4 lines for old file format, with header and time column already appended.
            if type(self.fid[0][0]) == str:
                for x in range(len(self.fid)):
                    new_x = float(self.fid[x][0].split('\t')[-1])
                    self.fid[x] = new_x
            if srate is None:
                self.srate = 25E9
            elif srate == 25:
                self.srate = 25E9
            elif srate == 50:
                self.srate = 50E9
            else:
                self.srate = srate
            self.point_spacing = 1 / (self.srate * 1E6)
            self.fid_time = len(self.fid) / self.srate
            self.ff_fid = None
            self.ff = None
            self.ff_kb_fid = None
            self.ff_kb_abs_fid = None
            self.kb = None
            self.ff_kb_zp_fid = None
            self.zp = None

    def gate(self, frac=None, time_column=False):
        """
        set self.ff_fid to a portion of the total FID, starting from the beginning of the FID.

        Parameters:
            frac (float):
                Fraction of the FID to keep. Value between 0 and 1.
                Default:  1.
            time_column (bool):
                Add time column to self.ff_fid
                Units: microseconds
                Default: False
        """
        if frac is None:
            frac = 1
        fid = self.fid[:, -1]
        fid = fid[0:(round(len(fid) * frac))]
        self.ff_fid = np.reshape(fid, newshape=(len(fid), 1))
        self.ff = frac
        if time_column:
            self.time_column_ff_fid()

    def kaiser_window(self, kb=None, abs_norm=True, time_column=False):
        """
        Set self.ff_kb_fid to array of FID filtered using a Kaiser-Bessel window.

        If abs_norm = True, set self.ff_kb_abs_fid to the absolute valued and normalized
        Kaiser-Bessel filtered FID.

        If self.ff_fid == None, set self.ff = 1 and apply Kaiser window to self.fid.

        Parameters:
            kb (float):
                Kaiser-Bessel window parameter.
                Default:  9.5.
            abs_norm (bool):
                If True, an array of the normalized absolute value filtered FID is returned.
                Default:  True.
            time_column (bool):
                Add time column to self.ff_kb_fid
                Units: microseconds
                Default: False
        """
        if self.ff_fid is None:
            fid_initial = self.fid[:, -1].flatten()
            self.ff = 1
        else:
            fid_initial = self.ff_fid[:, -1].flatten()
        if kb is None:
            kb = 9.5
        kaiser_window = np.kaiser(len(fid_initial), kb)
        fid = np.multiply(kaiser_window, fid_initial)
        self.ff_kb_fid = fid
        if abs_norm:
            abs_norm_kaiser = np.abs(fid)
            abs_norm_kaiser = abs_norm_kaiser / abs_norm_kaiser.max()
            self.ff_kb_abs_fid = abs_norm_kaiser
        if time_column:
            self.time_column_ff_kb_fid()

    def zeropad(self, total_time=None, units='usec', time_column=False):
        """
        Set self.ff_kb_zp_fid to array of the FID with zeropadding.

        If self.ff_kb_fid == None, run self.kaiser_window() with default params.

        Parameters:
            total_time (float):
                Total time, FID plus zeropadding.
                Units: microseconds.
                Default:  80
            units (str):
                'usec' or 'sec'.
                Default:  'usec'.
            time_column (bool):
                Add time column to self.ff_kb_fid
                Units: microseconds
                Default: False
        """
        if self.ff_kb_fid is None:
            self.kaiser_window()
        else:
            fid = self.ff_kb_fid
        if total_time is None:
            total_time = 80
        if units == 'usec':
            self.zp = total_time
            total_time = total_time * 1E-6
        point_num = round(total_time * self.srate)
        zp_fid = np.zeros((point_num,))
        zp_fid[:len(fid)] = fid
        self.ff_kb_zp_fid = zp_fid
        if time_column:
            self.time_column_ff_kb_zp_fid()

    def gate_kaiser_zeropad(self, frac=None, kb=None, total_time=None):
        """
        Combination of gate(frac), kaiser_window(kb), and zeropad(total_time).

        gate() uses raw FID.
        kaiser_window() uses result of gate().
        zeropad() uses result of kaiser_window().

        Parameters:
            frac (float):
                Fraction of FID.
                Default: None
            kb (float):
                Kaiser-Bessel window parameter.
                Default:  None
            total_time (float):
                Total time, FID plus zeropadding.
                Units: microseconds
                Default:  None
        """
        self.gate(frac=frac)
        self.kaiser_window(kb=kb, abs_norm=True)
        self.zeropad(total_time=total_time)

    def fft(self, fstart=None, fstop=None, full_ft=False):
        """
        Calculate the fast Fourier transform of a FID.

        Complete FID filtering if not done already.

        Parameters:
            fstart (int):
                Starting frequency of the fft.
                 Units: MHz.
                 Default:  2000
            fstop (int):
                Stopping frequency of the fft.
                Units: MHz.
                Default:  8000
            full_ft (bool):
                If True, real and imaginary. If False, magnitude.
                Default: False
        Returns:
            fft (array):
                2 or 3 column array.
                Col[0] -> frequency
                Col[1] -> magnitude or real
                Col[2] -> imaginary
        """
        if self.ff_kb_zp_fid is None:
            self.zp = 0
            if self.ff_kb_fid is None:
                self.kaiser_window()
            fid = self.ff_kb_fid
        else:
            fid = self.ff_kb_zp_fid
        if fstart is None:
            fstart = 2000
        if fstop is None:
            fstop = 8000

        fft = scipy.fftpack.fft(fid) / 100
        freq = (scipy.fftpack.fftfreq(len(fid), d=(1 / self.srate))) / 1E6

        fid_time = len(fid) / self.srate
        freq_res = round((1 / fid_time * 1E-6), 4)

        index_start = int(round((fstart - freq[0]) / freq_res))
        index_stop = int(round((fstop - freq[0]) / freq_res))

        freqs = freq[index_start:index_stop]
        if full_ft:
            ft_real = fft[index_start:index_stop].real
            ft_imag = fft[index_start:index_stop].imag
            fft = np.column_stack((freqs, ft_real, ft_imag))
        else:
            ft_mag = np.abs(fft[index_start:index_stop])
            fft = np.column_stack((freqs, ft_mag))
        return fft

    def quick_fft(self, frac=None, kb=None, total_time=None, fstart=None, fstop=None,
                  full_ft=False, units='usec'):
        """
        Full FID processing (gate, window filter, zeropad, fft) without creating copies at each step.

        Does not create array copies that would be created using gate(), kaiser_window(),
        and zeropad() individually. These array copies are useful for visualization but are
        memory intensive. This method is faster and should be used for automated data archiving
        where the instrument is still consuming sample while the data is being saved and processed.

        Parameters:
            frac (float):
                Fraction of the FID to keep. Value between 0 and 1.
                Default:  1.
            kb (float):
                Kaiser-Bessel window parameter.
                Default:  9.5.
            total_time (float):
                Total time, FID plus zeropadding.
                Units: microseconds
                Default:  80
            units (str):
                'usec' or 'sec'.
                Default:  'usec'.
            fstart (int):
                Starting frequency of the fft
                Units: MHz.
                Default:  2000.
            fstop (int):
                Stopping frequency of the fft
                Units: MHz.
                Default:  8000.
            full_ft (bool):
                if True, real and imaginary. If False, magnitude.
                Default:  False.
        Returns:
            fft (array):
                Shape:
                    If full_ft == True:
                        (((fstop - fstart) * point_spacing) , 3)
                        col[0] -> frequency
                        col[1] -> real
                        col[2] -> imaginary
                    If full_ft == False:
                        (((fstop - fstart) * point_spacing) , 2)
                        Col[0] -> frequency
                        Col[1] -> magnitude
        """
        if frac is None:
            frac = 1
        if kb is None:
            kb = 9.5
        if total_time is None:
            total_time = 80
        if units == 'usec':
            total_time = total_time * 1E-6
        if fstart is None:
            fstart = 2000
        if fstop is None:
            fstop = 8000
        partial_len = round(len(self.fid) * frac)
        try:
            if self.fid.shape[1] == 2:
                fid = self.fid[0:partial_len, -1]
        except IndexError:
            pass
        fid = self.fid
        fid = fid.flatten()

        window_filter = np.multiply(fid[0:partial_len], np.kaiser(partial_len, kb))

        point_num = round(total_time * self.srate)
        fid = np.zeros((point_num,))
        fid[0:len(window_filter)] = window_filter

        signal = scipy.fftpack.fft(fid) / 100
        freq = (scipy.fftpack.fftfreq(len(fid), d=(1 / self.srate))) / 1E6

        fid_time = len(fid) / self.srate
        freq_res = round((1 / fid_time * 1E-6), 4)
        len_arr = int((fstop - fstart) * len(fid) / (self.srate * 1E-6))
        index_start = int(round((fstart - freq[0]) / freq_res))
        index_stop = int(round((fstop - freq[0]) / freq_res))
        freqs = freq[index_start:index_stop]
        if full_ft:
            fft = np.zeros((len_arr, 3))
            fft[:, 0] = freqs
            fft[:, 1] = signal[index_start:index_stop].real
            fft[:, 2] = signal[index_start:index_stop].imag
        else:
            fft = np.zeros((len_arr, 2))
            fft[:, 0] = freqs
            fft[:, 1] = np.absolute(signal[index_start:index_stop])
        return fft

    def time_column_fid(self, units='usec'):
        """
        Add time column to self.fid. Useful for graphing.

        col[0] -> time,
        col[1] -> electric field.

        Parameters:
            units (str):
                Units: 'usec' or 'sec'.
                Default:  'usec' (microseconds)
        """
        if self.fid.shape[1] == 2:
            return
        if units == 'usec':
            t_final = (1 / self.srate) * len(self.fid) * 1E6
            srate = self.srate * 1E-6
        elif units == 'sec':
            t_final = (1 / self.srate) * len(self.fid)
            srate = self.srate
        time_fid = np.zeros((len(self.fid), 2))
        time_fid[:, 0] = np.arange(0, t_final, 1 / srate)
        time_fid[:len(self.fid), 1] = self.fid.transpose()
        self.fid = time_fid

    def time_column_ff_fid(self, units='usec'):
        """
        Add time column to self.ff_fid. Useful for graphing.

        col[0] -> time,
        col[1] -> electric field.

        Parameters:
            units (str):
                Units: 'usec' or 'sec'.
                Default:  'usec' (microseconds)
        """
        if self.ff_fid.shape[1] == 2:
            return
        if units == 'usec':
            t_final = (1 / self.srate) * len(self.ff_fid) * 1E6
            srate = self.srate * 1E-6
        elif units == 'sec':
            t_final = (1 / self.srate) * len(self.ff_fid)
            srate = self.srate
        time_fid = np.zeros((len(self.ff_fid), 2))
        time_fid[:, 0] = np.arange(0, t_final, 1 / srate)
        time_fid[:len(self.ff_fid), 1] = self.ff_fid.transpose()
        self.ff_fid = time_fid

    def time_column_ff_kb_fid(self, units='usec'):
        """
        Add time column to self.ff_kb_fid. Useful for graphing.

        col[0] -> time,
        col[1] -> electric field.

        Parameters:
            units (str):
                Units: 'usec' or 'sec'.
                Default:  'usec' (Microseconds)
        """
        if self.ff_kb_fid.shape[1] == 2:
            return
        if units == 'usec':
            t_final = (1 / self.srate) * len(self.ff_kb_fid) * 1E6
            srate = self.srate * 1E-6
        elif units == 'sec':
            t_final = (1 / self.srate) * len(self.ff_kb_fid)
            srate = self.srate
        time_fid = np.zeros((len(self.ff_kb_fid), 2))
        time_fid[:, 0] = np.arange(0, t_final, 1 / srate)
        time_fid[:len(self.ff_kb_fid), 1] = self.ff_kb_fid.transpose()
        self.ff_kb_fid = time_fid
        time_fid[:len(self.ff_kb_abs_fid), 1] = self.ff_kb_abs_fid.transpose()
        self.ff_kb_abs_fid = time_fid

    def time_column_ff_kb_zp_fid(self, units='usec'):
        """
        Add time column to self.ff_kb_zp_fid. Useful for graphing.

        col[0] -> time,
        col[1] -> electric field.

        Parameters:
            units (str):
                Units: 'usec' or 'sec'
                Default:  'usec' (Microseconds)
        """
        if self.ff_kb_zp_fid.shape[1] == 2:
            return
        if units == 'usec':
            t_final = (1 / self.srate) * len(self.ff_kb_zp_fid) * 1E6
            srate = self.srate * 1E-6
        elif units == 'sec':
            t_final = (1 / self.srate) * len(self.ff_kb_zp_fid)
            srate = self.srate
        time_fid = np.zeros((len(self.ff_kb_zp_fid), 2))
        time_fid[:, 0] = np.arange(0, t_final, 1 / srate)
        time_fid[:len(self.ff_kb_zp_fid), 1] = self.ff_kb_zp_fid.transpose()
        self.ff_kb_zp_fid = time_fid


# file = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Ethylbenzene\\Christoffers\\CoAdd_christoffers_ethylbenzene_30uL_RS_TFIP_2to8_100k_25C_2us_50in_10outpsig_.txt'

def simulate_spectrum(peak_list, freq_min=None, freq_max=None, step_size=None, fwhm=None,
                      scale_factor=None, save=False, fname=None):
    """
    Simulate spectrum using the peak list.

    Parameters:
        peak_list (array):
            Two column array of peak positions and intensities.
            col[0] -> freq
            col[1] -> intensity.
        freq_min (float):
            Starting frequency of the simulation.
            Units: MHz
            Default: 2000
        freq_max (float):
            Stopping frequency of the simulation.
            Units: MHz
            Default: 8000
        step_size (float):
            Point spacing.
            Units: MHz
            Default: 0.0125
        fwhm (float):
            Line width.
            Units: MHz
            Default: 0.060
        scale_factor (float):
            scale factor applied to the y-axis.
            Default: None
        save (bool):
            Option to save output to external file.
        fname(str):
            file name, if save=True.
    Return:
        simulation (array):
            Two column array.
            col[0] -> freq
            col[1] -> intensity
    """
    if freq_min is None:
        freq_min = 2000
    if freq_max is None:
        freq_max = 8000
    if step_size is None:
        step_size = 0.0125
    if fwhm is None:
        fwhm = 0.060
    hwhm = fwhm / 2

    num_points = round(((freq_max + step_size) - freq_min) / step_size)
    sim = np.zeros((int(num_points), 2))
    sim[:, 0] = np.linspace(freq_min, freq_max, num_points)

    freqs_intens = np.array(
        [peak_list[x, :] for x in range(len(peak_list)) if freq_min < peak_list[x, 0] < freq_max])

    row_start = np.floor(((freqs_intens[:, 0] - 4 * hwhm) - freq_min) / step_size)
    row_stop = np.ceil(((freqs_intens[:, 0] + 4 * hwhm) - freq_min) / step_size)

    for x in range(len(freqs_intens)):
        line = []
        rstart = row_start[x]
        rstop = row_stop[x] + 1
        rows = np.arange(rstart, rstop, 1)
        freqs = rows * step_size + freq_min
        for f in freqs:
            G = math.exp((((f - freqs_intens[x, 0]) / hwhm) ** 2) * (-1 * math.log(2)))
            line.append(freqs_intens[x, 1] * G)
        try:
            sim[int(rows[0]):int(rows[-1] + 1), 1] = line
        except ValueError:
            pass
    sim[:, 1] = np.real(sim[:, 1])

    if scale_factor is not None:
        sim[:, 1] = sim[:, 1] * scale_factor
    if save:
        np.savetxt(str(fname) + '_Simulation.prn', sim, fmt=['%.4f', '%.5e'])
    return sim


def build_matrix(*args):
    """
    Build matrix of spectra in a shared frequency region, keeping a single frequency column.

    col[0] -> frequency. col[1] -> spectral signal of the first spectrum.
    Subsequent columns contain the spectral signals of other spectra. In order to use this function,
    all spectra passed as *args need to be over the same frequency region.

    Parameters:
        args (array):
            Spectra. Two col each [freq, int].
    Return:
        matrix (array): col[0] -> frequency column.
                        Each subsequent col is the spectral intensity for a single spectrum.
    """
    first_spec = Spectrum(args[0][0]).spectrum
    freq = first_spec[:, 0]
    matrix = freq
    fnames = []
    for arg in args[0]:
        fnames.append(arg)
        spec = Spectrum(arg).spectrum
        matrix = np.column_stack((matrix, spec[:, 1]))
    return fnames, matrix


class Spectrum(FID):
    """
    Class for rotational spectra.

    Accepted file types include: *.ft, *.prn, and *.txt
        - Default extension of experimental spectra is *.ft
        - Default extension of simulated spectra is *.prn
        - Default edtension of raw time data is *.txt
        - Class inherits from FID class, so if a *.txt file is passed as the file arg,
            an FFT of the file is performed and used as the spectrum. Be sure to pass the
            relevant **kwargs for the fft if you want params other than the defaults.

    Many default parameters of this class reflect the most common frequency region we work with
    in the Pate Group, 2-8 GHz.

    Parameters:
        file (str):
            file path
        cols (list of int):
            columns to extract from file.
            Default: None
    Attributes:
        fname (str):
            file path
        spectrum (array):
            col[0] -> frequency
            col[1] -> intensity spec 1
            col[2...] intnesity spec 2...
        point_spacing (float):
            point spacing along the frequency axis.
            Units: MHz
        freq_min (float):
            minimum frequency.
            Units: MHz
        freq_max (float):
            maximum frequency.
            Units: MHz
        max_intensity (float):
            highest point in the spectrum.
            Units: mV
    Methods:
        freq_to_row(freq)
            Return the closest row number associated with freq.
        row_to_freq(row)
            Return the frequency associated with the row.
        get_intensity(freq, spec_num)
            Return the intensity of the spectrum at freq.
        spectrum_dictionary(spec_num)
            Return spectrum as a dictionary using frequencies as keys and intensities as vals.
        peak_pick(thresh, dyn_range, sort, spec_num)
            Perform a peak pick on the spectrum.
        peak_pick_sequence_measurement(matrix, thresh)
            Perform a peak pick on matrix of multiple spectra.
        simulate_peak_pick(thresh, dyn_rang, freq_min, freq_max, step_size, fwhm,
        scale_factor, spec_num)
            Perform a peak pick on the spectrum and produce a simulation of the peak pick, which
            removes noise.
        get_rows(freqs, matrix)
            Return section of overall spectrum corresponding to frequencies provided.
        signal_max(freqs, matrix, delta_freq, mode)
            Given a matrix of spectra, find the spectrum with most intensity at the given
            frequency +/- delta_freq.
        normalize_transition(freq)
            Use with spectra matrix. Normalize transition intensity across columns of the matrix.
    """

    def __init__(self, file, cols=None, **kwargs):
        self.fname = file
        ext = os.path.splitext(file)[1]
        if ext in ['.ft', '.prn']:
            self.spectrum = pd.read_csv(file, sep=' ', header=None, usecols=cols).values
        elif ext == '.txt':
            fid = FID(file)
            fid.gate_kaiser_zeropad(**kwargs)
            self.spectrum = fid.fft(fid, **kwargs)
        self.point_spacing = self.spectrum[1, 0] - self.spectrum[0, 0]
        self.freq_min = self.spectrum[0, 0]
        self.freq_max = self.spectrum[-1, 0]
        self.max_intensity = [
            np.max(self.spectrum[:, num]) for num in range(1, self.spectrum.shape[1])]

    def freq_to_row(self, freq):
        """
        Return closest row number associated with the provided frequency.

        Parameters:
            freq (float):
                frequency
        Return:
            row (int):
                row index corresponding to the provided frequency.
        """
        row = int(round((freq - self.freq_min) / self.point_spacing))
        return row

    def row_to_freq(self, row):
        """
        Return frequency associated with the provided row number.

        Parameters:
            row (int):
                row index
        Returns:
            freq (float):
                frequency corresponding to the provided row index.
        """
        freq = round((row * self.point_spacing) + self.freq_min, 4)
        return freq

    def get_intensity(self, freq, spec_num=None):
        """
        Return spectrum intensity at the provided frequency.

        Parameters:
            freq (float):
                frequency
                Units: MHz
            spec_num (int):
                Used to specify which column, i.e. which spectrum, to get intensity from if the file
                is a matrix of multiple spectra. For example, spec_num=1 would give the intensity of
                the first spectrum in the matrix.
                Default: 1
        Return:
            intensity (float):
                spectral intensity at provided frequency.
        """
        if spec_num is None:
            spec_num = 1
        num = self.freq_to_row(freq)
        intensity = self.spectrum[num, spec_num]
        return intensity

    def spectrum_dictionary(self, spec_num=None):
        """
        Return dictionary with frequencies as keys and intensities as vals.

        Parameters:
            spec_num (int):
                Used to specify which column, i.e. which spectrum, to return as attributes if the file
                is a matrix of multiple spectra. For example, spec_num=1 will return the first
                spectrum in the matrix as a attributes.
                Default: 1
        Return:
            dictionary (attributes):
                dictionary of self.spectrum.
        """
        spec_num = spec_num if spec_num is not None else 1
        dictionary = {}
        for x in range(len(self.spectrum)):
            dictionary[round(self.spectrum[x, 0], 4)] = self.spectrum[x, spec_num]
        return dictionary

    def peak_pick(self, thresh=None, dyn_range=None, sort=False, spec_num=None):
        """
        Perform peak pick on spectrum. Peak identification threshold can be absolute intensity
        or dynamic range.

        Parameters:
            thresh (float):
                Intensity threshold. Do not specify thresh if using dyn_range.
                Units: mV.
                Default:  None
            dyn_range (float):
                Dynamic range with respect to the strongest transition. Do not specify dyn_range if
                using thresh.
                Default: None.
            sort (bool):
                Sort from highest to lowest intensity.
                Default: False.
            spec_num (int):
                Used to specify which column, i.e. which spectrum, to peak pick if self.spectrum is
                a matrix of multiple spectra.
                Default: 1.
        Return:
            If sort is False:
                pp (dictionary):
                    peak pick.
                    key:frequency
                    val:intensity.
            If sort is True:
                pp (list):
                    list of peaks sorted from highest to lowest intensity.
        """
        spec_num = spec_num if spec_num is not None else 1
        if thresh is None:
            if dyn_range is None:
                raise ValueError('Must provide either intensity threshold or dynamic range.')
            else:
                param = self.max_intensity[spec_num - 1] / dyn_range
        else:
            param = thresh
        peaks, _ = scipy.signal.find_peaks(self.spectrum[:, spec_num], param)
        if sort is False:
            pp = {}
            for x in peaks:
                pp[self.spectrum[x, 0]] = self.spectrum[x, spec_num]
        else:
            freqs = []
            intens = []
            for x in peaks:
                freqs.append(self.spectrum[x, 0])
                intens.append(self.spectrum[x, spec_num])
            pp = np.column_stack((freqs, intens))
            pp = pp[(-pp[:, 1]).argsort()]
        return pp

    def peak_pick_sequence_measurement(self, matrix=None, thresh=None):
        """
        Perform peak pick for sequence of spectra. Used for time evolution and temperature ramp.

        If a transition surpasses threshold in any spectrum, log intensity for that frequency in all
        spectra. Monitor transition intensity of across multiple measurements.
        Does not support dynamic range.

        Parameters:
            matrix (array):
                Spectra matrix. col[0] freq. col[1:] intensity.
                Default: self.spectrum
            thresh (float):
                threshold.
                Units: mV.
                Default: None
        Returns:
            full_pp (array):
                Matrix of all identified peaks. Frequency and intensity in all spectra.
                col[0] freq. col[1:] intensity.
        """
        if matrix is None:
            matrix = self.spectrum
        if thresh is None:
            thresh = 0.001

        full_pp = []
        for x in range(1, matrix.shape[1]):
            signal = matrix[:, x]
            peaks, _ = scipy.signal.find_peaks(signal, thresh)
            for peak in peaks:
                full_pp.append(peak)
                if peak % 2 == 0:
                    full_pp.append(peak + 1)
        full_pp = list(dict.fromkeys(full_pp))
        full_pp = sorted(full_pp)

        plus_minus_one = []
        good_for_final = []
        for x in range(len(full_pp) - 1):
            if int(full_pp[x] + 1) == int(full_pp[x + 1]):
                plus_minus_one.append(full_pp[x])
                plus_minus_one.append(full_pp[x + 1])
            elif int(full_pp[x] + 1) != int(full_pp[x + 1]) and int(full_pp[x] - 1) != int(
                    full_pp[x - 1]):
                good_for_final.append(full_pp[x])
        plus_minus_one = sorted(list(dict.fromkeys(plus_minus_one)))

        consecutives = []
        for k, g in groupby(enumerate(plus_minus_one), lambda ix: ix[0] - ix[1]):
            consecutives.append(list(map(itemgetter(1), g)))
        final_pp = good_for_final
        for x in consecutives:
            freq_x = [self.row_to_freq(y) for y in x]
            high_point = self.signal_max(
                freq_x, matrix=matrix, delta_freq=0, mode='group')
            final_pp.append(self.freq_to_row(float(high_point[0, 0])))
        return final_pp

    def simulate_peak_pick(self, thresh=None, dyn_range=None, freq_min=None, freq_max=None,
                           step_size=None, fwhm=None, scale_factor=None, spec_num=None):
        """
        Perform peak pick on spectrum and simulate the peak pick to produce an artificial spectrum
        without noise.

        Parameters:
            thresh (float):
                threshold
                Units: mV
                Default: None
            dyn_range (float):
                dynamic range with respect to the strongest transition.
                Default: None
            freq_min (float):
                Starting frequency of the simulation.
                Units: MHz
                Default: 2000
            freq_max (float):
                Stopping frequency of the simulation.
                Units: MHz
                Default: 8000
            step_size (float):
                Point spacing.
                Units: MHz
                Default: 0.0125.
            fwhm (float):
                Line width, full width half max
                Units: MHz
                Default: 0.060
            scale_factor (float):
                scale factor applied to the y-axis.
                Default: None
            spec_num (int):
                Spectrum number if self.spectrum is a matrix of multiple spectra.
                Default: 1
        Return:
            pp (dictionary):
                peak pick.
                key:frequency
                val:intensity.
            sim (array):
                simulation of the peak pick.
        """
        pp = self.peak_pick(thresh=thresh, dyn_range=dyn_range, spec_num=spec_num, sort=False)
        pp_array = np.column_stack((list(pp.keys()), list(pp.vals())))
        sim = simulate_spectrum(
            pp_array, freq_min=freq_min, freq_max=freq_max, step_size=step_size, fwhm=fwhm,
            scale_factor=scale_factor, save=False)
        return pp, sim

    def get_rows(self, freqs, matrix=None):
        """
        Create submatrix rows corresponding to the freqs input.

        Parameters:
            freqs (list):
                list of frequecies.
            matrix (array):
                Spectra matrix. col[0] freq. col[1:] intensity.
                Default: self.spectrum
        Return:
            submatrix (array):
                array of the matrix containing only rows at the requested frequencies.
        """
        if matrix is None:
            matrix = self.spectrum
        submatrix = np.zeros((len(freqs), matrix.shape[1]))
        for x in range(len(freqs)):
            row = self.freq_to_row(freqs[x])
            submatrix[x, :] = matrix[row, :]
        return submatrix

    def signal_max(self, freqs, matrix=None, delta_freq=None, mode='singles'):
        """
        Find peak intensity, corresponding frequency, and corresponding spectrum from matrix.

        Given a matrix of spectra, identify the spectrum exhibiting the strongest signal in the
        region of frequency +/- delta_freq. The parameter, delta_freq, is a buffer added to the
        expected frequency used to find the best line position. Set delta_freq to a couple step
        sizes, at most, to avoid misidentification. The frequency corresponding to the strongest
        signal in the buffered region is taken as the accepted frequency.
        Three values are returned: the accepted frequency, the intensity of the strongest signal,
        and the column number (i.e. spectrum) containing the strongest signal.

        Parameters:
            freqs (list or array):
                Expected frequencies.
                Units: MHz.
            matrix (array):
                Spectra matrix. col[0] freq. col[1:] intensity.
                Default: self.spectrum
            delta_freq (float):
                Frequency buffer. Extends in both +/- directions around freqs items.
                Units: MHz
                Default: 0
            mode (str):
                Default: singles
                mode=singles: items from freqs are evaluated individually.
                mode=group: items in freqs are treated as a block of consecutive frequencies.
                Include all frequencies between upper and lower limits. delta_freq is added to
                upper and lower limits. Pass a single block per method call.
        Returns:
            high_points (array):
                col[0] -> Frequency of strongest signal in the submatrix.
                col[1] -> Max intensity observed in the submatrix.
                col[2] -> Spectrum in which the highest intensity is observed. Starts at 1, which
                corresponds to the first spectrum, since the 0th column contains frequency.
                Array is sorted in descending order by the intensity column
        """
        if matrix is None:
            matrix = self.spectrum
        if delta_freq is None:
            delta_freq = 0
        if type(freqs) != list:
            freqs = [freqs]
        else:
            freqs = sorted(freqs)
        if mode == 'singles':
            pass
        elif mode == 'group':
            freqs = [freqs]

        freq = []
        intensity = []
        spectrum = []
        pos_buffer = int(round(delta_freq / self.point_spacing) + 1)
        neg_buffer = int(round(delta_freq / self.point_spacing))
        for x in freqs:
            if mode == 'singles':
                target_row = self.freq_to_row(x)
                with_freq = matrix[target_row - neg_buffer:target_row + pos_buffer, :]
            elif mode == 'group':
                upper_row = self.freq_to_row(x[-1])
                lower_row = self.freq_to_row(x[0])
                with_freq = matrix[lower_row - neg_buffer:upper_row + pos_buffer, :]
            without_freq = with_freq[:, 1:]
            col_shape = np.shape(without_freq)[1]
            flattened_without_freq = without_freq.flatten()
            max_index = np.argmax(flattened_without_freq, axis=0)
            max_row = math.floor(max_index / col_shape)
            max_col_with_freq = max_index % col_shape + 1
            freq.append(with_freq[max_row, 0])
            intensity.append(with_freq[max_row, max_col_with_freq])
            spectrum.append(max_col_with_freq)
        high_points = np.column_stack((freq, intensity, spectrum))
        high_points = np.array(high_points[(-high_points[:, 1]).argsort()])
        return high_points

    def normalize_transition(self, freq):
        """
        Use with matrix of spectra. Normalize transition intensity across the columns of the matrix.

        Parameters:
            freq (float):
                Transition frequency.
                Units: MHz
        Returns:
            norm_intensities (array):
                col[0]
                    Frequency.
                    Units: MHz
                col[1]
                    Highest observed intensity (i.e. normalization factor)
                    Units: mV
                col[2:]
                    Remaining columns contain normalized intensities.
        """
        row = self.freq_to_row(freq)
        intensities = self.spectrum[row, 1:]
        norm_intensities = []
        max_intensity = np.max(intensities)
        norm_intensities.append(freq)
        norm_intensities.append(max_intensity)
        norm = intensities / max_intensity
        for x in norm:
            norm_intensities.append(x)
        return norm_intensities

# file = 'C:\\ROT\\CoAdd_water18_6percent_2to8_3500k_39C_4us_35psig__FF10_KB95_TRL80.ft'
# file = 'C:\\ROT\\CoAdd_water18_6percent_2to8_3500k_39C_4us_35psig__FF10_KB95_TRL80.ft'

# # file = 'C:\\ROT\\CoAdd_water18_6percent_2to8_3500k_39C_4us_35psig__FF10_KB95_TRL80.ft'
# # file_2 = 'C:\\ROT\\CoAdd_water18_3percent_2to8_3000k_39C_4us_35psig__FF10_KB95_TRL80.ft'

# import os
# fp = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\Rotational Spectroscopy Data Analysis 4_24_2020\\3_1_2021_Testing\\Spectrum\\'
# f1 = fp + '16_38_37_Varenicline_2to8_10k_175C_4us_15psig_.txt'
# # f2 = fp + '16_44_59_Varenicline_2to8_10k_175C_4us_15psig_.txt'
# # f3 = fp + '16_51_22_Varenicline_2to8_10k_175C_4us_15psig_.txt'
# # f4 = fp + '16_38_37_Varenicline_2to8_10k_175C_4us_15psig_.txt'
# # f5 = fp + '17_03_59_Varenicline_2to8_20k_175C_4us_15psig_.txt'
# # f6 = fp + '17_16_36_Varenicline_2to8_20k_175C_4us_15psig_.txt'
# #
# f1_fid = FID(f1)
# fft = f1_fid.quick_fft(0.5, 4, 80, 2000, 8000)
# os.chdir(fp)
# np.savetxt('quick_fft_test.ft', fft)
# f2_fid = FID(f2)
# f3_fid = FID(f3)
# f4_fid = FID(f4)
# f5_fid = FID(f5)
# f6_fid = FID(f6)

# f1_fid.gate_kaiser_zeropad(frac=1, kb=9.5, total_time=80)

# f2_add_time = f2_fid.add_time_column()
# f3_add_time = f3_fid.add_time_column()
# f4_add_time = f4_fid.add_time_column()
# f5_add_time = f5_fid.add_time_column()
# f6_add_time = f6_fid.add_time_column()
# print('balls')
