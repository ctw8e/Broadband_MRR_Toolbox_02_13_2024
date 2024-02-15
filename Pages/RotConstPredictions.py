"""
Author: Channing West
Changelog: 12/5/2019
"""

import numpy as np
import os
import tkinter as tk
import tkinter.ttk as ttk
import re
from Pages.PageFormat import PageFormat
import Pages.PageFormat as page_funcs
import pandas as pd
from tkinter.messagebox import showerror
from Pages.PickettWriter import import_rigid_rotor

np.set_printoptions(precision=12)

atomic_mass_dict = {
    'H': 1.00782503207, '2H': 2.0141017778, '3H': 3.0160492777,
    'He': 2.007825037,
    'C': 12, '13C': 13.0033548378,
    'N': 14.0030740048, '15N': 15.0001088982,
    'O': 15.99491461956, '17O': 16.99913170, '18O': 17.9991610,
    'Ne': 19.9924401754, '21Ne': 20.99384668, '22Ne': 21.991385114,
    'Si': 27.9769265325, '29Si': 28.976494700, '30Si': 29.97377017,
    'S': 31.97207100, '33S': 32.97145876, '34S': 33.96786690, '36S': 35.96708076,
    'Cl': 34.96885268, '37Cl': 36.96590259,
    'Ar': 39.9623831225, '36Ar': 35.967545106, '38Ar': 37.9627324,
    'Br': 78.9183371, '81Br': 80.9162906,
    'F': 18.99840325}

atomic_num_dict = {'H': 1, 1: 'H',
                   'He': 2, 2: 'He',
                   'C': 6, 6: 'C',
                   'N': 7, 7: 'N',
                   'O': 8, 8: 'O',
                   'F': 9, 9: 'F',
                   'S': 16, 16: 'S',
                   'Cl': 17, 17: 'Cl',
                   'Br': 35, 35: 'Br'}

isotope_dict = {'H': '2H', '2H': 'H',
                'C': '13C', '13C': 'C',
                'N': '15N', '15N': 'N',
                'O': '18O', '18O': 'O',
                'Ne': '22Ne', '22Ne': 'Ne',
                'S': '34S', '34S': 'S',
                'Cl': '37Cl', '37Cl': 'Cl',
                'Br': '81Br', '81Br': 'Br',
                'F': 'F'}


class RotConstPredictions(ttk.Frame):
    """
    Generate GUI. Extract rotational constants from files and calculate rotational constants of
    isotopomers.

    BROWSE
        Open file explorer
    EXECUTE (1.Extract or Caluculate Rotational Constants from Gaussian Files)
        Run self.gaussian_rc()
    EXECUTE (2.Calculate Rotational Constants of Singly-Substituted Isotopomers)
        Run isotopomer_constants().
    IMPORT
        Quick import rigid rotor rotational constants from Pickett file into entry boxes.
    """
    default = {'gaussian_path': 'None',
               'gaussian_input_path': 'None',
               'isotopomer_path': 'None'}

    def __init__(self, master, controller):

        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Predict Rotational Constants"

        self.gaussian_path = tk.StringVar()
        self.gaussian_path.set(RotConstPredictions.default['gaussian_path'])

        self.isotopomer_path = tk.StringVar()
        self.isotopomer_path.set(RotConstPredictions.default['isotopomer_path'])

        self.rc_a = tk.DoubleVar()
        self.rc_b = tk.DoubleVar()
        self.rc_c = tk.DoubleVar()
        r = tk.RIGHT
        c = tk.CENTER
        h10bB = 'h10b.TButton'
        h8bL_r = {'justify': tk.RIGHT, 'style': 'h8b.TLabel'}
        block_1 = ttk.Frame(frame)

        section_1_L = ttk.Label(
            block_1, justify=tk.LEFT, style='h14b.TLabel',
            text='1.  Extract or Calculate Rotational Constants from Gaussian Files')
        gaussian1_L = ttk.Label(
            block_1, text='*.out/*.log/*.gjf File(s):', justify=r, style='h8b.TLabel')
        gaussian1_E = ttk.Entry(block_1, textvariable=self.gaussian_path, width=100, justify=c)
        gaussian1_B = ttk.Button(
            block_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_paths(
                self.gaussian_path, eb_var=gaussian1_E, ftype='gaussian'))
        execute1_B = ttk.Button(block_1, text='Execute', style=h10bB, command=self.gaussian_rc)

        section2_L = ttk.Label(
            block_1, justify=tk.LEFT, style='h14b.TLabel',
            text='2.  Calculate Rotational Constants -  Singly-Substituted Isotopomers')
        gaussian2_L = ttk.Label(block_1, text='*.out/*.log File:', **h8bL_r)
        rc_a_L = ttk.Label(block_1, text='Exp. A:', **h8bL_r)
        rc_b_L = ttk.Label(block_1, text='Exp. B:', **h8bL_r)
        rc_c_L = ttk.Label(block_1, text='Exp. C:', **h8bL_r)
        rc_import_B = ttk.Button(
            block_1, text='Import', style='h8b.TButton',
            command=lambda: import_rigid_rotor(self.rc_a, self.rc_b, self.rc_c))

        gaussian2_E = ttk.Entry(block_1, textvariable=self.isotopomer_path, justify=c)
        rc_a_E = ttk.Entry(block_1, textvariable=self.rc_a, justify=c)
        rc_b_E = ttk.Entry(block_1, textvariable=self.rc_b, justify=c)
        rc_c_E = ttk.Entry(block_1, textvariable=self.rc_c, justify=c)

        gaussian_path_B = ttk.Button(
            block_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_paths(
                self.isotopomer_path, eb_var=gaussian2_E, ftype='.out'))

        execute2_B = ttk.Button(
            block_1, text='Execute', style=h10bB,
            command=lambda: isotopomer_constants(
                page_funcs.list_paths(
                    self.isotopomer_path), self.rc_a.get(), self.rc_b.get(), self.rc_c.get()))

        horizontal_3 = ttk.Separator(block_1, orient='horizontal')

        section_1_L.grid(row=0, column=0, columnspan=3, padx=2, pady=2, sticky='w')
        gaussian1_L.grid(row=1, column=0, padx=2, pady=2, sticky='e')
        gaussian1_E.grid(row=1, column=1, padx=2, pady=2, sticky='ew')
        gaussian1_B.grid(row=1, column=2, stick='ew', padx=2, pady=2)
        execute1_B.grid(row=2, column=0, columnspan=4, padx=50, pady=10, sticky='ew')
        horizontal_3.grid(row=3, column=0, columnspan=4, padx=2, pady=20, sticky='ew')

        section2_L.grid(row=8, column=0, columnspan=3, padx=2, pady=2, sticky='w')
        gaussian2_L.grid(row=9, column=0, padx=2, pady=2, sticky='e')
        rc_a_L.grid(row=10, column=0, padx=2, pady=2, sticky='e')
        rc_b_L.grid(row=11, column=0, padx=2, pady=2, sticky='e')
        rc_c_L.grid(row=12, column=0, padx=2, pady=2, sticky='e')
        rc_import_B.grid(row=11, column=2, padx=2, pady=2, sticky='w')

        gaussian2_E.grid(row=9, column=1, padx=2, pady=2, sticky='ew')
        rc_a_E.grid(row=10, column=1, padx=2, pady=2, sticky='ew')
        rc_b_E.grid(row=11, column=1, padx=2, pady=2, sticky='ew')
        rc_c_E.grid(row=12, column=1, padx=2, pady=2, sticky='ew')

        gaussian_path_B.grid(row=9, column=2, stick='ew', padx=2, pady=2)
        execute2_B.grid(row=13, column=0, columnspan=4, padx=50, pady=10, sticky='ew')

        vertical_1 = ttk.Separator(frame, orient='vertical')
        vertical_2 = ttk.Separator(frame, orient='vertical')
        horizontal_1 = ttk.Separator(frame, orient='horizontal')
        horizontal_2 = ttk.Separator(frame, orient='horizontal')

        vertical_1.grid(row=0, column=0, rowspan=3, padx=20, pady=0, sticky='ns')
        vertical_2.grid(row=0, column=2, rowspan=3, padx=20, pady=0, sticky='ns')
        horizontal_1.grid(row=0, column=1, padx=2, pady=10, sticky='ew')
        horizontal_2.grid(row=2, column=1, padx=2, pady=10, sticky='ew')

        block_1.grid(row=1, column=1, sticky='e')

    def gaussian_rc(self):
        """ Runs on EXECUTE. Selects function based on file extension. """
        gaussian_paths = page_funcs.list_paths(self.gaussian_path)
        ext = os.path.splitext(gaussian_paths[0])[1]
        if ext in ['.out', '.log', '.OUT', '.LOG']:
            df = gaussian_outputs(gaussian_paths)
        elif ext in ['.gjf', '.GJF']:
            df = gaussian_inputs(gaussian_paths)


def gaussian_outputs(paths_list, save=True):
    """
    Extract rotational constants and dipoles from list of Gaussian input files.

    Parameters:
        paths_list (list of str):
            Gaussian output file paths (*.out/*.log)
        save (bool):
            Save df to csv.
            Default: True
    Returns:
        df (DataFrame):
            col[0] -> file name
            col[1] -> A val (MHz)
            col[2] -> B val (MHz)
            col[3] -> C val (MHz)
            col[4] -> uA dipole componenet (D)
            col[5] -> uB dipole componenet (D)
            col[6] -> uC dipole componenet (D)
    """
    final = []
    for file in paths_list:
        inner = []
        basename = os.path.basename(file)
        inner.append(basename)
        gaussian_file = [row for row in open(file)]

        RC_line = gaussian_file[gaussian_file.index(' Rotational constants (MHZ):\n') + 1]
        stripped_RC = re.sub(' +', ' ', RC_line).strip().split(' ')
        for constant in stripped_RC[0:3]:
            inner.append(abs(float(constant)))

        dipole_line = gaussian_file[gaussian_file.index(' Dipole moment (Debye):\n') + 1]
        stripped_dipole = re.sub(' +', ' ', dipole_line).strip().split(' ')
        for dipole in stripped_dipole[0:3]:
            inner.append(abs(float(dipole)))
        final.append(inner)
    df = pd.DataFrame(final, columns=('file name', 'A', 'B', 'C', 'uA', 'uB', 'uC'))
    if save:
        initialdir = os.path.dirname(paths_list[0])
        fname = page_funcs.save_file(ftype='csv', initialdir=initialdir, defaultextension='.csv')
        df.to_csv(fname)
    return df


def gaussian_inputs(paths_list, save=True):
    """
    Calculate rotational constants for a list of Gaussian input files.

    Parameters:
        paths_list (list of str):
            Gaussian input file paths (*.gjf)
        save (bool):
            Save output to csv.
    Returns:
        df (DataFrame):
            col[0] -> file name
            col[1] -> A val (MHz)
            col[2] -> B val (MHz)
            col[3] -> C val (MHz)
    """
    final = []
    for file in paths_list:
        inner = []
        basename = os.path.basename(file)
        inner.append(basename)
        gaussian_file = [row for row in open(file)]
        struct_start = int(gaussian_file.index('  0   1 \n') + 1)
        gauss = gaussian_file[struct_start:]
        end = int(gauss.index(' \n'))
        gauss = gauss[:end]
        gauss = [gauss[x].split() for x in range(len(gauss))]
        atomic_number = []
        for x in range(len(gauss)):
            row = gauss[x]
            atomic_number.append(atomic_num_dict[row[0]])
            row[0] = atomic_mass_dict[row[0]]
            for y in range(len(row)):
                row[y] = float(row[y])
            gauss[x] = row
        gauss = np.column_stack((atomic_number, np.array(gauss)))
        A, B, C = calc_rc(gauss)
        for constant in [A, B, C]:
            inner.append(abs(float(constant)))
        final.append(inner)
    df = pd.DataFrame(final, columns=('file name', 'A', 'B', 'C'))
    if save:
        initialdir = os.path.dirname(paths_list[0])
        fname = page_funcs.save_file(ftype='csv', initialdir=initialdir, defaultextension='.csv')
        df.to_csv(fname)
    return df


def isotopomer_constants(paths_list, rc_a, rc_b, rc_c, save=True):
    """
    Calculate rotational constants of singly substituted 13-C isotopomers from gaussian structure.

    Isotopomer rotational constants scaled using (experimental constant / predicted constant).

    Parameters:
        paths_list (list of strings):
            List of gaussian output/log file paths.
        rc_a (float):
            Experimental A val.
            Units: MHz
        rc_b (float):
            Experimental B val (MHz)
            Units: MHz
        rc_c (float):
            Experimental C val (MHz)
            Units: MHz
        save (bool):
            Save output to csv
            Default: True
    Returns:
        df (DataFrame):
            col[0] -> Label (ex. 13C)
            col[1] -> A val (MHz)
            col[2] -> B val (MHz)
            col[3] -> C val (MHz)
    """
    for file in paths_list:
        gaussian_file = [row for row in open(file)]
        gaussRC = gaussian_file[
            int(gaussian_file.index(' Rotational constants (MHZ):\n') + 1)].split()

        scaleA = rc_a / float(gaussRC[0])
        scaleB = rc_b / float(gaussRC[1])
        scaleC = rc_c / float(gaussRC[2])

        struct_start = int(
            gaussian_file.index(
                '                Principal axis orientation:                \n') + 5)
        gauss = gaussian_file[struct_start:]
        end = int(gauss.index(
            ' ---------------------------------------------------------------------\n'))
        gauss = gauss[:end]
        gauss = [row.split() for row in gauss]

        atomic_masses = []
        for x in range(len(gauss)):
            row = gauss[x]
            row.remove(row[0])
            for y in range(len(row)):
                row[y] = float(row[y])

            gauss[x] = row
            atomic_masses.append(atomic_mass_dict[atomic_num_dict[int(row[0])]])

        atomic_masses = np.array(atomic_masses)
        atomic_masses.shape = (len(atomic_masses), 1)
        gauss = np.array(gauss)
        gauss = np.hstack((gauss[:, :1], atomic_masses, gauss[:, 1:]))

        A, B, C = calc_rc(gauss)
        labels = ['NS']
        A_list = [A * scaleA]
        B_list = [B * scaleB]
        C_list = [C * scaleC]

        for x in range(len(gauss)):
            atomic_number = gauss[x, 0]
            iso_struct = np.array([gauss[x, :] for x in range(len(gauss))])
            iso_label = isotope_dict[atomic_num_dict[atomic_number]]
            iso_struct[x, 1] = atomic_mass_dict[iso_label]
            A, B, C = calc_rc(iso_struct)
            labels.append(iso_label)
            A_list.append(A * scaleA)
            B_list.append(B * scaleB)
            C_list.append(C * scaleC)
        iso_const_arr = np.column_stack((labels, A_list, B_list, C_list))
        df = pd.DataFrame(iso_const_arr, columns=('isotope', 'A', 'B', 'C'))
        if save:
            initialdir = os.path.dirname(paths_list[0])
            fname = page_funcs.save_file(
                ftype='csv', initialdir=initialdir, defaultextension='.csv')
            if not fname:
                return
            else:
                df.to_csv(fname)
        return df


def calc_rc(structure):
    """
    Calculate rotational constants in the principal axis system from cartesian
    coordinates and atomic masses.

    Parameters:
        structure (array):
            Atomic coordinates in cartesian coordinates.
            Units: angstroms
    Returns:
        A, B, C (floats):
            Rotational constants in PAS.
            Units: MHz
    """
    atomic_masses = [float(x) for x in structure[:, 1]]
    molecular_mass = sum(atomic_masses)

    COM_x = sum([atomic_masses[x] * float(structure[x, 2]) for x in
                 range(0, len(structure))]) / molecular_mass
    COM_y = sum([atomic_masses[x] * float(structure[x, 3]) for x in
                 range(0, len(structure))]) / molecular_mass
    COM_z = sum([atomic_masses[x] * float(structure[x, 4]) for x in
                 range(0, len(structure))]) / molecular_mass

    for row in range(len(structure)):
        structure[row, 2] = float(structure[row, 2]) - COM_x
        structure[row, 3] = float(structure[row, 3]) - COM_y
        structure[row, 4] = float(structure[row, 4]) - COM_z

    I_xx = sum([structure[x, 1] * (structure[x, 3] ** 2 + structure[x, 4] ** 2) for x in
                range(len(structure))])
    I_yy = sum([structure[x, 1] * (structure[x, 2] ** 2 + structure[x, 4] ** 2) for x in
                range(len(structure))])
    I_zz = sum([structure[x, 1] * (structure[x, 2] ** 2 + structure[x, 3] ** 2) for x in
                range(len(structure))])
    I_xy = (-1) * sum(
        [structure[x, 1] * structure[x, 2] * structure[x, 3] for x in range(len(structure))])
    I_xz = (-1) * sum(
        [structure[x, 1] * structure[x, 2] * structure[x, 4] for x in range(len(structure))])
    I_yz = (-1) * sum(
        [structure[x, 1] * structure[x, 3] * structure[x, 4] for x in range(len(structure))])

    inertia_matrix = np.zeros((3, 3))
    inertia_matrix[0, 0] = I_xx
    inertia_matrix[1, 1] = I_yy
    inertia_matrix[2, 2] = I_zz
    inertia_matrix[0, 1] = I_xy
    inertia_matrix[1, 0] = I_xy
    inertia_matrix[2, 0] = I_xz
    inertia_matrix[0, 2] = I_xz
    inertia_matrix[2, 1] = I_yz
    inertia_matrix[1, 2] = I_yz

    eigenvals_ = np.linalg.eigh(inertia_matrix)
    eigenvals = eigenvals_[0]

    I_x, I_y, I_z = eigenvals[0], eigenvals[1], eigenvals[2]
    if I_x <= I_y <= I_z:
        H_8pi2 = 505379.0094
        A, B, C = (H_8pi2 / I_x), (H_8pi2 / I_y), (H_8pi2 / I_z)
        return A, B, C
    else:
        showerror(title='Error', message='Isotopic substitution changes principal axes')
