"""
Author: Channing West
Changelog: 12/5/2019, 2/1/2020
"""

import os
import shutil
import numpy as np
import subprocess
import pandas as pd
import Spectrum

key_dict = {'A': '10000', 'B': '20000', 'C': '30000',
            'DJ': '200', 'DJK': '1100', 'DK': '2000', 'dJ': '40100', 'dK': '41000',
            'chi_aa_1': '110010000', 'chi_bbcc_1': '110040000', 'chi_ab_1': '110610000',
            'chi_bc_1': '110210000', 'chi_ac_1': '110410000', 'chi_aa_2': '220010000',
            'chi_bbcc_2': '220040000', 'chi_ab_2': '220610000', 'chi_bc_2': '220210000',
            'chi_ac_2': '220410000', 'chi_aa_3': '330010000', 'chi_bbcc_3': '330040000',
            'chi_ab_3': '330610000', 'chi_bc_3': '330210000', 'chi_ac_3': '330410000',
            '10000': 'A', '20000': 'B', '30000': 'C',
            '200': 'DJ', '1100': 'DJK', '2000': 'DK', '40100': 'dJ', '41000': 'dK',
            '110010000': 'chi_aa_1', '110040000': 'chi_bbcc_1', '110610000': 'chi_ab_1',
            '110210000': 'chi_bc_1', '110410000': 'chi_ac_1', '220010000': 'chi_aa_2',
            '220040000': 'chi_bbcc_2', '220610000': 'chi_ab_2', '220210000': 'chi_bc_2',
            '220410000': 'chi_ac_2', '330010000': 'chi_aa_3', '330040000': 'chi_bbcc_3',
            '330610000': 'chi_ab_3', '330210000': 'chi_bc_3', '330410000': 'chi_ac_3'}
spind_dict = {'3': 1, '5': 2, '7': 3, '2': 0.5, '4': 1.5, '6': 2.5}
dc_list = ['DJ', 'DJK', 'DK', 'dJ', 'dK']


class Par_Var:
    """
    Manipulate preexisting *.par and *.var files. Create new files.

    Attributes:
        file (str):
            File read into a list.
            Default: None
        attributes (dict):
            npar (int):
                Maximum number of constants in fit.
                Default: 8
            nline (int):
                Maximum number of transitions in fit.
                Default: 1000
            nitr (int):
                Maximum number of iterations to reach convergence.
                Default: 51
            nxpar (int):
                Number of parameters to exclude from end of list when fitting special lines.
                Default: 0
            thresh (str):
                Initial Marquardt-Levenburg parameter.
                Default: 0.000E+000
            errtst (float):
                Maximum [(obs-calc)/error].
                Default: 1.00E+005
            frac (float):
                Fractional importance of variance.
                Default: 1.00E+000
            cal (float):
                Scaling for infrared line frequencies.
                Default: 1.0000
            spin1, spin2, spin3 (int):
                Nuclear spins.
                Default: None
            spind: (int)
                Degeneracy of spins, first spin degeneracy in units digit, second in tens digit,
                etc.
                Default: 1
            chr (str):
                'a' is used for Watson A set. 's' is used for Watson S set.
                Default: a
            nvib (int):
                Sign -> positive, prolate rotor (z = a, y = b, x = c)
                sign -> negative, oblate rotor (z = c, y = b, x = a).
                magnitude -> number of vibronic states.
                Default: 1
            knmin (int):
                Minimum K value.
                Default: 0
            knmax (int):
                Maximum K value.
                Default: 99
            ixx (int):
                Binary flags for inclusion of interactions:
                bit 0 set means no deltaN != 0 interactions,
                bit 1 means no deltaJ,
                bit 2 means no delta F1.
                Default: 0
            iax (int):
                If negative, use Itot basis, in which the last n spins are summed to give Itot,
                which is then combined with the other spins to give F.
                Default: 1
            wtpl (int):
                Statistical weight for even vibronic state.
                Default: 1
            wtmn (int):
                Statistical weight for odd vibronic state.
                Default: 1
            vsym (int):
                Positive or zero, there is only one option line.
                Default: 1
            ewt (int):
                Weight for states with E symmetry
                Default: -1
            diag (int):
                -1 for no diagonalization
                0 for energy ordering within Wang sub-blocks
                1 for full projection assignment
                Default: 0
            xopt (int):
                = PHASE + 10 * NEWLZ + 20 * NOFC + 40 * G12
                -   PHASE = 0 : : : 8, force phase choice. 0 means no forcing, 8 means use
                    standard phase with all even-order operators real and all odd-order
                    operators imaginary.
                -   NEWLZ is 1 if Lz operator is explicitly defined in the parameter identifier
                -   NOFC is 1 if the FF field of IDPAR specifies Kavg rather than Fourier
                    coeficient
                -   G12 is one if the sine or cosine Fourier operator is to be multiplied
                    by -1 if K is odd
                Default: None
            A, B, C (float):
                Rigid rotor constants
                Units: MHz
                Default: 0
            DJ, DJK, DK, dJ, dK (float):
                Quartic distortion constants
                Units: MHz
                Default: None
            DJ_err, DJK_err, DK_err, dJ_err, dK_err (float):
                Quartic distortion uncertainties
                Units: MHz
                Default: 1
            chi_aa_1, chi_bbcc_1, chi_ab_1, chi_bc_1, chi_ac_1 (float):
                Quad constants nucleus 1
                Default: None
            chi_aa_2, chi_bbcc_2, chi_ab_2, chi_bc_2, chi_ac_2 (float):
                Quad constants nucleus 2
                Default: None
            chi_aa_3, chi_bbcc_3, chi_ab_3, chi_bc_3, chi_ac_3 (float):
                Quad constants nucleus 3
                Default: None
            chi_aa_1_err, chi_bbcc_1_err, chi_ab_1_err, chi_bc_1_err, chi_ac_1_err (float):
                Quad uncertainties nucleus 1
                Default: 0
            chi_aa_2_err, chi_bbcc_2_err, chi_ab_2_err, chi_bc_2_err, chi_ac_2_err (float):
                Quad uncertainties nucleus 2
                Default: 0
            chi_aa_3_err, chi_bbcc_3_err, chi_ab_3_err, chi_bc_3_err, chi_ac_3_err (float):
                Quad uncertainties nucleus 3
                Default: 0
        given_constants (list):
            List constants contained in *.par/*.var file.
    Methods:
        set_constant(constant, val)
            Set value of rotational constant to val in self.attributes
        set_stdev(constant, stdev)
            Set stdev of rotational constant to either 1.0E-020 or 1.0E+000 in self.attributes
        float_all_qdc()
            Set stdev of all quartic distortion constants to 1.0E+000 in self.attributes
        fix_all_qdc()
            Set stdev of all quartic distortion constants to 1.0E-020 in self.attributes
        float_given_qdc()
            Set stdev of all non-None quartic distortion constants to 1.0E+000 in self.attributes
        fix_given_qdc()
            Set stdev of all non-None quartic distortion constants to 1.0E-020 in self.attributes
        remove_constant(constant)
            Remove constant from self.attributes. Constant no longer appears in self.write() return
        nuclear_spin_flag(spin1, spin2, spin3)
            Generate nucluear spin flag (spind) for up to three quadrupolar nuclei.
        get_constant(constant)
            Return constant(s) from self.attributes.
        get_stdev(constant)
            Return standard deviation(s) from self.attributes.
        write(fname, all_qdc, save, extension)
            Generate formatted string. Can be saved as *.par/*.var file.
        save(fname, all_qdc, extension)
            Save formatted *.par or *.var file.
    """
    default_dict = {
        'npar': 8, 'nline': 1000, 'nitr': 51, 'nxpar': 0, 'thresh': '0.000E+000',
        'errtst': '1.00E+005', 'frac': '1.00E+000', 'cal': '1.0000',
        'spin_1': None, 'spin_2': None, 'spin_3': None,
        'chr': 'a', 'spind': 1, 'nvib': 1, 'knmin': 0, 'knmax': 99, 'ixx': 0,
        'iax': 1, 'wtpl': 1, 'wtmn': 1, 'vsym': 1, 'ewt': -1, 'diag': 0, 'xopt': None,
        'A': 0, 'B': 0, 'C': 0, 'A_err': 1, 'B_err': 1, 'C_err': 1,
        'DJ': None, 'DJK': None, 'DK': None, 'dJ': None, 'dK': None,
        'DJ_err': 1, 'DJK_err': 1, 'DK_err': 1, 'dJ_err': 1, 'dK_err': 1,
        'chi_aa_1': None, 'chi_bbcc_1': None, 'chi_ab_1': None,
        'chi_bc_1': None, 'chi_ac_1': None,
        'chi_aa_2': None, 'chi_bbcc_2': None, 'chi_ab_2': None,
        'chi_bc_2': None, 'chi_ac_2': None,
        'chi_aa_3': None, 'chi_bbcc_3': None, 'chi_ab_3': None,
        'chi_bc_3': None, 'chi_ac_3': None,
        'chi_aa_1_err': 0, 'chi_bbcc_1_err': 0, 'chi_ab_1_err': 0,
        'chi_bc_1_err': 0, 'chi_ac_1_err': 0,
        'chi_aa_2_err': 0, 'chi_bbcc_2_err': 0, 'chi_ab_2_err': 0,
        'chi_bc_2_err': 0, 'chi_ac_2_err': 0,
        'chi_aa_3_err': 0, 'chi_bbcc_3_err': 0, 'chi_ab_3_err': 0,
        'chi_bc_3_err': 0, 'chi_ac_3_err': 0}

    def __init__(self, file=None, **kwargs):
        variables = ['npar', 'nline', 'nitr', 'nxpar', 'thresh', 'errtst', 'frac', 'cal', 'spin_1',
                     'spin_2', 'spin_3', 'chr', 'spind', 'nvib', 'knmin', 'knmax', 'ixx', 'iax',
                     'wtpl', 'wtmn', 'vsym', 'ewt', 'diag', 'xopt']
        type_integer = ['npar', 'nline', 'nitr', 'nxpar', 'spin_1', 'spin_2', 'spin_3',
                        'nvib', 'knmin', 'knmax', 'ixx', 'iax', 'wtpl', 'wtmn', 'vsym', 'ewt',
                        'diag', 'xopt']
        type_float = ['thresh', 'errtst', 'frac', 'cal']
        type_str = ['chr', 'spind']
        rcs = ['A', 'B', 'C', 'DJ', 'DJK', 'DK', 'dJ', 'dK',
               'chi_aa_1', 'chi_bbcc_1', 'chi_ab_1', 'chi_bc_1', 'chi_ac_1',
               'chi_aa_2', 'chi_bbcc_2', 'chi_ab_2', 'chi_bc_2', 'chi_ac_2',
               'chi_aa_3', 'chi_bbcc_3', 'chi_ab_3', 'chi_bc_3', 'chi_ac_3']
        self.attributes = {}
        if file is None:
            for variable in variables:
                if variable in kwargs.keys():
                    self.attributes[variable] = kwargs[variable]
                else:
                    self.attributes[variable] = Par_Var.default_dict[variable]
            for rc in rcs:
                if rc in kwargs.keys():
                    self.attributes[rc] = kwargs[rc]
                else:
                    self.attributes[rc] = Par_Var.default_dict[rc]

                err = rc + '_err'
                if err in kwargs.keys():
                    self.set_stdev(rc, floating=not (kwargs[err]))
                else:
                    self.attributes[err] = Par_Var.default_dict[err]
            self.attributes['spind'] = self.nuclear_spin_flag(
                spin_1=self.attributes['spin_1'], spin_2=self.attributes['spin_2'],
                spin_3=self.attributes['spin_3'])
        else:
            with open(file, "r") as f:
                self.file = f.readlines()
            f.close()
            split_file = [row.split() for row in self.file]
            first_elements = []
            for row in split_file:
                try:
                    first_elements.append(row[0])
                except IndexError:
                    pass
            flags = (
                ('npar', 1, 0), ('nline', 1, 1), ('nitr', 1, 2), ('nxpar', 1, 3), ('thresh', 1, 4),
                ('errtst', 1, 5), ('frac', 1, 6), ('cal', 1, 7), ('chr', 2, 0), ('spind', 2, 1),
                ('nvib', 2, 2), ('knmin', 2, 3), ('knmax', 2, 4), ('ixx', 2, 5), ('iax', 2, 6),
                ('wtpl', 2, 7), ('wtmn', 2, 8), ('vsym', 2, 9), ('ewt', 2, 10), ('diag', 2, 11),
                ('xopt', 2, 12))
            constants = (
                ('A', '10000'), ('B', '20000'), ('C', '30000'),
                ('DJ', '200'), ('DJK', '1100'), ('DK', '2000'), ('dJ', '40100'), ('dK', '41000'),
                ('chi_aa_1', '110010000'), ('chi_bbcc_1', '110040000'), ('chi_ab_1', '110610000'),
                ('chi_bc_1', '110210000'), ('chi_ac_1', '110410000'),
                ('chi_aa_2', '220010000'), ('chi_bbcc_2', '220040000'), ('chi_ab_2', '220610000'),
                ('chi_bc_2', '220210000'), ('chi_ac_2', '220410000'),
                ('chi_aa_3', '330010000'), ('chi_bbcc_3', '330040000'), ('chi_ab_3', '330610000'),
                ('chi_bc_3', '330210000'), ('chi_ac_3', '330410000'))
            for flag, row, col in flags:
                try:
                    if flag in type_integer:
                        self.attributes[flag] = int(split_file[row][col])
                    elif flag in type_str:
                        self.attributes[flag] = str(split_file[row][col])
                    elif flag in type_float:
                        self.attributes[flag] = float(split_file[row][col])
                    else:
                        self.attributes[flag] = str(split_file[row][col])
                except IndexError:
                    self.attributes[flag] = None
            self.given_constants = []
            for constant, par in constants:
                try:
                    self.attributes[constant] = float(split_file[first_elements.index(par)][1])
                    self.attributes[
                        '{constant}_err'.format(constant=constant)] = float(
                        split_file[first_elements.index(par)][2])
                    self.given_constants.append(constant)
                except (ValueError, AttributeError):
                    self.attributes[constant] = None
                    self.attributes['{constant}_err'.format(constant=constant)] = None
            spind = self.attributes['spind']
            spind = list(spind)
            if len(spind) == 1:
                spin_1 = spind[0]
                if int(spin_1) == 1:
                    self.attributes['spin_1'] = 0
                    self.attributes['spin_2'] = 0
                    self.attributes['spin_3'] = 0
                else:
                    self.attributes['spin_1'] = spind_dict[spin_1]
                    self.attributes['spin_2'] = 0
                    self.attributes['spin_3'] = 0
            elif len(spind) == 2:
                self.attributes['spin_1'] = spind_dict[spind[0]]
                self.attributes['spin_2'] = spind_dict[spind[1]]
                self.attributes['spin_3'] = 0
            if len(spind) == 3:
                self.attributes['spin_1'] = spind_dict[spind[0]]
                self.attributes['spin_2'] = spind_dict[spind[1]]
                self.attributes['spin_3'] = spind_dict[spind[2]]

    def set_constant(self, constant, val=None):
        """
        Set rotational constant value to val in self.attributes.

        Parameters:
            constant (str or list of strings):
               A, B, C, DJ, DJK, DK, dJ, dK, chi_aa_1, etc.
            val (float or list of floats):
               Rotational constant value.
               Units: MHz.
        """
        if type(constant) != list:
            constant = [constant]
        if val is not None:
            if type(val) != list:
                val = [val]
        else:
            val = [0.0 for x in constant]
        for x in range(len(constant)):
            self.attributes[constant[x]] = val[x]

    def set_stdev(self, constant, floating=True):
        """
        Set stdev of a constant to 1.0E-020 or 1.0E+000 in self.attributes.

        Parameters:
            constant (str or list of strings):
               A, B, C, DJ, DJK, DK, dJ, dK, chi_aa_1, . . . etc.
            floating (bool):
               If True, constant is able to fluctuate. If False, constant is fixed.
        """
        if type(constant) != list:
            constant = [constant]
        for x in range(len(constant)):
            if floating:
                stdev = 1.0E+000
            else:
                stdev = 1.0E-020
            self.attributes['{param}_err'.format(param=constant[x])] = stdev

    def float_all_qdc(self):
        """ Set stdev of all quartic distortion constants to 1.0E+000. """
        for dc in dc_list:
            if self.attributes[dc] is None:
                self.set_constant(dc, 0.0)
                self.attributes['npar'] = int(self.attributes['npar']) + 1
        self.set_stdev(dc_list, floating=True)

    def fix_all_qdc(self):
        """ Set stdev of all quartic distortion constants to 1.0E-020. """
        for dc in dc_list:
            if self.attributes[dc] is None:
                self.set_constant(dc, 0.0)
                self.attributes['npar'] = int(self.attributes['npar']) + 1
        self.set_stdev(dc_list, floating=False)

    def float_given_qdc(self):
        """ Set stdev of all non-None quartic distortion constants to 1.0E+000. """
        for dc in dc_list:
            if self.attributes[dc] is not None:
                self.set_stdev(dc_list, floating=True)

    def fix_given_qdc(self):
        """ Set stdev of all non-None quartic distortion constants to 1.0E-020. """
        for dc in dc_list:
            if self.attributes[dc] is not None:
                self.set_stdev(dc_list, floating=False)

    def remove_constant(self, constant):
        """ Remove constant from self.attributes. Removes it from self.write() return. """
        if type(constant) != list:
            constant = [constant]
        for x in constant:
            self.attributes[x] = None

    def nuclear_spin_flag(self, spin_1=None, spin_2=None, spin_3=None):
        """
        Return the nucluear spin flag (spind) from the nuclear spin flags of up to three quads.

        If no quads, return 1.

        Parameters:
            spin_1 (str):
                Nuclear spin of quadrupolar nucleus 1.
            spin_2 (str):
                Nuclear spin of quadrupolar nucleus 2.
            spin_3 (str):
                Nuclear spin of quadrupolar nucleus 3.
        Returns:
            spin_total (str):
                Nuclear spin flag.
        """
        spin_dict = {'1': '3', '1.0': '3', '2': '5', '2.0': '5', '3': '7', '3.0': '7', '0.5': '2',
                     '1.5': '4', '2.5': '6'}
        if spin_1 is None:
            spin_1 = '1'
        else:
            spin_1 = spin_dict[str(spin_1)]
        if spin_2 is not None:
            spin_2 = spin_dict[str(spin_2)]
        if spin_3 is not None:
            spin_3 = spin_dict[str(spin_3)]

        spin_total = spin_1
        if spin_2 is not None:
            spin_total += spin_2
        if spin_3 is not None:
            spin_total += spin_3
        return spin_total

    def get_constant(self, constant):
        """
        Return constant(s) from self.attributes.

        Parameters:
            constant (str or list of strings):
                A, B, C, DJ, DJK, DK, dJ, dK, chi_aa_1, . . . etc.
        Returns:
            param_list (list of strings):
                List of requested rotational constants.
                Units: MHz
        """
        if type(constant) != list:
            params = [constant]
        param_list = [self.attributes[param] for param in params]
        return param_list

    def get_stdev(self, constant):
        """
        Return standard deviation(s) from self.attributes.

        Parameters:
            constant (str or list of strings):
                A, B, C, DJ, DJK, DK, dJ, dK, chi_aa_1, . . . etc.
        Returns:
            param_list (list of strings):
                List of requested standard deviation(s).
                Units: MHz
        """
        if type(constant) != list:
            params = [constant]
        param_list = [self.attributes['{param}_err'.format(param=param)] for param in params]
        return param_list

    def write(self, fname=None, all_qdc=False, save=False, extension=None):
        """
        Generate formatted string that can be saved as *.par/*.var file.

        Parameters:
            fname (str):
                File name.
            all_qdc (bool):
                Set whether to include zero valued quartic distortion constants in the output.
            save (bool):
                Set whether to save output to a file.
            extension (str):
                Set extension type of saved file. (*.par or *.var)
        Returns:
            par_file (str):
                Formatted string.
        """
        if fname is None:
            fname = 'molecule'
        if all_qdc:
            qdcs = ['DJ', 'DJK', 'DK', 'dJ', 'dK']
            for qdc in qdcs:
                if self.attributes[qdc] is None:
                    self.attributes[qdc] = 0
        quad_list = ['chi_aa_1', 'chi_bbcc_1', 'chi_ab_1', 'chi_bc_1', 'chi_ac_1', 'chi_aa_2',
                     'chi_bbcc_2', 'chi_ab_2', 'chi_bc_2', 'chi_ac_2', 'chi_aa_3', 'chi_bbcc_3',
                     'chi_ab_3', 'chi_bc_3', 'chi_ac_3']
        quad_terms = ""
        for quad in quad_list:
            if self.attributes[quad] is not None:
                self.attributes['npar'] = int(self.attributes['npar']) + 1
                quad_terms += "       {key}  {constant} {err} \n".format(
                    key=key_dict[quad], constant=self.attributes[quad],
                    err=self.attributes['{quad}_err'.format(quad=quad)])
        npar = self.attributes['npar'] if self.attributes['npar'] is not None else ''
        nline = self.attributes['nline'] if self.attributes['nline'] is not None else ''
        nitr = self.attributes['nitr'] if self.attributes['nitr'] is not None else ''
        nxpar = self.attributes['nxpar'] if self.attributes['nxpar'] is not None else ''
        thresh = self.attributes['thresh'] if self.attributes['thresh'] is not None else ''
        errtst = self.attributes['errtst'] if self.attributes['errtst'] is not None else ''
        frac = self.attributes['frac'] if self.attributes['frac'] is not None else ''
        cal = self.attributes['cal'] if self.attributes['cal'] is not None else ''
        chr = self.attributes['chr'] if self.attributes['chr'] is not None else ''
        spind = self.attributes['spind'] if self.attributes['spind'] is not None else ''
        nvib = self.attributes['nvib'] if self.attributes['nvib'] is not None else ''
        knmin = self.attributes['knmin'] if self.attributes['knmin'] is not None else ''
        knmax = self.attributes['knmax'] if self.attributes['knmax'] is not None else ''
        ixx = self.attributes['ixx'] if self.attributes['ixx'] is not None else ''
        iax = self.attributes['iax'] if self.attributes['iax'] is not None else ''
        wtpl = self.attributes['wtpl'] if self.attributes['wtpl'] is not None else ''
        wtmn = self.attributes['wtmn'] if self.attributes['wtmn'] is not None else ''
        vsym = self.attributes['vsym'] if self.attributes['vsym'] is not None else ''
        ewt = self.attributes['ewt'] if self.attributes['ewt'] is not None else ''
        diag = self.attributes['diag'] if self.attributes['diag'] is not None else ''
        xopt = self.attributes['xopt'] if self.attributes['xopt'] is not None else ''

        par_dict = {'npar': npar, 'nline': nline, 'nitr': nitr, 'nxpar': nxpar, 'thresh': thresh,
                    'errtst': errtst, 'frac': frac, 'cal': cal}
        par_dict_2 = {'chr': chr, 'spind': spind, 'nvib': nvib, 'knmin': knmin, 'knmax': knmax,
                      'ixx': ixx, 'iax': iax, 'wtpl': wtpl, 'wtmn': wtmn, 'vsym': vsym, 'ewt': ewt,
                      'diag': diag, 'xopt': xopt}
        par_file = ""
        par_file += "{fname}  \n".format(fname=fname)
        par_file += "   {npar}  {nline}  {nitr}  {nxpar}  {thresh}  {errtst}  {frac}  " \
                    "{cal}\n".format(**par_dict)
        par_file += "{chr}  {spind}  {nvib}  {knmin}  {knmax}  {ixx}  {iax}  {wtpl}  {wtmn}  " \
                    "{vsym}  {ewt}  {diag}  {xopt}\n".format(**par_dict_2)

        rc_list = ['A', 'B', 'C', 'DJ', 'DJK', 'DK', 'dJ', 'dK']
        for rc in rc_list:
            if len(key_dict[rc]) == 3:
                spaces = '             '
            elif len(key_dict[rc]) == 4:
                spaces = '            '
            elif len(key_dict[rc]) == 5:
                spaces = '           '
            if self.attributes[rc] is not None:
                par_file += "{spaces}{idpar}  {par} {err} \n".format(
                    spaces=spaces, idpar=key_dict[rc], par=self.attributes[rc],
                    err=self.attributes['{rc}_err'.format(rc=rc)])
        par_file += quad_terms
        if save:
            if extension is None:
                extension = '.par'
            elif extension == 'par':
                extension = '.par'
            elif extension == 'var':
                extension = '.var'
            else:
                extension = extension
            with open('{fname}{ext}'.format(fname=fname, ext=extension), 'w') as f:
                for row in par_file:
                    f.write(row)
            f.close()
        return par_file

    def save(self, fname=None, all_qdc=False, extension=None):
        """
        Save  *.par or *.var file with proper formatting.

        Parameters:
            fname (str):
                File name.
            extension (str):
                Set extension type of the saved file. (*.par or *.var)
            all_qdc (bool):
                Set whether to include zero valued quartic distortion constants in the output.
        """
        par = self.write(fname, all_qdc=all_qdc, save=True, extension=extension)
        if fname is None:
            fname = self.fname
        if extension is None:
            extension = '.par'
        elif extension == 'par':
            extension = '.par'
        elif extension == 'var':
            extension = '.var'
        else:
            extension = extension
        with open('{fname}{ext}'.format(fname=fname, ext=extension), 'w') as f:
            for row in par:
                f.write(row)
        f.close()


# f = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\Varenicline\\Pickett Var for AABS.par'
# # # f2 = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\Rotational Spectroscopy Data Analysis 4_24_2020\\Program Testing\\t3.par'
# par = Par_Var(file=f)
# print(par.attributes)
# write = par.write(fname='test')
# print('\n\n\n', write, '\n\n\n', par.attributes['npar'])


class Lin:
    """
    Manipulate preexisting *.lin files. Create new files.

    Parameters:
        file (str):
            File path.
    Attributes:
        delimiter (list of str):
            List of column spacings.
            Default:
                ['%3.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f',
                '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%12.4f', '%12.6f', '%12.2E']
        fname (str):
            File name. Not full path
        fpath (str):
            Full file path.
        lin (np.array):
            File read into array.
        dict (dict of dicts):
            {freq:{J1:,Ka1:,Kc1:,J0:,Ka0:,Kc0:,QN1_1:,QN2_1:,QN3_1:,QN1_0:,QN2_0:,QN3_0:}}
            Keys are frequencies. vals are dicts, with each dict being a unique set of QNs
    Methods:
        assign_transition(**kw)
            Add new assignment to self.dict.
        delete_dict_asn(freq)
            Delete assignment from self.dict.
        delete_array_row(row, arr)
            Delete assignment from self.lin array.
        write(arr, save, fname)
            Return formatted string using assignments in self.dict.
        save(fname, arr)
            Save external *.lin file.
     """
    default_dict = {'QN1_1': 0, 'QN2_1': 0, 'QN3_1': 0, 'QN1_0': 0, 'QN2_0': 0, 'QN3_0': 0,
                    'err': 0.040000, 'wt': 1.00E-04}

    def __init__(self, file=None):
        self.delimiter = ['%3.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f',
                          '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%12.4f', '%12.6f', '%12.2E']
        self.dict = {}
        if file is not None:
            self.fname = os.path.basename(str(file)).split('.')[0]
            self.fpath = os.path.abspath(str(file))
            self.lin = np.genfromtxt(file)
            self.update_dict(arr=self.lin)
        else:
            self.fname = None
            self.fpath = None
            self.lin = None

    def update_dict(self, arr=None):
        """
        Update self.dict using array. Use to keep self.lin and self.dict consistent.

        Useful in situations where manipulating an array is easier than manipulating self.dict.

        Parameters:
            arr (np.array):
                Array of lin information.
                Default: self.lin
        """
        if arr is None:
            arr = self.lin
        J1 = arr[:, 0]
        Ka1 = arr[:, 1]
        Kc1 = arr[:, 2]
        QN1_1 = arr[:, 6]
        QN2_1 = arr[:, 7]
        QN3_1 = arr[:, 8]
        J0 = arr[:, 3]
        Ka0 = arr[:, 4]
        Kc0 = arr[:, 5]
        QN1_0 = arr[:, 9]
        QN2_0 = arr[:, 10]
        QN3_0 = arr[:, 11]
        freq = arr[:, 12]
        err = arr[:, 13]
        wt = arr[:, 14]
        for x in range(len(freq)):
            line_dict = {
                'J1': int(J1[x]), 'Ka1': int(Ka1[x]), 'Kc1': int(Kc1[x]),
                'J0': int(J0[x]), 'Ka0': int(Ka0[x]), 'Kc0': int(Kc0[x]),
                'QN1_1': int(QN1_1[x]), 'QN2_1': int(QN2_1[x]), 'QN3_1': int(QN3_1[x]),
                'QN1_0': int(QN1_0[x]), 'QN2_0': int(QN2_0[x]), 'QN3_0': int(QN3_0[x]),
                'freq': freq[x], 'err': err[x], 'wt': wt[x]}
            if freq[x] in self.dict.keys():
                self.dict[freq[x]].append(line_dict)
            else:
                self.dict[freq[x]] = [line_dict]

    def update_array(self, dict=None):
        """
        Update self.lin using dictionary. Use to keep self.lin and self.dict consistent.

        Parameters:
            dict (dictionary):
                Dictionary of lin information.
                Default: self.dict
        """
        if dict is None:
            dict = self.dict
        J1, Ka1, Kc1, J0, Ka0, Kc0 = [], [], [], [], [], []
        QN1_1, QN2_1, QN3_1, QN1_0, QN2_0, QN3_0 = [], [], [], [], [], []
        freq, err, wt = [], [], []
        write_dict = {
            'J1': J1, 'Ka1': Ka1, 'Kc1': Kc1, 'J0': J0, 'Ka0': Ka0, 'Kc0': Kc0, 'QN1_1': QN1_1,
            'QN2_1': QN2_1, 'QN3_1': QN3_1, 'QN1_0': QN1_0, 'QN2_0': QN2_0, 'QN3_0': QN3_0,
            'freq': freq, 'err': err, 'wt': wt}
        lines = [v[x] for k, v in dict.items() for x in range(len(v))]
        for d in lines:
            for k, v in d.items():
                write_dict[k].append(v)
        self.lin = np.column_stack(
            (J1, Ka1, Kc1, J0, Ka0, Kc0, QN1_1, QN2_1, QN3_1, QN1_0, QN2_0, QN3_0, freq, err, wt))

    def assign_transition(self, **kwargs):
        """
        Add new transition assignment to self.dict.

        Parameters:
            Pass single value kwargs to assign a single transition or a list of values to assign
            multiple transitions in a single method call.

            Required Kwargs:
                freq (float):
                    Line frequency.
                    Units: MHz.
                J1 (int):
                    J1 Quantum Number
                Ka1 (int):
                    Ka1 Quantum Number
                Kc1 (int):
                    Kc1 Quantum Number
                J0 (int):
                    J0 Quantum Number
                Ka0 (int):
                    Ka0 Quantum Number
                Kc0 (int):
                    Kc0 Quantum Number
            Optional Kwargs
                err (float):
                    Expected error
                    Units: MHz
                    Default: 0.040000
                wt (float):
                    Blend weight
                    Default: 1.00E-04

                If additional quantum numbers are needed for quad splitting:
                QN1_1 (int):
                    QN1_1 Quantum Number
                    Default: 0
                QN2_1 (int):
                    QN2_1 Quantum Number
                    Default: 0
                QN3_1 (int):
                    QN3_1 Quantum Number
                    Default: 0
                QN1_0 (int):
                    QN1_0 Quantum Number
                    Default: 0
                QN2_0 (int):
                    QN2_0 Quantum Number
                    Default: 0
                QN3_0 (int):
                    QN3_0 Quantum Number
                    Default: 0
        """
        required_kwargs = ['freq', 'J1', 'Ka1', 'Kc1', 'J0', 'Ka0', 'Kc0']
        optional_kwargs = ['QN1_1', 'QN2_1', 'QN3_1', 'QN1_0', 'QN2_0', 'QN3_0', 'err', 'wt']
        # for key in kwargs.keys():
        #     if type(kwargs[key]) != list:
        #         kwargs[key] = [kwargs[key]]
        for key in optional_kwargs:
            if key in kwargs.keys():
                if type(kwargs[key]) != list:
                    kwargs[key] = [kwargs[key]]
            else:
                kwargs[key] = [Lin.default_dict[key] for x in range(len(kwargs['freq']))]
        iter_required = iter(required_kwargs)
        length = len(next(iter_required))
        if all(var in kwargs.keys() for var in iter_required):
            if all(len(l) == length for l in iter_required):
                for x in range(len(kwargs['freq'])):
                    line_dict = {'J1': kwargs['J1'][x], 'Ka1': kwargs['Ka1'][x],
                                 'Kc1': kwargs['Kc1'][x], 'J0': kwargs['J0'][x],
                                 'Ka0': kwargs['Ka0'][x], 'Kc0': kwargs['Kc0'][x],
                                 'QN1_1': kwargs['QN1_1'][x], 'QN2_1': kwargs['QN2_1'][x],
                                 'QN3_1': kwargs['QN3_1'][x], 'QN1_0': kwargs['QN1_0'][x],
                                 'QN2_0': kwargs['QN2_0'][x], 'QN3_0': kwargs['QN3_0'][x],
                                 'freq': kwargs['freq'][x], 'err': kwargs['err'][x],
                                 'wt': kwargs['wt'][x]}
                    if kwargs['freq'][x] in self.dict.keys():
                        self.dict[kwargs['freq'][x]].append(line_dict)
                    else:
                        self.dict[kwargs['freq'][x]] = [line_dict]
                self.update_array()

    def delete_dict_asn(self, freq):
        """
        Delete transition from self.dict. Update self.lin.

        Parameters:
            freq (float):
                Frequency of transition to remove from self.dict.
                Units: MHz.
        """
        self.dict.pop(freq, None)
        self.update_array()

    def delete_array_row(self, row, arr=None):
        """
        Delete a transition from self.lin array. Update self.dict.

        Parameters:
            row (int):
                Row index.
            arr (array):
                Optional array. Use for array other than self.lin.
                Default: self.lin
        """
        if arr is None:
            arr = self.lin
        self.lin = np.delete(arr, row, 0)
        self.update_dict()

    def save(self, fname=None):
        """
        Save *.lin file.

        Parameters:
            fname (str):
                File name.
        """
        if fname is None:
            try:
                fname = self.fname
            except AttributeError:
                fname = 'molecule'
        np.savetxt('{fname}{ext}'.format(fname=fname, ext='.lin'), self.lin, fmt=self.delimiter)


# f = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\Rotational Spectroscopy Data Analysis 4_24_2020\\3_1_2021_Testing\\FinalFit\\old\\fenR_Risop1_a_test.lin'
# # f = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\Rotational Spectroscopy Data Analysis 4_24_2020\\Program Testing\\FinalFit\\old\\fenR_Risop1_a_test.lin'
# lin = Lin(f)
# print(lin.lin[:, 0])

class Int_File:
    """
    Class for Int files

    Attributes:
         fname (str):
            Base name of the file. Not full path.
         fpath (str):
            full file path.
         file (list of str):
            file read into a list.
         dictionary (dictionary):
            flags (int):
                = IRFLG*1000+OUTFLG*100+STRFLG*10+EGYFL
                IRFLG = 1 if constants are in wavenumbers.
                IRFLG = 0 if constants are in MHz.
                OUTFLG = 0 for short form file.out.
                STRFLG = 1,2 to enable file.str output.
                SRFLG = 2 is used to label separate dipole contributions in the file.str output.
                EGYFLG != 0 to enable file.egy energy listing.
                EGYFLG = 2,4 to enable file.egy derivative listing.
                EGYFLG = 3,4 to enable file.egy eigenvector listing.
                EGYFLG = 5 to dump Hamiltonian with no diagonalization.
                Default: 0
            tag (int):
                Catalog species tag.
                Default: 91
            qrot (float):
                Partition function for TEMP.
                Default: None
            fbgn (int):
                Beginning integer F quantum (round up).
                Default: 00
            fend (int):
                Ending integer F quantum (round up).
                Default: 25
            str0 (float):
                Log strength cutoff.
                Default: -10.0
            str1 (float):
                Log strength cutoff.
                Default: -10.0
            fqlim (float):
                Frequency limit.
                Units: GHz
                Default: 18
            temp (float):
                Temperature for intensity calculation.
                Units: K
                Default:1
            maxv (int):
                States with v>MAVX will not be included in the output files of SPCAT.
                Default: 999
            muA (float):
                Dipole component along A principle axis.
                Units: Debye
                Default: 1
            muB (float):
                Dipole component along B principle axis.
                Units: Debye
                Default: 1
            muC (float):
                Dipole component along C principle axis.
                Units: Debye
                Default: 1
            A (float):
                Rotational constant.
                Units: MHz
                Default: None
            B (float):
                Rotational constant.
                Units: MHz
                Default: None
            C (float):
                Rotational constant.
                Units: MHz
                Default: None
    Methods:
        partition_function()
            Calulate the partition function for the given temperature and rotational constants.
        save(fname)
            Save *.int file in the proper format.
    """
    default_dict = {
        'flags': 0, 'tag': 91, 'fbgn': 00, 'fend': 25, 'str0': -10.0, 'str1': -10.0, 'fqlim': 18,
        'temp': 1, 'maxv': None, 'muA': 1, 'muB': 1, 'muC': 1, 'A': None, 'B': None, 'C': None}

    def __init__(self, file=None, **kwargs):
        variables = ['flags', 'tag', 'fbgn', 'fend', 'str0', 'str1', 'fqlim', 'temp', 'maxv',
                     'muA', 'muB', 'muC', 'A', 'B', 'C']
        self.dict = {}
        if file is None:
            for variable in variables:
                if variable in kwargs.keys():
                    self.dict[variable] = kwargs[variable]
                else:
                    self.dict[variable] = Int_File.default_dict[variable]
            self.partition_function()
        else:
            self.fname = os.path.basename(str(file)).split('.')[0]
            self.fpath = os.path.abspath(str(file))
            with open(file, "r") as f:
                self.file = [row for row in f]
            f.close()
            split_file = [row.split() for row in self.file]
            first_elements = [row[0] for row in split_file]
            flags = (
                ('flags', 1, 0), ('tag', 1, 1), ('qrot', 1, 2), ('fgbn', 1, 3), ('fend', 1, 4),
                ('str0', 1, 5), ('str1', 1, 6), ('fqlim', 1, 7), ('temp', 1, 8), ('maxv', 1, 9),
                ('muA', first_elements.index('001'), 1), ('muB', first_elements.index('002'), 1),
                ('muC', first_elements.index('003'), 1))
            for flag, row, col in flags:
                try:
                    self.dict[flag] = str(split_file[row][col])
                except IndexError:
                    self.dict[flag] = None

    def partition_function(self):
        """ Calulate the partition function for the given temperature and rotational constants. """
        keys = ['temp', 'A', 'B', 'C']
        for key in keys:
            if self.dict[key] is None:
                print('Must provide ' + str(key) + ' to calculate partition function')
                return
        qrot = (5.3311 * 10 ** 6) * (self.dict['temp'] ** 1.5) * (
                float(self.dict['A']) * float(self.dict['B']) * float(self.dict['C'])) ** (-0.5)
        self.dict['qrot'] = qrot
        return qrot

    def save(self, fname=None):
        """
        Save *.int file in the proper format.

        Parameters:
            fname (str):
                File name.
                Default: molecule
        """
        dipole_key = {'muA': '001', 'uA': '001', 'A': '001', 'muB': '002', 'uB': '002', 'B': '002',
                      'muC': '003', 'uC': '003', 'C': '003'}
        muA = self.dict['muA'] if self.dict['muA'] is not None else ''
        muB = self.dict['muB'] if self.dict['muB'] is not None else ''
        muC = self.dict['muC'] if self.dict['muC'] is not None else ''

        flags = self.dict['flags'] if self.dict['flags'] is not None else ''
        tag = self.dict['tag'] if self.dict['tag'] is not None else ''
        self.partition_function()
        qrot = self.dict['qrot'] if self.dict['qrot'] is not None else ''
        fbgn = self.dict['fbgn'] if self.dict['fbgn'] is not None else ''
        fend = self.dict['fend'] if self.dict['fend'] is not None else ''
        str0 = self.dict['str0'] if self.dict['str0'] is not None else ''
        str1 = self.dict['str1'] if self.dict['str1'] is not None else ''
        fqlim = self.dict['fqlim'] if self.dict['fqlim'] is not None else ''
        temp = self.dict['temp'] if self.dict['temp'] is not None else ''
        maxv = self.dict['maxv'] if self.dict['maxv'] is not None else ''

        if fname is None:
            try:
                fname = self.fname
            except AttributeError:
                fname = 'molecule'
        else:
            fname = fname
        int_file = ""
        int_file += "{fname} \n".format(fname=fname)
        int_file += "{flags}  {tag}  {qrot}  {fbgn}  {fend}  {str0}  {str1}  {fqlim}  {temp}  " \
                    "{maxv} \n".format(flags=flags, tag=tag, qrot=qrot, fbgn=fbgn, fend=fend,
                                       str0=str0, str1=str1, fqlim=fqlim, temp=temp, maxv=maxv)
        dipoles = (('muA', muA), ('muB', muB), ('muC', muC))
        for key, dipole in dipoles:
            int_file += " {key}  {dipole} \n".format(key=dipole_key[key], dipole=dipole)
        with open('{fname}{ext}'.format(fname=fname, ext='.int'), 'w') as f:
            for row in int_file:
                f.write(row)
        f.close()


class Cat:
    """
    Class for Piform output files. Accepted file extension: *.pi

    Attributes:
        delimiter (list of str):
            List of column spacings.
            Default:    ['%3.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f',
                        '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%12.4f', '%12.6f', '%12.2E']
        fname (str):
           Base name of the file. Not full path.
        fpath (str):
           Full file path.
        cat (array):
           File read into numpy array.
        dict (dictionary):
            freq (float):
               Transition frequency.
            err (float):
               Estimated or experimental error.
               Units: MHz
            lgint (float):
               Base 10 logarithm of the integrated intensity.
               Units: nm^2 MHz
            dr (int):
               Degrees of freedom in the rotational partition function
            elo (float):
               Lower state energy.
               Units: wavenumbers
            gup (int):
               Upper state degeneracy
            tag (int):
               Species tag or molecular identifier
            qnfmt (int):
               Identifies the format of the quantum numbers given in the field QN
            N1, Ka1, Kc1, J1, F11, F1, N0, Ka0, Kc0, J0, F10, F0 (int):
               Quantum numbers
    Methods:
        line_list(dictionary)
            Return two column array. Col[0]: frequency, col[1]: intensity.
        max_intensity(dictionary)
            Return frequency and intensity of the strongest predicted transition.
        filter(dictionary)
            Filter transitions by various parameters.
        simulate(line_list, freq_min, freq_max, step_size, fwhm, scale_factor, save, fname, **kw)
            Produce a simulated spectrum from the given line_list.
        spectrum_matches(spec_pp, dictionary, thresh)
            Return line positions of predicted and experimental transitions that satisfy threshold.
        scale_to_spectrum(spectrum, asn, dictionary, thresh)
            Return scale factor that scales the intensity of the predicted spectrum to match an
            experimental spectrum.
    """

    def __init__(self, file=None):
        self.delimiter = ['%13.4f', '%8.4f', '%8.4f', '%2.0f', '%10.4f', '%3.0f', '%7.0f',
                          '%4.0f', '%2.0f', '%2.0f', '%2.0f', '%8.0f', '%2.0f', '%2.0f']
        if file is not None:
            self.fname = os.path.basename(str(file)).split('.')[0]
            self.fpath = os.path.abspath(str(file))
            self.cat = np.genfromtxt(
                file, delimiter=[13, 8, 8, 2, 10, 3, 7, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
            freq = self.cat[:, 0]
            err = self.cat[:, 1]
            lgint = self.cat[:, 2]
            dr = self.cat[:, 3]
            elo = self.cat[:, 4]
            gup = self.cat[:, 5]
            tag = self.cat[:, 6]
            qnfmt = self.cat[:, 7]
            N1 = self.cat[:, 8]
            Ka1 = self.cat[:, 9]
            Kc1 = self.cat[:, 10]
            J1 = self.cat[:, 11]
            F11 = self.cat[:, 12]
            F1 = self.cat[:, 13]
            N0 = self.cat[:, 14]
            Ka0 = self.cat[:, 15]
            Kc0 = self.cat[:, 16]
            J0 = self.cat[:, 17]
            F10 = self.cat[:, 18]
            F0 = self.cat[:, 19]

            self.dict = {}
            for x in range(len(freq)):
                line_dict = {
                    'freq': float(freq[x]), 'err': float(err[x]), 'lgint': float(lgint[x]),
                    'dr': int(dr[x]), 'elo': float(elo[x]), 'gup': int(gup[x]), 'tag': int(tag[x]),
                    'qnfmt': int(qnfmt[x]), 'N1': int(N1[x]), 'Ka1': int(Ka1[x]),
                    'Kc1': int(Kc1[x]), 'J1': J1[x], 'F11': F11[x], 'F1': F1[x], 'N0': int(N0[x]),
                    'Ka0': int(Ka0[x]), 'Kc0': int(Kc0[x]), 'J0': J0[x], 'F10': F10[x], 'F0': F0[x]}
                if freq[x] in self.dict.keys():
                    self.dict[freq[x]].append(line_dict)
                else:
                    self.dict[freq[x]] = [line_dict]

    def line_list(self, dictionary=None):
        """
        Return array of transition frequencies and predicted intensities.

        Parameters:
            dictionary (dictionary):
                Optional dictionary. Use for dict other than self.dict.
        Return:
            line_list (array):
                 Col[0]: frequency
                    Units: MHz
                 col[1]: intensity.
                    Units: mV
        """
        if dictionary is None:
            dictionary = self.dict
        freq = []
        intens = []
        for k, v in dictionary.items():
            for line in v:
                freq.append(k)
                intens.append(10 ** line['lgint'])
        line_list = np.column_stack((freq, intens))
        return line_list

    def max_intensity(self, dictionary=None):
        """
        Return frequency and intensity of the strongest predicted transition.

        Parameters:
            dictionary (dictionary):
                Optional dictionary. Use for dict other than self.dict.
        Return:
            max_int (array):
                Frequency and intensity of the strongest transition.
                Units: MHz and mV
        """
        if dictionary is None:
            dictionary = self.dict
        line_list = self.line_list(dictionary)
        max_int = line_list[np.argmax(line_list[:, 1]), :]
        return max_int

    def filter(self, dictionary=None, **kwargs):
        """
        Filter rows of the cat by various parameters.

        Parameters:
            dictionary (dictionary):
                Optional dictionary. Use for dict other than self.dict.
            kwargs['freq_max'] (int):
                Upper bound frequency.
                Units: MHz.
            kwargs['freq_min'] (int):
                Lower bound frequency.
                Units: MHz.
            kwargs['N_max'] (int):
                Upper bound N quantum number.
            kwargs['N_min'] (int):
                Lower bound  N quantum number.
            kwargs['Ka_max'] (int):
                Upper bound K prolate quantum number.
            kwargs['Ka_min'] (int):
                Lower bound K prolate quantum number.
            kwargs['Kc_max'] (int):
                Upper bound K oblate quantum number.
            kwargs['Kc_min'] (int):
                Lower bound K oblate quantum number.
            kwargs['J_max'] (int):
                Upper bound J quantum number.
            kwargs['J_min'] (int):
                Lower bound J quantum number.
            kwargs['F1_max'] (int):
                Upper bound F1 quantum number.
            kwargs['F1_min'] (int):
                Lower bound F1 quantum number.
            kwargs['F_max'] (int):
                Upper bound F quantum number.
            kwargs['F_min'] (int):
                Lower bound F quantum number.
            kwargs['dyn_range'] (float):
                dynamic range with respect to the strongest peak.
        Return:
            filtered (dictionary):
                Key:val pairs from input dictionary which meet filter requirements.
        """
        kwarg_dict = {'freq_max': 'freq', 'N_max': 'N1', 'Ka_max': 'Ka1', 'Kc_max': 'Kc1',
                      'J_max': 'J1', 'F1_max': 'F11', 'F_max': 'F1',
                      'freq_min': 'freq', 'N_min': 'N1', 'Ka_min': 'Ka1', 'Kc_min': 'Kc1',
                      'J_min': 'J1', 'F1_min': 'F11', 'F_min': 'F1', 'dyn_range': 'dyn_range'}
        max_kwargs = ['freq_max', 'N_max', 'Ka_max', 'Kc_max', 'J_max', 'F1_max', 'F_max']
        min_kwargs = ['freq_min', 'N_min', 'Ka_min', 'Kc_min', 'J_min', 'F1_min', 'F_min']
        dyn_range = ['dyn_range']
        if dictionary is None:
            filtered = dict(self.dict)
        else:
            filtered = dict(dictionary)
        delete_list = []
        for freq, lines in filtered.items():
            for line in lines:
                for key, param in kwargs.items():
                    if key not in ['None', None]:
                        if key in max_kwargs:
                            if float(line[kwarg_dict[key]]) > float(kwargs[key]):
                                delete_list.append(freq)
                        if key in min_kwargs:
                            if float(line[kwarg_dict[key]]) < float(kwargs[key]):
                                delete_list.append(freq)
                        if key in dyn_range:
                            max_int = self.max_intensity()
                            lower_limit = max_int[1] / float(kwargs[key])
                            if float(10 ** line['lgint']) < lower_limit:
                                delete_list.append(freq)
        for key in delete_list:
            try:
                del filtered[key]
            except KeyError:
                pass
        return filtered

    def simulate(self, line_list=None, freq_min=None, freq_max=None, step_size=None, fwhm=None,
                 scale_factor=None, save=False, fname=None):
        """
        Simulate spectrum using the given line_list.

        Parameters:
            line_list (array):
                Two column arraycontaining frequencies and intensities for the desired Peaks.
                Col[0]: frequencies.
                    Units: MHz
                Col[1]: Intensities.
                    Units: mV
            freq_min (int):
                Lower bound of the simulation
                Units: MHz
                Default:  2000
            freq_max (int):
                Upper bound of the simulation
                Units: MHz.
                Default:  8000
            step_size (float):
                Point spacing
                Units: MHz.
                Default:  0.0125
            fwhm (float):
                FWHM line width
                Units: MHz.
                Default: 0.060
            scale_factor (float):
                Scale factor applied to the y-axis.
                Default:  None.
            save (bool):
                Option to save output to external file.
                Default: False
            fname(str):
                File name, if save=True.
        Return:
            simulation (array):
                Two column array.
                Col[0]: freq.
                Col[1]: intensity
        """
        if line_list is None:
            line_list = self.line_list()
        sim = Spectrum.simulate_spectrum(
            line_list, freq_min=freq_min, freq_max=freq_max, step_size=step_size, fwhm=fwhm,
            scale_factor=scale_factor, save=save, fname=fname)
        return sim

    def spectrum_matches(self, spec_pp, dictionary=None, thresh=None):
        """
        Return transition frequencies for predicted and experimental transitions that meet the
        cutoff threshold.

        Parameters:
            spec_pp (list):
                Peak pick of an experimental spectrum.
            dictionary (dict):
                Cat dictionary (filtered or unfiltered).
                Default: self.dict
            thresh (float):
                Max frequency difference for a predicted and experimental peak to be classified as
                a match.
                Units: MHz.
                Default: 0.020
        Return:
             cat_freq (list):
                List of match frequencies from cat file.
             spec_freq (list):
                List of match frequencies from experimental spectrum.
        """

        if dictionary is None:
            dictionary = self.dict
        if thresh is None:
            thresh = 0.020
        cat_freqs = list(dictionary.keys())
        spec_freqs = spec_pp[:, 0]
        cat_freq = []
        spec_freq = []
        for x in spec_freqs:
            for y in cat_freqs:
                if (y + thresh) >= x >= (y - thresh):
                    cat_freq.append(y)
                    spec_freq.append(round(x, 4))
        return cat_freq, spec_freq

    def scale_to_spectrum(self, spectrum, asn, dictionary=None, thresh=None):
        """
        Return scale factor that scales the intensity of the predicted spectrum to match an
        experimental spectrum.

        Parameters:
            spectrum (Spectrum class obj):
                Spectrum object with potential matches.
            asn (list):
                List of assigned transition frequencies in the experimental spectrum.
            dictionary (dict):
                Cat dictionary (filtered or unfiltered).
                Default: self.dict
            thresh (float):
                Maximum allowed frequency difference for a predicted and experimental peak to be
                classified as a match.
                Units: MHz.
                Default:  0.010
        Returns:
            scale_factor (float):
                Scale factor that, when applied to cat sim, matches experimental spectrum intensity
                (on average).
         """
        if dictionary is None:
            dictionary = self.dict
        if thresh is None:
            thresh = 0.010
        cat_lnlst = self.line_list(dictionary)
        cat_lnlst = np.array(
            [cat_lnlst[x, :] for x in range(len(cat_lnlst)) for y in range(len(asn)) if
             (cat_lnlst[x, 0] + thresh) >= asn[y] >= (cat_lnlst[x, 0] - thresh)])
        exp_intens = []
        cat_intens = []
        for x in range(len(cat_lnlst)):
            freq = cat_lnlst[x, 0]
            try:
                exp_intens.append(spectrum.get_intensity(freq))
                cat_intens.append(cat_lnlst[x, 1])
            except (KeyError, IndexError):
                pass
        intens = np.column_stack((cat_intens, exp_intens))
        intens = np.array([intens[x, :] for x in range(len(intens)) if intens[x, 1] != 0])
        scale_factors = [intens[x, 1] / intens[x, 0] for x in range(len(intens))]

        zscore_check = True
        while zscore_check:
            sf_mean = np.mean(scale_factors)
            sf_stdev = np.std(scale_factors)
            z_min = sf_mean - 3 * sf_stdev
            z_max = sf_mean + 3 * sf_stdev
            len_1 = len(scale_factors)
            scale_factors = [
                scale_factor for scale_factor in scale_factors if z_min <= scale_factor <= z_max]
            len_2 = len(scale_factors)
            if len_1 == len_2:
                zscore_check = False
        scale_factor = np.mean(scale_factors)
        return scale_factor

# c = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\Rotational Spectroscopy Data Analysis 4_24_2020\\3_1_2021_Testing\\FinalFit\\test_RR_1d.cat'
# cat = Cat(c)
# f = cat.cat


class Piform:
    """
    Class for Piform output files. Accepted file extension: *.pi

    Attributes:
         fname (str):
            Base name of the file. Not full path.
         fpath (str):
            Full file path
         file (list of str):
            File read into a list.
         split_file (list of list of str):
            Similar to file, but each line is split.
         dict (dict):
             bad_constants (list of str):
                Constants with greater than 20% uncertainty.
             rms (float):
                Root mean square of fit.
                Units: MHz
             distinct_freq (int):
                Number of distinct line positions.
             distinct_param (int):
                Number of constants in fit.
             rigid rotor constants:
                Numerical values
                Units: MHz
             quartic distortion constants:
                Numerical values
                Units: MHz
             quadrupolar constants:
                Numerical values
                Units: MHz
             errors associated with each constant:
                Numerical values
                Units: MHz
    Methods:
        qdc_check()
            Compare quartic distortion constants with their uncertainties. Removes val from fit
            if magnitude of uncertainty is greater than the magnitude of the val itself.
        const_err_str(constant)
            Returns "constant (uncertainty)"  Ex. 0.0275(12).
        line_list_split(num_qn)
            Split assigned transition section into quantum numbers, freqencies, and
            obs - calc values.
        line_list_LaTeX(num_qns, caption, preamble, save, fname, **kw)
            Generate LaTeX table of assigned transitions from the piform file. Includes quantum
            numbers, frequencies, and obs. - calc. values for each assigned transition.
        rot_const_LaTeX(num_qns, caption, preamble, save, fname, **kw)
            Generate LaTeX table of rotational constants. Includes rotational constants, of
            assigned transitions, and RMS of the fit.
        save_LaTeX_table(fname, type, **kw)
            Generate and save LaTeX tables.
    """

    def __init__(self, file=None):
        if file is not None:
            self.fname = os.path.basename(str(file))
            self.fpath = os.path.abspath(str(file))
            with open(file, "r") as f:
                self.file = f.readlines()
            f.close()
            self.split_file = [row.split() for row in self.file]
            self.dict = {}
            try:
                start = ' Worst fitted constants, with greater than 20% uncertainty:' \
                        '                            %\n'
                bad_consts = self.file[(self.file.index(start) + 2):]
                stop = '------------------------------------------------------------------------' \
                       '------------------\n'
                bad_consts = bad_consts[:(bad_consts.index(stop))]
                self.dict['bad_constants'] = [str(bad_consts[x]).split()[0] for x in
                                              range(len(bad_consts))]
            except (ValueError, IndexError):
                self.dict['bad_constants'] = None
            try:
                start = ' Worst fitted lines (obs-calc/error):\n'
                worst_lines = self.file[(self.file.index(start) + 2):]
                worst_line = worst_lines[worst_lines.index('\n') + 1]
                self.worst_line = worst_line.split()
            except ValueError:
                pass
            file_reversed = [row for row in reversed(self.file)]
            stop_i = '---------------------------------------------------------------------------' \
                     '----------=========\n'
            stop = file_reversed.index(stop_i) + 1
            start = file_reversed.index(
                ' PARAMETERS IN FIT WITH STANDARD ERRORS ON THOSE THAT ARE FITTED:\n') + 3

            final_fit_iter = [row for row in reversed(file_reversed[start:stop])]
            self.line_list = final_fit_iter[1:final_fit_iter.index('\n') - 1]
            final_fit_iter = final_fit_iter[final_fit_iter.index('\n') + 3:]
            self.rotational_constants = final_fit_iter[:final_fit_iter.index('\n')]
            rc = [row.split() for row in self.rotational_constants]
            const_key = [rc[x][0] for x in range(len(rc))]
            final_fit_iter = final_fit_iter[final_fit_iter.index('\n') + 2:]
            self.dict['rms'] = float(final_fit_iter[0].split()[3])
            self.dict['distinct_freq'] = int(final_fit_iter[3].split()[5])
            self.dict['distict_param'] = int(final_fit_iter[4].split()[4])
            key_dict = {
                '10000': ['a', 'a_err'], '20000': ['b', 'b_err'], '30000': ['c', 'c_err'],
                '200': ['DJ', 'DJ_err'], '1100': ['DJK', 'DJK_err'], '2000': ['DK', 'DK_err'],
                '40100': ['dJ', 'dJ_err'], '41000': ['dK', 'dK_err'],
                '110010000': ['chi_aa_1', 'chi_aa_1_err'],
                '110040000': ['chi_bbcc_1', 'chi_bbcc_1_err'],
                '110610000': ['chi_ab_1', 'chi_ab_1_err'],
                '110210000': ['chi_bc_1', 'chi_bc_1_err'],
                '110410000': ['chi_ac_1', 'chi_ac_1_err'],
                '220010000': ['chi_aa_2', 'chi_aa_2_err'],
                '220040000': ['chi_bbcc_2', 'chi_bbcc_2_err'],
                '220610000': ['chi_ab_2', 'chi_ab_2_err'],
                '220210000': ['chi_bc_2', 'chi_bc_2_err'],
                '220410000': ['chi_ac_2', 'chi_ac_2_err'],
                '330010000': ['chi_aa_3', 'chi_aa_3_err'],
                '330040000': ['chi_bbcc_3', 'chi_bbcc_3_err'],
                '330610000': ['chi_ab_3', 'chi_ab_3_err'],
                '330210000': ['chi_bc_3', 'chi_bc_3_err'],
                '330410000': ['chi_ac_3', 'chi_ac_3_err']}
            for param in key_dict.keys():
                vars = key_dict[str(param)]
                try:
                    const_err = rc[const_key.index(param)][2]
                    split = const_err.split(sep=')')
                    split = split[0].split(sep='(')
                    self.dict[vars[0]] = str(split[0])
                    self.dict[vars[1]] = str(int(split[1]))
                except ValueError:
                    self.dict[vars[0]] = None  # '[0.]'
                    self.dict[vars[1]] = None  # '0'
                except IndexError:
                    if const_err == '[':
                        const_err = rc[const_key.index(param)][2:4]
                        const_err = ''.join(const_err)
                        self.dict[vars[0]] = str(const_err)
                        self.dict[vars[1]] = str(0)

    def qdc_check(self):
        """
        Compare quartic distortion constants with respective uncertainty.

        Remove constant from fit if uncertainty is greater than the magnitude of the constant
        itself.

        Returns:
            constants (list):
                List of labels that fail the check and should be removed from par file.
        """
        qdcs = ['DJ', 'DJK', 'DK', 'dJ', 'dK']
        failed = []
        for qdc in qdcs:
            if self.dict[qdc] in [None, '[0.]', '[ 0.]', '[0]']:
                continue
            else:
                qdc_err = self.const_err_str(qdc)
                t_f = uncertainty_check(qdc_err)
                if not t_f:
                    failed.append(qdc)
        return failed

    def const_err_str(self, constant):
        """
        Return constant and uncertainty in parentheses as a string.

        Parameters:
            constant (str):
                Ex. A, B, C, DJ, etc.. . .
        Returns:
            val (str):
                Ex. 0.0275(12)
        """
        error = constant + '_err'
        val = str(self.dict[constant]) + '(' + str(self.dict[error]) + ')'
        return val

    def line_list_split(self, num_qn):
        """
        Split final section of assignments into quantum numbers, freqencies, and obs - calc values.

        Parameters:
            num_qn (int):
                Number of quantum numbers assigned in the fit.
        Returns:
            qns (list):
                Quantum numbers
            freqs (list):
                Frequencies
            o_c (list):
                Obs - calc.
        """
        num_col = num_qn * 2
        qn_section = [row.split() for row in self.line_list]
        qns = []
        freqs = []
        o_c = []
        for row in qn_section:
            count = 0
            for x in row:
                x_list = list(x)
                count += 1
                if x_list[-1] == ':':
                    break
                else:
                    continue
            qns.append(row[count:count + num_col])
            freqs.append(row[count + num_col])
            o_c.append(row[count + num_col + 1])
        qns = np.array(qns)
        freqs = np.array(freqs)
        o_c = np.array(o_c)
        return qns, freqs, o_c

    def line_list_LaTeX(self, num_qns, caption=None, preamble=False, save=False, fname=None,
                        **kwargs):
        """
        Generate a LaTeX table with assigned transitions from the piform file.

        Table includes quantum numbers, frequencies, and obs. - calc. values for each assigned
        transition.

        Parameters:
            num_qns (int):
                Number of quantum numbers that are assigned in the fit.
            caption (str):
                Optional table caption.
            preamble (bool):
                Set whether preamble is placed at the start of a new LaTeX document. If adding a
                table to an existing document, omit preamble.
                Default: False
            save (bool):
                Save output.
                Default: False
            fname (str):
                File name if file is saved.
                Default: line_list_latex.tex
        Returns:
            latex (str):
                String that produces formatted table when compiled in LaTeX.
        """
        df = pd.DataFrame()
        qns, freqs, oc = self.line_list_split(num_qns)
        if preamble:
            preamble = \
                "\\documentclass[10pt]{article} \n" \
                "\\usepackage{cellspace, array, longtable, booktabs, floatrow} \n" \
                "\t\\setlength\\cellspacetoplimit{2pt} \n" \
                "\t\\setlength\\cellspacebottomlimit{2pt} \n" \
                "\t\\floatsetup[longtable]{LTcapwidth=table} \n" \
                "\\usepackage[margin=0.5in]{geometry} \n" \
                "\\usepackage[labelfont=bf]{caption} \n" \
                "\t\\captionsetup[longtable]{justification=raggedright, singlelinecheck=off} \n" \
                "\n" \
                "\\begin{document} \n" \
                "\\begin{center} \n"
        if qns.shape[1] == 6:
            colfmt = "Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc " \
                     ">{\\centering\\arraybackslash}m{2cm} >{\\centering\\arraybackslash}m{2cm}"
            columns = \
                ["$J^{''}$", "$K_{a}^{''}$", "$K_{c}^{''}$",
                 "$\\leftarrow$",
                 "$J^{'}$", "$K_{a}^{'}$", "$K_{c}^{'}$",
                 "\\multicolumn{1}{m{2cm}}{\\centering $\\nu_{obs.}$ \\\\ \\emph{(MHz)}}",
                 "\\multicolumn{1}{m{2cm}}{\\centering $\\nu_{obs}. - \\nu_{calc.}$ \\\\ "
                 "\\emph{(MHz)}}"]
            df[columns[0]] = qns[:, 0]
            df[columns[1]] = qns[:, 1]
            df[columns[2]] = qns[:, 2]
            df[columns[3]] = " "
            df[columns[4]] = qns[:, 3]
            df[columns[5]] = qns[:, 4]
            df[columns[6]] = qns[:, 5]
            df[columns[7]] = freqs[:]
            df[columns[8]] = oc[:]
        if qns.shape[1] == 8:
            colfmt = "Sc Sc Sc Sc Sc Sc Sc Sc Sc >{\\centering\\arraybackslash}m{2cm} " \
                     ">{\\centering\\arraybackslash}m{2cm}"
            columns = ["$J^{''}$", "$K_{a}^{''}$", "$K_{c}^{''}$", "$F^{''}$",
                       "$\\leftarrow$",
                       "$J^{'}$", "$K_{a}^{'}$", "$K_{c}^{'}$", "$F^{'}$",
                       "\\multicolumn{1}{m{2cm}}{\\centering $\\nu_{obs.}$ \\\\ \\emph{(MHz)}}",
                       "\\multicolumn{1}{m{2cm}}{\\centering $\\nu_{obs}. - \\nu_{calc.}$ \\\\ "
                       "\\emph{(MHz)}}"]
            df[columns[0]] = qns[:, 0]
            df[columns[1]] = qns[:, 1]
            df[columns[2]] = qns[:, 2]
            df[columns[3]] = qns[:, 3]
            df[columns[4]] = " "
            df[columns[5]] = qns[:, 4]
            df[columns[7]] = qns[:, 5]
            df[columns[8]] = qns[:, 6]
            df[columns[5]] = qns[:, 7]
            df[columns[7]] = freqs[:]
            df[columns[8]] = oc[:]
        if qns.shape[1] == 10:
            colfmt = "Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc >{\\centering\\arraybackslash}m{2cm} " \
                     ">{\\centering\\arraybackslash}m{2cm}"
            columns = ["$J^{''}$", "$K_{a}^{''}$", "$K_{c}^{''}$", "$I^{''}$", "$F^{''}$",
                       "$\\leftarrow$",
                       "$J^{'}$", "$K_{a}^{'}$", "$K_{c}^{'}$", "$I^{'}$", "$F^{'}$",
                       "\\multicolumn{1}{m{2cm}}{\\centering $\\nu_{obs.}$ \\\\ \\emph{(MHz)}}",
                       "\\multicolumn{1}{m{2cm}}{\\centering $\\nu_{obs}. - \\nu_{calc.}$ \\\\ "
                       "\\emph{(MHz)}}"]
            df[columns[0]] = qns[:, 0]
            df[columns[1]] = qns[:, 1]
            df[columns[2]] = qns[:, 2]
            df[columns[3]] = qns[:, 3]
            df[columns[4]] = qns[:, 4]
            df[columns[5]] = ' '
            df[columns[6]] = qns[:, 5]
            df[columns[7]] = qns[:, 6]
            df[columns[8]] = qns[:, 7]
            df[columns[9]] = qns[:, 8]
            df[columns[10]] = qns[:, 9]
            df[columns[11]] = freqs[:]
            df[columns[12]] = oc[:]
        if qns.shape[1] == 12:
            colfmt = \
                "Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc Sc >{\\centering\\arraybackslash}m{2cm} " \
                ">{\\centering\\arraybackslash}m{2cm}"
            columns = ["$J^{''}$", "$K_{a}^{''}$", "$K_{c}^{''}$", "$I^{''}$", "$F_{1}^{''}$",
                       "$F^{''}$", "$\\leftarrow$",
                       "$J^{'}$", "$K_{a}^{'}$", "$K_{c}^{'}$", "$I^{'}$", "$F_{1}^{'}$", "$F^{'}$",
                       "\\multicolumn{1}{m{2cm}}{\\centering $\\nu_{obs.}$ \\\\ \\emph{(MHz)}}",
                       "\\multicolumn{1}{m{2cm}}{\\centering $\\nu_{obs}. - \\nu_{calc.}$ \\\\ "
                       "\\emph{(MHz)}}"]
            df[columns[0]] = qns[:, 0]
            df[columns[1]] = qns[:, 1]
            df[columns[2]] = qns[:, 2]
            df[columns[3]] = qns[:, 3]
            df[columns[4]] = qns[:, 4]
            df[columns[5]] = qns[:, 5]
            df[columns[6]] = ' '
            df[columns[7]] = qns[:, 6]
            df[columns[8]] = qns[:, 7]
            df[columns[9]] = qns[:, 8]
            df[columns[10]] = qns[:, 9]
            df[columns[11]] = qns[:, 10]
            df[columns[12]] = qns[:, 11]
            df[columns[13]] = freqs[:]
            df[columns[14]] = oc[:]
        latex = df.to_latex(index=False, escape=False, column_format=colfmt, longtable=True,
                            caption=caption, **kwargs)
        if preamble:
            latex = preamble + latex + '\n\\end{center} \n\\end{document}'
        if save:
            if fname is None:
                fname = 'line_list_latex.tex'
            with open(fname, 'w') as f:
                f.write(latex)
        return latex

    def rot_const_LaTeX(self, num_qns, caption=None, show_zero_qdc=False, preamble=False,
                        save=False, fname=None, **kwargs):
        """
        Generate a table in LaTeX formatting with rotational constants from piform file.

        Table includes rotational constants, number of assigned transitions, and RMS of the fit.

        Parameters:
            num_qns (int):
                Number of quantum numbers that are assigned in fit.
            caption (str):
                Optional table caption.
            show_zero_qdc (bool):
                Sets whether zero-valued quartic distortion constants are included.
            preamble (bool):
                Set whether preamble is placed at the start of a new LaTeX document. If adding a
                table to an existing document, omit preamble.
                Default: False
            save (bool):
                Save the output to a file.
                Default: False
            fname (str):
                File name if file is saved.
                Default: 'rot_const_latex.tex'
        Returns:
            latex (str):
                String that produces formatted table when compiled in LaTeX.
        """
        df = pd.DataFrame()
        if preamble:
            preamble = "\\documentclass[10pt]{article} \n" \
                       "\\renewcommand{\\familydefault}{\\sfdefault} \n" \
                       "\\usepackage{booktabs, array} \n" \
                       "\\usepackage[labelfont=bf, singlelinecheck=false]{caption} \n" \
                       "\t\\captionsetup[table]{justification=raggedright, " \
                       "singlelinecheck=off} \n" \
                       "\\usepackage{floatrow} \n" \
                       "\t\\floatsetup[table]{capposition=top, objectset=raggedright, " \
                       "margins=raggedright, midcode=captionskip, captionskip=10pt} \n" \
                       "\\usepackage[margin=0.5in]{geometry} \n" \
                       "\n" \
                       "\\begin{document} \n"
        rcs = [('a', '\\emph{A / MHz.}'), ('b', '\\emph{B / MHz.}'), ('c', '\\emph{C / MHz.}'),
               ('DJ', '\\emph{$\\Delta_{J}$ / kHz}'), ('DJK', '\\emph{$\\Delta_{JK}$ / kHz.}'),
               ('DK', '\\emph{$\\Delta_{K}$ / kHz}'), ('dJ', '\\emph{$\\delta_{J}$ / kHz.}'),
               ('dK', '\\emph{$\\delta_{K}$ / kHz}'),
               ('chi_aa_1', '\\emph{$\\chi_{aa1}$ / MHz}'),
               ('chi_bbcc_1', '\\emph{$\\chi_{bbcc1}$ / MHz}'),
               ('chi_ab_1', '\\emph{$\\chi_{ab1}$ / MHz}'),
               ('chi_bc_1', '\\emph{$\\chi_{bc1}$ / MHz}'),
               ('chi_ac_1', '\\emph{$\\chi_{ac1}$ / MHz}'),
               ('chi_aa_2', '\\emph{$\\chi_{aa2}$ / MHz}'),
               ('chi_bbcc_2', '\\emph{$\\chi_{bbcc2}$ / MHz}'),
               ('chi_ab_2', '\\emph{$\\chi_{ab2}$ / MHz}'),
               ('chi_bc_2', '\\emph{$\\chi_{bc2}$ / MHz}'),
               ('chi_ac_2', '\\emph{$\\chi_{ac2}$ / MHz}'),
               ('chi_aa_3', '\\emph{$\\chi_{aa3}$ / MHz}'),
               ('chi_bbcc_3', '\\emph{$\\chi_{bbcc3}$ / MHz}'),
               ('chi_ab_3', '\\emph{$\\chi_{ab3}$ / MHz}'),
               ('chi_bc_3', '\\emph{$\\chi_{bc3}$ / MHz}')
               ]
        qdcs = ['DJ', 'DJK', 'DK', 'dJ', 'dK']
        consts = []
        for rc, label in rcs:
            if rc in qdcs:
                if show_zero_qdc:
                    try:
                        const = move_decimal(self.dict[rc], 3)
                        err = self.dict[rc + '_err']
                        consts.append([label, str(const) + '(' + str(err) + ')'])
                    except (TypeError, ValueError):
                        const = '[0.]'
                        consts.append([label, str(const)])
                else:
                    try:
                        const = move_decimal(self.dict[rc], 3)
                        err = self.dict[rc + '_err']
                    except (ValueError, TypeError):
                        continue
                    consts.append([label, str(const) + '(' + str(err) + ')'])
            else:
                if self.dict[rc] not in [None, 0, '[0.]']:
                    const = self.dict[rc]
                    err = self.dict[rc + '_err']
                    consts.append([label, str(const) + '(' + str(err) + ')'])
                else:
                    continue
        qns, freqs, o_c = self.line_list_split(num_qns)
        rms = move_decimal(self.dict['rms'], 3)
        consts.append(('\\emph{$N$}', len(qns)))
        consts.append(('\\emph{$rms$} / kHz', rms))
        consts = np.array(consts)
        columns = [" ", "\\emph{Experimental}"]
        df[columns[0]] = consts[:, 0]
        df[columns[1]] = consts[:, 1]
        colfmt = ">{\\raggedright\\arraybackslash}b{3cm} >{\\centering\\arraybackslash}b{4cm}"
        latex = df.to_latex(index=False, escape=False, column_format=colfmt, caption=caption,
                            **kwargs)
        if preamble:
            latex = preamble + latex + '\n\\end{document}'
        if save:
            if fname is None:
                fname = 'rot_const_latex.tex'
            with open(fname, 'w') as f:
                f.write(latex)
        return latex


def move_decimal(number, decimal_places):
    """
    Take a float represented as a string, move decimal, and return as a string.

    Useful for tkinter Entry widgets, allowing you to use a tk.StringVar variable instead of a
    tk.DoubleVar variable. You can also set the default to "None" or display an error message.
    Handles moving a decimal within a string rather than a float.

    Parameters:
        number (str or tk.StringVar):
            String of characters that could be interpretted as a float.
        decimal_places (int):
            Number of decimal places to move the decimal. Positive values move the decimal to the
            right, and negative values move the decimal to the left.
    Returns:
        new_val (str):
            New string with decimal moved.
    """
    dc = list(str(number))
    skip = ['0', '-', '.']
    index = 0
    while True:
        if dc[index] in skip:
            index += 1
        else:
            break
    keeps = dc[index:]
    for x in keeps:
        if x == '.':
            keeps.remove(x)
    sigfigs = len(keeps)
    sci_notation = '{:e}'.format(float(number))
    sci_notation_split = sci_notation.split('e')
    shifted = int(sci_notation_split[1]) + int(decimal_places)
    new_val = list(str(float(sci_notation_split[0] + 'e' + str(shifted))))
    index = 0
    while True:
        if new_val[index] in skip:
            index += 1
        else:
            break
    keeps = new_val[index:]
    check = len(keeps)
    if check < sigfigs:
        new_val = ''.join(new_val) + '0'
    else:
        new_val = ''.join(new_val)
    return new_val


def uncertainty_check(val):
    """
    Take a string consisting of a rotational constant and its uncertianty in form of 0.00275(12),
    and determine if the uncertainty is greater than the value.

    Useful for tkinter Entry widgets, allowing a tk.StringVar variable to be used instead of a
    tk.DoubleVar variable. You can set the default to "None" or display an error message. Handles
    moving a decimal place within a string rather than a float.

    Parameters:
        val (str or tk.StringVar):
            String of characters that can be interpretted as a float.
    Returns:
        bool:
            True = constant is greater than uncertainty.
            False = uncertainty greater than constant.
    """
    val = list(str(val).replace('.', ''))
    toss = ['0', '-', '.']
    i = 0
    while True:
        if val[i] in toss:
            i += 1
        else:
            break
    constant = val[i:]
    i = 0
    while True:
        if constant[i] == '(':
            i += 1
            j = i
            while True:
                if constant[j] == ')':
                    break
                else:
                    j += 1
            break
        else:
            i += 1
    uncertainty = constant[i:j]
    constant = constant[:i - 1]
    s = ''
    constant = int(s.join(constant))
    uncertainty = int(s.join(uncertainty))
    if constant > uncertainty:
        return True
    else:
        return False


# f = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Code\\Rotational Spectroscopy Data Analysis 4_24_2020\\Program Testing\\FinalFit\\fenR_Risop1_a_test.pi'
# file = 'C:\\Users\\chann\\OneDrive\\Graduate School\\Pate Group\\Varenicline\\Varenicline.pi'
# # # file = 'C:\\ROT\\GammaOcta1.pi'
# file = 'C:\\ROT\\fenR_Risop1_a.pi'
# instance = Piform(file)
# print(instance.file)
# # df = instance.rot_const_LaTeX(preamble=True, caption='Second Caption')


def copy_spfit_spcat_piform(parent_dir, dst_dir):
    """
    Check dst_dir for SPFIT, SPCAT, and Piform EXEs. Copy files to pickett_dir if not found.
    Requires EXEs in C:\ROT.

    Parameters:
        parent_dir (str):
            Parent director where EXEs are found.
        dst_dir (str):
            Destination directory. Directory where EXEs may or may not befound.
    """
    spfit_check = os.path.isfile(os.path.join(dst_dir, 'spfit.exe'))
    if not spfit_check:
        spfit = os.path.join(parent_dir, 'spfit.exe')
        shutil.copy(spfit, dst_dir)
    spcat_check = os.path.isfile(os.path.join(dst_dir, 'SPCAT.exe'))
    if not spcat_check:
        spcat = os.path.join(parent_dir, 'SPCAT.exe')
        shutil.copy(spcat, dst_dir)
    piform_check = os.path.isfile(os.path.join(dst_dir, 'piform.exe'))
    if not piform_check:
        piform = os.path.join(parent_dir, 'piform.exe')
        shutil.copy(piform, dst_dir)


def spfit_run(file, num_decimals=None):
    """
    Run SPFIT.exe and, subsequently, Piform.exe as subprocesses.
    Place output files in same directory as SPFIT.exe.
    
    Parameters:
        file (str):
            *.par or *.lin file path
        num_decimals (int):
            Number of num_decimals after decimal to keep for uncertainty.
            Default: 2
    """
    file = str(os.path.basename(file).split('.')[0])
    if num_decimals is None:
        num_decimals = 2
    SPFIT_string = 'SPFIT' + ' ' + str(file)
    a = subprocess.Popen(str(SPFIT_string), stdout=subprocess.PIPE, shell=False)
    a.stdout.read()
    piform_run(file, num_decimals)


def spcat_run(file):
    """
    Run SPCAT.exe as subprocess. Output files placed in same directory as SPCAT.exe

    Parameters:
        file (str):
            *.var or *.lin file path
    """
    file = str(os.path.basename(file).split('.')[0])
    filecontent1 = '%s.var\n' % file
    filecontent2 = '%s.int\n' % file
    spcat = subprocess.Popen('SPCAT', stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    spcat.stdin.write(filecontent1.encode('utf-8'))
    spcat.stdin.write(filecontent2.encode('utf-8'))
    spcat.communicate()


def piform_run(file, num_decimals=None):
    """
    Run Piform.exe as subprocess.

    Parameters:
        file (str):
            *.fit file path
        num_decimals (int):
            Number of digits after decimal to keep for uncertainty.
            Default: 2
    """
    file = str(os.path.basename(file).split('.')[0])
    if num_decimals is None:
        num_decimals = 2
    filecontent1 = '%s\n' % file
    filecontent2 = '%s.pi\n' % file
    filecontent3 = '%s\n' % num_decimals
    pf = subprocess.Popen('piform', stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    pf.stdin.write(filecontent1.encode('utf-8'))
    pf.stdin.write(filecontent2.encode('utf-8'))
    pf.stdin.write(filecontent3.encode('utf-8'))
    pf.communicate()
