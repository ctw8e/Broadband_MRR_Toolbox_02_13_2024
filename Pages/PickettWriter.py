"""
Author: Channing West
Changelog: 12/5/2019

"""

import os
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror, askyesnocancel
from Pages.PageFormat import PageFormat
import Pickett
import Pages.PageFormat as page_funcs
import re


class PickettWriter(ttk.Frame):
    """
    Generate GUI. Write Pickett files.

    Buttons:
        SAVE SETUP, LOAD SETUP, DEFAULTS, BACK TO NAVIGATOR, EXIT APPLICATION
            See PageFormat.py
        IMPORT
            Depending on the section the button resides in, run either
            import_rigid_rotor(self.A, self.B, self.C),
            import_quartic_distortion(self.DJ, self.DJK, self.DK, self.dJ, self.dK),
            or import_dipole_components(self.uA, self.uB, self.uC)
        18 GHZ | 1 K | 20
            Quick fill option. Run self.partition_entry(18, 1, 20).
        8 GHZ | 1 K | 20
            Quick fill option. Run self.partition_entry(8, 1, 20).
        2-8 GHZ
            Quick fill option. Run self.spec_prediction_entry(2000, 8000).
        6-18 GHZ
            Quick fill option. Run self.spec_prediction_entry(6000, 18000).
        2-18 GHZ
            Quick fill option. Run self.spec_prediction_entry(2000, 18000).
        QUICK_IMPORT
            Run self.quick_import(). Search for rigid rotor constants, quartic distortion constants,
             quadrupolar constants, and dipole components from a set of Pickett files.
        WRITE PICKETT FILES
            Run self.write_single(). Generate *.par, *.var, *.cat, *.out, and *.int files using GUI
            values. Optionally generate spectral simulation.
        WRITE PICKETT FILES: SET OF ISOTOPOMERS
            Run self.isotopomers(). Write Pickett files for all 13C isotopomers of a molecule.
        LATEX: LINE LIST
            Run self.piform_LaTeX('line_list'). Generate a LaTeX table containing assigned
            transitions.
        LATEX: ROT. CONSTANTS
            Run self.piform_LaTeX('rot_const'). Generate a LaTeX table containing rotational
            constants.
    Checkbuttons:
        FIX
            Beside all constants, there are checkbuttons that allow the user to fix the constant,
            thus, setting the uncertainty to 1e-20.
        SIMULATE
            Check to produce spectral simulation after writing Pickett files.
        PREAMBLE
            Check to write preamble in output. Include preamble for new LaTeX document. Not
            necessary if planning to add table to existing LaTeX document.
    """
    default = {'A': 0,
               'B': 0,
               'C': 0,
               'A_err': 0,
               'B_err': 0,
               'C_err': 0,
               'DJ': 0,
               'DJK': 0,
               'DK': 0,
               'dJ': 0,
               'dK': 0,
               'DJ_err': 0,
               'DJK_err': 0,
               'DK_err': 0,
               'dJ_err': 0,
               'dK_err': 0,
               'all_qdc': 1,
               'muA': 0,
               'muB': 0,
               'muC': 0,
               'max_freq': 18,
               'T': 1,
               'Jmax': 20,
               'start_freq': 2000,
               'end_freq': 18000,
               'fwhm': 0.035,
               'spin_1': 0,
               'chi_aa_1': 0,
               'chi_bbcc_1': 0,
               'chi_ab_1': 0,
               'chi_bc_1': 0,
               'chi_ac_1': 0,
               'chi_aa_1_err': 0,
               'chi_bbcc_1_err': 0,
               'chi_ab_1_err': 0,
               'chi_bc_1_err': 0,
               'chi_ac_1_err': 0,
               'spin_2': 0,
               'chi_aa_2': 0,
               'chi_bbcc_2': 0,
               'chi_ab_2': 0,
               'chi_bc_2': 0,
               'chi_ac_2': 0,
               'chi_aa_2_err': 0,
               'chi_bbcc_2_err': 0,
               'chi_ab_2_err': 0,
               'chi_bc_2_err': 0,
               'chi_ac_2_err': 0,
               'spin_3': 0,
               'chi_aa_3': 0,
               'chi_bbcc_3': 0,
               'chi_ab_3': 0,
               'chi_bc_3': 0,
               'chi_ac_3': 0,
               'chi_aa_3_err': 0,
               'chi_bbcc_3_err': 0,
               'chi_ab_3_err': 0,
               'chi_bc_3_err': 0,
               'chi_ac_3_err': 0,
               'sim_spec': 1,
               'piform_file': 'None',
               'num_qns': 3,
               'preamble': 1,
               'caption': 'None'}

    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        self.controller = controller
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Pickett Writer"

        self.A = tk.DoubleVar()
        self.B = tk.DoubleVar()
        self.C = tk.DoubleVar()
        self.A.set(PickettWriter.default['A'])
        self.B.set(PickettWriter.default['B'])
        self.C.set(PickettWriter.default['C'])
        self.A_err = tk.IntVar()
        self.B_err = tk.IntVar()
        self.C_err = tk.IntVar()
        self.A_err.set(PickettWriter.default['A_err'])
        self.B_err.set(PickettWriter.default['B_err'])
        self.C_err.set(PickettWriter.default['C_err'])
        self.DJ = tk.DoubleVar()
        self.DJK = tk.DoubleVar()
        self.DK = tk.DoubleVar()
        self.dJ = tk.DoubleVar()
        self.dK = tk.DoubleVar()
        self.DJ.set(PickettWriter.default['DJ'])
        self.DJK.set(PickettWriter.default['DJK'])
        self.DK.set(PickettWriter.default['DK'])
        self.dJ.set(PickettWriter.default['dJ'])
        self.dK.set(PickettWriter.default['dK'])
        self.DJ_err = tk.IntVar()
        self.DJK_err = tk.IntVar()
        self.DK_err = tk.IntVar()
        self.dJ_err = tk.IntVar()
        self.dK_err = tk.IntVar()
        self.DJ_err.set(PickettWriter.default['DJ_err'])
        self.DJK_err.set(PickettWriter.default['DJK_err'])
        self.DK_err.set(PickettWriter.default['DK_err'])
        self.dJ_err.set(PickettWriter.default['dJ_err'])
        self.dK_err.set(PickettWriter.default['dK_err'])
        self.uA = tk.DoubleVar()
        self.uB = tk.DoubleVar()
        self.uC = tk.DoubleVar()
        self.uA.set(PickettWriter.default['muA'])
        self.uB.set(PickettWriter.default['muB'])
        self.uC.set(PickettWriter.default['muC'])
        self.max_freq = tk.DoubleVar()
        self.T = tk.DoubleVar()
        self.Jmax = tk.IntVar()
        self.max_freq.set(PickettWriter.default['max_freq'])
        self.T.set(PickettWriter.default['T'])
        self.Jmax.set(PickettWriter.default['Jmax'])
        self.start_freq = tk.IntVar()
        self.end_freq = tk.IntVar()
        self.line_width = tk.DoubleVar()
        self.start_freq.set(PickettWriter.default['start_freq'])
        self.end_freq.set(PickettWriter.default['end_freq'])
        self.line_width.set(PickettWriter.default['fwhm'])
        self.spin_1 = tk.DoubleVar()
        self.chi_aa_1 = tk.DoubleVar()
        self.chi_bbcc_1 = tk.DoubleVar()
        self.chi_ab_1 = tk.DoubleVar()
        self.chi_bc_1 = tk.DoubleVar()
        self.chi_ac_1 = tk.DoubleVar()
        self.spin_1.set(PickettWriter.default['spin_1'])
        self.chi_aa_1.set(PickettWriter.default['chi_aa_1'])
        self.chi_bbcc_1.set(PickettWriter.default['chi_bbcc_1'])
        self.chi_ab_1.set(PickettWriter.default['chi_ab_1'])
        self.chi_bc_1.set(PickettWriter.default['chi_bc_1'])
        self.chi_ac_1.set(PickettWriter.default['chi_ac_1'])
        self.chi_aa_1_err = tk.IntVar()
        self.chi_bbcc_1_err = tk.IntVar()
        self.chi_ab_1_err = tk.IntVar()
        self.chi_bc_1_err = tk.IntVar()
        self.chi_ac_1_err = tk.IntVar()
        self.chi_aa_1_err.set(PickettWriter.default['chi_aa_1_err'])
        self.chi_bbcc_1_err.set(PickettWriter.default['chi_bbcc_1_err'])
        self.chi_ab_1_err.set(PickettWriter.default['chi_ab_1_err'])
        self.chi_bc_1_err.set(PickettWriter.default['chi_bc_1_err'])
        self.chi_ac_1_err.set(PickettWriter.default['chi_ac_1_err'])
        self.spin_2 = tk.DoubleVar()
        self.chi_aa_2 = tk.DoubleVar()
        self.chi_bbcc_2 = tk.DoubleVar()
        self.chi_ab_2 = tk.DoubleVar()
        self.chi_bc_2 = tk.DoubleVar()
        self.chi_ac_2 = tk.DoubleVar()
        self.spin_2.set(PickettWriter.default['spin_2'])
        self.chi_aa_2.set(PickettWriter.default['chi_aa_2'])
        self.chi_bbcc_2.set(PickettWriter.default['chi_bbcc_2'])
        self.chi_ab_2.set(PickettWriter.default['chi_ab_2'])
        self.chi_bc_2.set(PickettWriter.default['chi_bc_2'])
        self.chi_ac_2.set(PickettWriter.default['chi_ac_2'])
        self.chi_aa_2_err = tk.IntVar()
        self.chi_bbcc_2_err = tk.IntVar()
        self.chi_ab_2_err = tk.IntVar()
        self.chi_bc_2_err = tk.IntVar()
        self.chi_ac_2_err = tk.IntVar()
        self.chi_aa_2_err.set(PickettWriter.default['chi_aa_2_err'])
        self.chi_bbcc_2_err.set(PickettWriter.default['chi_bbcc_2_err'])
        self.chi_ab_2_err.set(PickettWriter.default['chi_ab_2_err'])
        self.chi_bc_2_err.set(PickettWriter.default['chi_bc_2_err'])
        self.chi_ac_2_err.set(PickettWriter.default['chi_ac_2_err'])
        self.spin_3 = tk.DoubleVar()
        self.chi_aa_3 = tk.DoubleVar()
        self.chi_bbcc_3 = tk.DoubleVar()
        self.chi_ab_3 = tk.DoubleVar()
        self.chi_bc_3 = tk.DoubleVar()
        self.chi_ac_3 = tk.DoubleVar()
        self.spin_3.set(PickettWriter.default['spin_3'])
        self.chi_aa_3.set(PickettWriter.default['chi_aa_3'])
        self.chi_bbcc_3.set(PickettWriter.default['chi_bbcc_3'])
        self.chi_ab_3.set(PickettWriter.default['chi_ab_3'])
        self.chi_bc_3.set(PickettWriter.default['chi_bc_3'])
        self.chi_ac_3.set(PickettWriter.default['chi_ac_3'])
        self.chi_aa_3_err = tk.IntVar()
        self.chi_bbcc_3_err = tk.IntVar()
        self.chi_ab_3_err = tk.IntVar()
        self.chi_bc_3_err = tk.IntVar()
        self.chi_ac_3_err = tk.IntVar()
        self.chi_aa_3_err.set(PickettWriter.default['chi_aa_3_err'])
        self.chi_bbcc_3_err.set(PickettWriter.default['chi_bbcc_3_err'])
        self.chi_ab_3_err.set(PickettWriter.default['chi_ab_3_err'])
        self.chi_bc_3_err.set(PickettWriter.default['chi_bc_3_err'])
        self.chi_ac_3_err.set(PickettWriter.default['chi_ac_3_err'])
        self.sim_spec = tk.IntVar()
        self.sim_spec.set(PickettWriter.default['sim_spec'])
        self.piform_file = tk.StringVar()
        self.preamble = tk.IntVar()
        self.num_qns = tk.IntVar()
        self.caption = tk.StringVar()
        self.piform_file.set(PickettWriter.default['piform_file'])
        self.preamble.set(PickettWriter.default['preamble'])
        self.num_qns.set(PickettWriter.default['num_qns'])

        block_1 = ttk.Frame(frame)
        block_2 = ttk.Frame(frame)
        block_3 = ttk.Frame(frame)
        c = tk.CENTER
        x2y2e = {'padx': 2, 'pady': 2, 'sticky': 'e'}
        x2y2ew = {'padx': 2, 'pady': 2, 'sticky': 'ew'}
        h10bL_r = {'style': 'h10b.TLabel', 'justify': tk.RIGHT}
        r_w40 = {'justify': c, 'width': 40}
        h12bL_c = {'style': 'h12b.TLabel', 'justify': c}
        h8bL_c = {'style': 'h8b.TLabel', 'justify': c}
        cspan2_x2y10 = {'columnspan': 2, 'padx': 2, 'pady': 10}
        x2y10w = {'padx': 2, 'pady': 10, 'sticky': 'w'}
        x2y20ew = {'padx': 2, 'pady': 20, 'sticky': 'ew'}
        x2y2 = {'padx': 2, 'pady': 2}
        x10y0ew = {'padx': 10, 'pady': 0, 'sticky': 'ew'}
        # ==========================================================================================
        #                                    Rigid Rotor Block
        # ==========================================================================================
        RC_L = ttk.Label(block_1, text='Rigid Rotor (MHz)', **h12bL_c)
        RC_fix_L = ttk.Label(block_1, text='fix', **h8bL_c)
        A_L = ttk.Label(block_1, text='A', **h10bL_r)
        B_L = ttk.Label(block_1, text='B', **h10bL_r)
        C_L = ttk.Label(block_1, text='C', **h10bL_r)
        A_E = ttk.Entry(block_1, textvariable=self.A, **r_w40)
        B_E = ttk.Entry(block_1, textvariable=self.B, **r_w40)
        C_E = ttk.Entry(block_1, textvariable=self.C, **r_w40)
        A_err_cb = ttk.Checkbutton(block_1, variable=self.A_err)
        B_err_cb = ttk.Checkbutton(block_1, variable=self.B_err)
        C_err_cb = ttk.Checkbutton(block_1, variable=self.C_err)
        button_RC_JB = ttk.Button(
            block_1, text='Import', style='h8b.TButton',
            command=lambda: import_rigid_rotor(self.A, self.B, self.C))
        RC_L.grid(row=0, column=1, **cspan2_x2y10)
        RC_fix_L.grid(row=0, column=2, **x2y10w)
        A_L.grid(row=1, column=0, **x2y2e)
        B_L.grid(row=2, column=0, **x2y2e)
        C_L.grid(row=3, column=0, **x2y2e)
        A_E.grid(row=1, column=1, **x2y2ew)
        B_E.grid(row=2, column=1, **x2y2ew)
        C_E.grid(row=3, column=1, **x2y2ew)
        A_err_cb.grid(row=1, column=2, **x2y2)
        B_err_cb.grid(row=2, column=2, **x2y2)
        C_err_cb.grid(row=3, column=2, **x2y2)
        button_RC_JB.grid(row=0, column=3, **x10y0ew)

        separator = ttk.Separator(block_1, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=4, **x2y20ew)

        # ==========================================================================================
        #                                    Quartic Distortion Block
        # ==========================================================================================
        distortion_L = ttk.Label(block_1, text='Quartic Distortion (MHz)', **h12bL_c)
        qdc_fix_L = ttk.Label(block_1, text='fix', **h8bL_c)
        DJ_L = ttk.Label(block_1, text='\u0394J', **h10bL_r)
        DJK_L = ttk.Label(block_1, text='\u0394JK', **h10bL_r)
        DK_L = ttk.Label(block_1, text='\u0394K', **h10bL_r)
        dJ_L = ttk.Label(block_1, text='\u03B4J', **h10bL_r)
        dK_L = ttk.Label(block_1, text='\u03B4K', **h10bL_r)
        DJ_E = ttk.Entry(block_1, textvariable=self.DJ, **r_w40)
        DJK_E = ttk.Entry(block_1, textvariable=self.DJK, **r_w40)
        DK_E = ttk.Entry(block_1, textvariable=self.DK, **r_w40)
        dJ_E = ttk.Entry(block_1, textvariable=self.dJ, **r_w40)
        dK_E = ttk.Entry(block_1, textvariable=self.dK, **r_w40)
        DJ_err_cb = ttk.Checkbutton(block_1, variable=self.DJ_err)
        DJK_err_cb = ttk.Checkbutton(block_1, variable=self.DJK_err)
        DK_err_cb = ttk.Checkbutton(block_1, variable=self.DK_err)
        dJ_err_cb = ttk.Checkbutton(block_1, variable=self.dJ_err)
        dK_err_cb = ttk.Checkbutton(block_1, variable=self.dK_err)
        JB_qdc_B = ttk.Button(
            block_1, text='Import', style='h8b.TButton',
            command=lambda: import_quartic_distortion(self.DJ, self.DJK, self.DK, self.dJ, self.dK))
        distortion_L.grid(row=5, column=1, **cspan2_x2y10)
        qdc_fix_L.grid(row=5, column=2, **x2y10w)
        DJ_L.grid(row=6, column=0, **x2y2e)
        DJK_L.grid(row=7, column=0, **x2y2e)
        DK_L.grid(row=8, column=0, **x2y2e)
        dJ_L.grid(row=9, column=0, **x2y2e)
        dK_L.grid(row=10, column=0, **x2y2e)
        DJ_E.grid(row=6, column=1, **x2y2ew)
        DJK_E.grid(row=7, column=1, **x2y2ew)
        DK_E.grid(row=8, column=1, **x2y2ew)
        dJ_E.grid(row=9, column=1, **x2y2ew)
        dK_E.grid(row=10, column=1, **x2y2ew)
        DJ_err_cb.grid(row=6, column=2, **x2y2)
        DJK_err_cb.grid(row=7, column=2, **x2y2)
        DK_err_cb.grid(row=8, column=2, **x2y2)
        dJ_err_cb.grid(row=9, column=2, **x2y2)
        dK_err_cb.grid(row=10, column=2, **x2y2)
        JB_qdc_B.grid(row=5, column=3, **x10y0ew)

        separator = ttk.Separator(block_1, orient='horizontal')
        separator.grid(row=11, column=0, columnspan=4, **x2y20ew)

        # ==========================================================================================
        #                                    Dipole Component Block
        # ==========================================================================================
        dipole_L = ttk.Label(block_1, text='Dipole Components (D)', **h12bL_c)
        uA_L = ttk.Label(block_1, text='\u03BCa', **h10bL_r)
        uB_L = ttk.Label(block_1, text='\u03BCb', **h10bL_r)
        uC_L = ttk.Label(block_1, text='\u03BCc', **h10bL_r)
        uA_E = ttk.Entry(block_1, textvariable=self.uA, **r_w40)
        uB_E = ttk.Entry(block_1, textvariable=self.uB, **r_w40)
        uC_E = ttk.Entry(block_1, textvariable=self.uC, **r_w40)
        button_dipole = ttk.Button(
            block_1, text='Import', style='h8b.TButton',
            command=lambda: import_dipole_components(self.uA, self.uB, self.uC))
        dipole_L.grid(row=12, column=1, **cspan2_x2y10)
        uA_L.grid(row=13, column=0, **x2y2e)
        uB_L.grid(row=14, column=0, **x2y2e)
        uC_L.grid(row=15, column=0, **x2y2e)
        uA_E.grid(row=13, column=1, **x2y2ew)
        uB_E.grid(row=14, column=1, **x2y2ew)
        uC_E.grid(row=15, column=1, **x2y2ew)
        button_dipole.grid(row=12, column=3, **x10y0ew)

        separator = ttk.Separator(block_1, orient='horizontal')
        separator.grid(row=16, column=0, columnspan=4, **x2y20ew)

        # ==========================================================================================
        #                                   Partition Function Block
        # ==========================================================================================
        partition_L = ttk.Label(block_1, text='Partition Function', **h12bL_c)
        max_freq_L = ttk.Label(block_1, text='Max Freq. (GHz)', **h10bL_r)
        T_L = ttk.Label(block_1, text='Temp. (K)', **h10bL_r)
        Jmax_L = ttk.Label(block_1, text='J Max', **h10bL_r)
        max_freq_E = ttk.Entry(block_1, textvariable=self.max_freq, **r_w40)
        T_E = ttk.Entry(block_1, textvariable=self.T, **r_w40)
        Jmax_E = ttk.Entry(block_1, textvariable=self.Jmax, **r_w40)
        button_max_18 = ttk.Button(
            block_1, text='18GHz | 1K | 20', style='h8b.TButton',
            command=lambda: self.partition_entry(18, 1, 20))
        button_max_8 = ttk.Button(
            block_1, text='8GHz | 1K | 20', style='h8b.TButton',
            command=lambda: self.partition_entry(8, 1, 20))
        partition_L.grid(row=17, column=1, **cspan2_x2y10)
        max_freq_L.grid(row=18, column=0, **x2y2e)
        T_L.grid(row=19, column=0, **x2y2e)
        Jmax_L.grid(row=20, column=0, **x2y2e)
        max_freq_E.grid(row=18, column=1, **x2y2ew)
        T_E.grid(row=19, column=1, **x2y2ew)
        Jmax_E.grid(row=20, column=1, **x2y2ew)
        button_max_18.grid(row=18, column=3, **x10y0ew)
        button_max_8.grid(row=19, column=3, **x10y0ew)

        separator = ttk.Separator(block_1, orient='horizontal')
        separator.grid(row=21, column=0, columnspan=4, **x2y20ew)

        # ==========================================================================================
        #                          Spectrum Prediction and Output Block
        # ==========================================================================================
        prediction_L = ttk.Label(block_1, text='Spectral Simulation (MHz)', **h12bL_c)
        sim_spec_L = ttk.Label(block_1, text='Simulate:', **h10bL_r)
        start_freq_L = ttk.Label(block_1, text='Start Freq.', **h10bL_r)
        end_freq_L = ttk.Label(block_1, text='End Freq.', **h10bL_r)
        line_width_L = ttk.Label(block_1, text='Line Width', **h10bL_r)
        sim_spec_checkbox = ttk.Checkbutton(block_1, variable=self.sim_spec)
        start_freq_E = ttk.Entry(block_1, textvariable=self.start_freq, **r_w40)
        end_freq_E = ttk.Entry(block_1, textvariable=self.end_freq, **r_w40)
        line_width_E = ttk.Entry(block_1, textvariable=self.line_width, **r_w40)
        button_2to18 = ttk.Button(
            block_1, text='2-18 GHz', style='h8b.TButton',
            command=lambda: self.spec_prediction_entry(2000, 18000, 0.035))
        button_2to8 = ttk.Button(
            block_1, text='2-8 GHz', style='h8b.TButton',
            command=lambda: self.spec_prediction_entry(2000, 8000, 0.035))
        button_6to18 = ttk.Button(
            block_1, text='6-18 GHz', style='h8b.TButton',
            command=lambda: self.spec_prediction_entry(6000, 18000, 0.035))
        prediction_L.grid(row=22, column=1, **cspan2_x2y10)
        sim_spec_L.grid(row=23, column=0, **x2y2e)
        start_freq_L.grid(row=24, column=0, **x2y2e)
        end_freq_L.grid(row=25, column=0, **x2y2e)
        line_width_L.grid(row=26, column=0, **x2y2e)
        sim_spec_checkbox.grid(row=23, column=1, **x2y2)
        start_freq_E.grid(row=24, column=1, **x2y2ew)
        end_freq_E.grid(row=25, column=1, **x2y2ew)
        line_width_E.grid(row=26, column=1, **x2y2ew)
        button_2to18.grid(row=24, column=3, **x10y0ew)
        button_2to8.grid(row=25, column=3, **x10y0ew)
        button_6to18.grid(row=26, column=3, **x10y0ew)

        separator = ttk.Separator(block_1, orient='horizontal')
        separator.grid(row=27, column=0, columnspan=4, padx=2, pady=14, sticky='ew')

        # ==========================================================================================
        #                              Quadrupolar Nucleus 1
        # ==========================================================================================
        nuc_1_hyperfine_L = ttk.Label(block_2, text='Quad. Nucleus 1 (MHz)', **h12bL_c)
        nuc_1_fix_L = ttk.Label(block_2, text='fix', **h8bL_c)
        spin_L_1 = ttk.Label(block_2, text='Nuclear Spin', **h10bL_r)
        chi_aa_L_1 = ttk.Label(block_2, text='1.5 \u03C7aa', **h10bL_r)
        chi_bbcc_L_1 = ttk.Label(block_2, text='0.25(\u03C7bb - \u03C7cc)', **h10bL_r)
        chi_ab_L_1 = ttk.Label(block_2, text='\u03C7ab', **h10bL_r)
        chi_bc_L_1 = ttk.Label(block_2, text='\u03C7bc', **h10bL_r)
        chi_ac_L_1 = ttk.Label(block_2, text='\u03C7ac', **h10bL_r)
        spin_E_1 = ttk.Entry(block_2, textvariable=self.spin_1, **r_w40)
        chi_aa_E_1 = ttk.Entry(block_2, textvariable=self.chi_aa_1, **r_w40)
        chi_bbcc_E_1 = ttk.Entry(block_2, textvariable=self.chi_bbcc_1, **r_w40)
        chi_ab_E_1 = ttk.Entry(block_2, textvariable=self.chi_ab_1, **r_w40)
        chi_bc_E_1 = ttk.Entry(block_2, textvariable=self.chi_bc_1, **r_w40)
        chi_ac_E_1 = ttk.Entry(block_2, textvariable=self.chi_ac_1, **r_w40)
        chi_aa_1_err_cb = ttk.Checkbutton(block_2, variable=self.chi_aa_1_err)
        chi_bbcc_1_err_cb = ttk.Checkbutton(block_2, variable=self.chi_bbcc_1_err)
        chi_ab_1_err_cb = ttk.Checkbutton(block_2, variable=self.chi_ab_1_err)
        chi_bc_1_err_cb = ttk.Checkbutton(block_2, variable=self.chi_bc_1_err)
        chi_ac_1_err_cb = ttk.Checkbutton(block_2, variable=self.chi_ac_1_err)
        nuc_1_hyperfine_L.grid(row=0, column=1, **cspan2_x2y10)
        nuc_1_fix_L.grid(row=0, column=2, **x2y10w)
        spin_L_1.grid(row=1, column=0, **x2y2e)
        chi_aa_L_1.grid(row=2, column=0, **x2y2e)
        chi_bbcc_L_1.grid(row=3, column=0, **x2y2e)
        chi_ab_L_1.grid(row=4, column=0, **x2y2e)
        chi_bc_L_1.grid(row=5, column=0, **x2y2e)
        chi_ac_L_1.grid(row=6, column=0, **x2y2e)
        spin_E_1.grid(row=1, column=1, **x2y2ew)
        chi_aa_E_1.grid(row=2, column=1, **x2y2ew)
        chi_bbcc_E_1.grid(row=3, column=1, **x2y2ew)
        chi_ab_E_1.grid(row=4, column=1, **x2y2ew)
        chi_bc_E_1.grid(row=5, column=1, **x2y2ew)
        chi_ac_E_1.grid(row=6, column=1, **x2y2ew)
        chi_aa_1_err_cb.grid(row=2, column=2, **x2y2)
        chi_bbcc_1_err_cb.grid(row=3, column=2, **x2y2)
        chi_ab_1_err_cb.grid(row=4, column=2, **x2y2)
        chi_bc_1_err_cb.grid(row=5, column=2, **x2y2)
        chi_ac_1_err_cb.grid(row=6, column=2, **x2y2)

        separator = ttk.Separator(block_2, orient='horizontal')
        separator.grid(row=7, column=0, columnspan=2, padx=2, pady=12, sticky='ew')
        # ==========================================================================================
        #                              Quadrupolar Nucleus 2
        # ==========================================================================================
        nuc_2_hyperfine_L = ttk.Label(block_2, text='Quad. Nucleus 2 (MHz)', **h12bL_c)
        nuc_2_fix_L = ttk.Label(block_2, text='fix', **h8bL_c)
        spin_L_2 = ttk.Label(block_2, text='Nuclear Spin', **h10bL_r)
        chi_aa_L_2 = ttk.Label(block_2, text='1.5 \u03C7aa', **h10bL_r)
        chi_bbcc_L_2 = ttk.Label(block_2, text='0.25(\u03C7bb - \u03C7cc)', **h10bL_r)
        chi_ab_L_2 = ttk.Label(block_2, text='\u03C7ab', **h10bL_r)
        chi_bc_L_2 = ttk.Label(block_2, text='\u03C7bc', **h10bL_r)
        chi_ac_L_2 = ttk.Label(block_2, text='\u03C7ac', **h10bL_r)
        spin_E_2 = ttk.Entry(block_2, textvariable=self.spin_2, **r_w40)
        chi_aa_E_2 = ttk.Entry(block_2, textvariable=self.chi_aa_2, **r_w40)
        chi_bbcc_E_2 = ttk.Entry(block_2, textvariable=self.chi_bbcc_2, **r_w40)
        chi_ab_E_2 = ttk.Entry(block_2, textvariable=self.chi_ab_2, **r_w40)
        chi_bc_E_2 = ttk.Entry(block_2, textvariable=self.chi_bc_2, **r_w40)
        chi_ac_E_2 = ttk.Entry(block_2, textvariable=self.chi_ac_2, **r_w40)
        chi_aa_2_err_cb = ttk.Checkbutton(block_2, variable=self.chi_aa_2_err)
        chi_bbcc_2_err_cb = ttk.Checkbutton(block_2, variable=self.chi_bbcc_2_err)
        chi_ab_2_err_cb = ttk.Checkbutton(block_2, variable=self.chi_ab_2_err)
        chi_bc_2_err_cb = ttk.Checkbutton(block_2, variable=self.chi_bc_2_err)
        chi_ac_2_err_cb = ttk.Checkbutton(block_2, variable=self.chi_ac_2_err)
        nuc_2_hyperfine_L.grid(row=8, column=1, **cspan2_x2y10)
        nuc_2_fix_L.grid(row=8, column=2, **x2y10w)
        spin_L_2.grid(row=9, column=0, **x2y2e)
        chi_aa_L_2.grid(row=10, column=0, **x2y2e)
        chi_bbcc_L_2.grid(row=11, column=0, **x2y2e)
        chi_ab_L_2.grid(row=12, column=0, **x2y2e)
        chi_bc_L_2.grid(row=13, column=0, **x2y2e)
        chi_ac_L_2.grid(row=14, column=0, **x2y2e)
        spin_E_2.grid(row=9, column=1, **x2y2ew)
        chi_aa_E_2.grid(row=10, column=1, **x2y2ew)
        chi_bbcc_E_2.grid(row=11, column=1, **x2y2ew)
        chi_ab_E_2.grid(row=12, column=1, **x2y2ew)
        chi_bc_E_2.grid(row=13, column=1, **x2y2ew)
        chi_ac_E_2.grid(row=14, column=1, **x2y2ew)
        chi_aa_2_err_cb.grid(row=10, column=2, **x2y2)
        chi_bbcc_2_err_cb.grid(row=11, column=2, **x2y2)
        chi_ab_2_err_cb.grid(row=12, column=2, **x2y2)
        chi_bc_2_err_cb.grid(row=13, column=2, **x2y2)
        chi_ac_2_err_cb.grid(row=14, column=2, **x2y2)

        separator = ttk.Separator(block_2, orient='horizontal')
        separator.grid(row=15, column=0, columnspan=2, padx=2, pady=12, sticky='ew')
        # ==========================================================================================
        #                              Quadrupolar Nucleus 3
        # ==========================================================================================
        nuc_3_hyperfine_L = ttk.Label(
            block_2, text='Quad. Nucleus 3 (MHz)', style='h12b.TLabel', justify=c)
        nuc_3_fix_L = ttk.Label(block_2, text='fix', **h8bL_c)
        spin_L_3 = ttk.Label(block_2, text='Nuclear Spin', **h10bL_r)
        chi_aa_L_3 = ttk.Label(block_2, text='1.5 \u03C7aa', **h10bL_r)
        chi_bbcc_L_3 = ttk.Label(block_2, text='0.25(\u03C7bb - \u03C7cc)', **h10bL_r)
        chi_ab_L_3 = ttk.Label(block_2, text='\u03C7ab', **h10bL_r)
        chi_bc_L_3 = ttk.Label(block_2, text='\u03C7bc', **h10bL_r)
        chi_ac_L_3 = ttk.Label(block_2, text='\u03C7ac', **h10bL_r)
        spin_E_3 = ttk.Entry(block_2, textvariable=self.spin_3, **r_w40)
        chi_aa_E_3 = ttk.Entry(block_2, textvariable=self.chi_aa_3, **r_w40)
        chi_bbcc_E_3 = ttk.Entry(block_2, textvariable=self.chi_bbcc_3, **r_w40)
        chi_ab_E_3 = ttk.Entry(block_2, textvariable=self.chi_ab_3, **r_w40)
        chi_bc_E_3 = ttk.Entry(block_2, textvariable=self.chi_bc_3, **r_w40)
        chi_ac_E_3 = ttk.Entry(block_2, textvariable=self.chi_ac_3, **r_w40)
        chi_aa_3_err_cb = ttk.Checkbutton(block_2, variable=self.chi_aa_3_err)
        chi_bbcc_3_err_cb = ttk.Checkbutton(block_2, variable=self.chi_bbcc_3_err)
        chi_ab_3_err_cb = ttk.Checkbutton(block_2, variable=self.chi_ab_3_err)
        chi_bc_3_err_cb = ttk.Checkbutton(block_2, variable=self.chi_bc_3_err)
        chi_ac_3_err_cb = ttk.Checkbutton(block_2, variable=self.chi_ac_3_err)
        nuc_3_hyperfine_L.grid(row=16, column=1, **cspan2_x2y10)
        nuc_3_fix_L.grid(row=16, column=2, **x2y10w)
        spin_L_3.grid(row=17, column=0, **x2y2e)
        chi_aa_L_3.grid(row=18, column=0, **x2y2e)
        chi_bbcc_L_3.grid(row=19, column=0, **x2y2e)
        chi_ab_L_3.grid(row=20, column=0, **x2y2e)
        chi_bc_L_3.grid(row=21, column=0, **x2y2e)
        chi_ac_L_3.grid(row=22, column=0, **x2y2e)
        spin_E_3.grid(row=17, column=1, **x2y2ew)
        chi_aa_E_3.grid(row=18, column=1, **x2y2ew)
        chi_bbcc_E_3.grid(row=19, column=1, **x2y2ew)
        chi_ab_E_3.grid(row=20, column=1, **x2y2ew)
        chi_bc_E_3.grid(row=21, column=1, **x2y2ew)
        chi_ac_E_3.grid(row=22, column=1, **x2y2ew)
        chi_aa_3_err_cb.grid(row=18, column=2, **x2y2)
        chi_bbcc_3_err_cb.grid(row=19, column=2, **x2y2)
        chi_ab_3_err_cb.grid(row=20, column=2, **x2y2)
        chi_bc_3_err_cb.grid(row=21, column=2, **x2y2)
        chi_ac_3_err_cb.grid(row=22, column=2, **x2y2)

        separator = ttk.Separator(block_2, orient='horizontal')
        separator.grid(row=23, column=0, columnspan=2, padx=2, pady=12, sticky='ew')
        # ==========================================================================================
        #                                       Buttons
        # ==========================================================================================
        write_single_B = ttk.Button(
            block_2, text='Write Pickett Files', style='h8b.TButton', command=self.write_single)
        write_iso_B = ttk.Button(
            block_2, text='Write Pickett Files: Set of Isotopomers',
            style='h8b.TButton', command=self.isotopomers)
        import_B = ttk.Button(
            block_2, text='Quick Import', style='h8b.TButton', command=self.quick_import)
        save = ttk.Button(
            block_2, text='Save Setup', style='h8b.TButton',
            command=lambda: page_funcs.save_page(self.attr_dict, self.text_box_dict))
        load = ttk.Button(
            block_2, text='Load Setup', style='h8b.TButton',
            command=lambda: page_funcs.load_page(self.attr_dict, tb_dict=self.text_box_dict))
        clear = ttk.Button(
            block_2, text='Defaults', style='h8b.TButton',
            command=lambda: page_funcs.clear_page(
                PickettWriter.default, self.attr_dict, self.text_box_dict))
        write_single_B.grid(row=27, column=0, columnspan=3, padx=10, pady=2, sticky='ew')
        write_iso_B.grid(row=28, column=0, columnspan=3, padx=10, pady=2, sticky='ew')
        separator = ttk.Separator(block_2, orient='horizontal')
        separator.grid(row=29, column=0, columnspan=2, padx=2, pady=5, sticky='ew')
        save.grid(row=31, column=0, columnspan=3, padx=10, pady=2, sticky='ew')
        load.grid(row=32, column=0, columnspan=3, padx=10, pady=2, sticky='ew')
        separator = ttk.Separator(block_2, orient='horizontal')
        separator.grid(row=33, column=0, columnspan=2, padx=2, pady=5, sticky='ew')
        import_B.grid(row=34, column=0, columnspan=3, padx=10, pady=2, sticky='ew')
        clear.grid(row=35, column=0, columnspan=3, padx=10, pady=2, sticky='ew')
        separator = ttk.Separator(block_2, orient='horizontal')
        separator.grid(row=36, column=0, columnspan=2, padx=2, pady=5, sticky='ew')

        table_L = ttk.Label(block_3, text='LaTeX Table Generator', **h12bL_c)
        piform_file_L = ttk.Label(block_3, text='File', **h10bL_r)
        caption_L = ttk.Label(block_3, text='Caption (Optional)', **h10bL_r)
        num_qns_L = ttk.Label(block_3, text='# quant. num.', **h10bL_r)
        preamble_L = ttk.Label(block_3, text='Preamble', **h10bL_r)

        piform_file_E = ttk.Entry(block_3, textvariable=self.piform_file, justify=c, width=50)
        num_qns_E = ttk.Entry(block_3, textvariable=self.num_qns, justify=c, width=50)
        self.caption_TB = tk.Text(
            block_3, relief='flat', font='Helvetica 10', wrap=tk.WORD, width=40, height=3)
        preamble_checkB = ttk.Checkbutton(block_3, variable=self.preamble)

        piform_file_B = ttk.Button(
            block_3, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(
                self.piform_file, eb_var=piform_file_E, ftype='pi'))
        table_L.grid(row=0, column=0, columnspan=3, **x2y2)
        piform_file_L.grid(row=1, column=0, **x2y2e)
        caption_L.grid(row=3, column=0, **x2y2e)
        num_qns_L.grid(row=2, column=0, **x2y2e)
        preamble_L.grid(row=4, column=0, **x2y2e)
        piform_file_E.grid(row=1, column=1, **x2y2e)
        self.caption_TB.grid(row=3, column=1, padx=2, pady=5, sticky='ew')
        num_qns_E.grid(row=2, column=1, **x2y2e)
        preamble_checkB.grid(row=4, column=1, **x2y2)
        piform_file_B.grid(row=1, column=2, **x2y2)

        self.caption_TB.delete('1.0', tk.END)
        self.caption_TB.insert('1.0', 'None')

        lnlst_LaTeX_B = ttk.Button(
            block_3, text='LaTeX: Line List', style='h8b.TButton',
            command=lambda: self.piform_LaTeX('line_list'))
        rc_LaTeX_B = ttk.Button(
            block_3, text='LaTeX: Rot. Constants', style='h8b.TButton',
            command=lambda: self.piform_LaTeX('rot_const'))
        lnlst_LaTeX_B.grid(row=6, column=0, columnspan=3, padx=10, pady=2, sticky='ew')
        rc_LaTeX_B.grid(row=7, column=0, columnspan=3, padx=10, pady=2, sticky='ew')

        separator = ttk.Separator(block_3, orient='horizontal')
        separator.grid(row=5, column=0, columnspan=3, padx=2, pady=12, sticky='ew')
        separator = ttk.Separator(block_3, orient='horizontal')
        separator.grid(row=8, column=0, columnspan=3, padx=2, pady=12, sticky='ew')
        block_1.grid(row=1, column=1, sticky='n')
        block_2.grid(row=1, column=3, sticky='n')
        block_3.grid(row=1, column=5, sticky='n')

        column_separator = ttk.Separator(frame, orient=tk.VERTICAL)
        column_separator.grid(row=1, column=0, rowspan=28, padx=20, sticky='ns')
        column_separator_2 = ttk.Separator(frame, orient=tk.VERTICAL)
        column_separator_2.grid(row=1, column=2, rowspan=28, padx=20, sticky='ns')
        column_separator_3 = ttk.Separator(frame, orient=tk.VERTICAL)
        column_separator_3.grid(row=1, column=4, rowspan=28, padx=20, sticky='ns')
        column_separator_4 = ttk.Separator(frame, orient=tk.VERTICAL)
        column_separator_4.grid(row=1, column=6, rowspan=28, padx=20, sticky='ns')

        self.text_box_dict = {'caption': self.caption_TB}
        self.page.enter_textbox(self.caption_TB)
        self.page.exit_textbox(self.caption_TB)

        self.attr_dict = {
            'A': self.A, 'B': self.B, 'C': self.C,
            'DJ': self.DJ, 'DJK': self.DJK, 'DK': self.DK, 'dJ': self.dJ, 'dK': self.dK,
            'muA': self.uA, 'muB': self.uB, 'muC': self.uC,
            'max_freq': self.max_freq, 'T': self.T, 'Jmax': self.Jmax,
            'start_freq': self.start_freq, 'end_freq': self.end_freq, 'fwhm': self.line_width,
            'spin_1': self.spin_1, 'chi_aa_1': self.chi_aa_1,
            'chi_bbcc_1': self.chi_bbcc_1, 'chi_ab_1': self.chi_ab_1, 'chi_bc_1': self.chi_bc_1,
            'chi_ac_1': self.chi_ac_1, 'chi_aa_1_err': self.chi_aa_1_err,
            'chi_bbcc_1_err': self.chi_bbcc_1_err, 'chi_ab_1_err': self.chi_ab_1_err,
            'chi_bc_1_err': self.chi_bc_1_err, 'chi_ac_1_err': self.chi_ac_1_err,
            'spin_2': self.spin_2, 'chi_aa_2': self.chi_aa_2, 'chi_bbcc_2': self.chi_bbcc_2,
            'chi_ab_2': self.chi_ab_2, 'chi_bc_2': self.chi_bc_2, 'chi_ac_2': self.chi_ac_2,
            'chi_aa_2_err': self.chi_aa_2_err, 'chi_bbcc_2_err': self.chi_bbcc_2_err,
            'chi_ab_2_err': self.chi_ab_2_err, 'chi_bc_2_err': self.chi_bc_2_err,
            'chi_ac_2_err': self.chi_ac_2_err,
            'spin_3': self.spin_3, 'chi_aa_3': self.chi_aa_3,
            'chi_bbcc_3': self.chi_bbcc_3, 'chi_ab_3': self.chi_ab_3, 'chi_bc_3': self.chi_bc_3,
            'chi_ac_3': self.chi_ac_3, 'chi_aa_3_err': self.chi_aa_3_err,
            'chi_bbcc_3_err': self.chi_bbcc_3_err, 'chi_ab_3_err': self.chi_ab_3_err,
            'chi_bc_3_err': self.chi_bc_3_err, 'chi_ac_3_err': self.chi_ac_3_err,
            'sim_spec': self.sim_spec, 'piform_file': self.piform_file, 'preamble': self.preamble,
            'num_qns': self.num_qns}

    def partition_entry(self, max_ghz, T, Jmax):
        """
        Quick fill for partition function parameters.

        Parameters:
            max_ghz (float):
                Frequency upper bound.
                Units: GHz
            T (float):
                Temperature.
                Units: K
            Jmax (int):
                J quantum number upper bound.
        """
        self.max_freq.set(max_ghz)
        self.T.set(T)
        self.Jmax.set(Jmax)

    def spec_prediction_entry(self, start, end, width):
        """
        Quick fill for spectral prediction parameters.

        Parameters:
            start (int):
                Starting frequency.
                Units: MHz
            end (int):
                Ending frequency.
                Units: MHz
            width (float):
                Full width half max.
                Units: MHz
        """
        self.start_freq.set(start)
        self.end_freq.set(end)
        self.line_width.set(width)

    def quick_import(self):
        """
        Run when 'Quick Import' button is pressed.

        Accept *.int, *.cat, *.lin, *.pi, *.par, *.var file types.
        Searches for rigid rotor constants, quartic distortion constants, quadrupolar constants,
        and dipole components. If a certain val is not found in the file that is selected, val is
        searched for in files with different file extensions and the same base file name.
        For example, if 'molecule.par' is uploaded, the dipole components are found 'molecule.int'.
        """
        file = page_funcs.open_file(ftype='quick_import')
        ext = os.path.splitext(file)[1]
        if ext in ['.int', '.INT', '.cat', '.CAT', '.lin', '.LIN', '.pi', '.PI']:
            f = os.path.splitext(file)[0]
            if os.path.isfile(f + '.par'):
                file = f + '.par'
            else:
                if os.path.isfile(f + '.var'):
                    file = f + '.var'
                else:
                    if os.path.isfile(f + '.pi'):
                        file = f + '.pi'
                    else:
                        msg = "No supported files found in same directory as %s" % file
                        showerror(title="File Not Found", message=msg)
        int_file = os.path.splitext(file)[0] + '.int'
        import_rigid_rotor(self.A, self.B, self.C, file=file)
        import_quartic_distortion(self.DJ, self.DJK, self.DK, self.dJ, self.dK, file=file)
        import_quadrupolar_constants(
            self.spin_1, self.chi_aa_1, self.chi_bbcc_1, self.chi_ab_1, self.chi_bc_1,
            self.chi_ac_1, self.spin_2, self.chi_aa_2, self.chi_bbcc_2, self.chi_ab_2,
            self.chi_bc_2, self.chi_ac_2, self.spin_3, self.chi_aa_3, self.chi_bbcc_3,
            self.chi_ab_3, self.chi_bc_3, self.chi_ac_3, file=file)
        try:
            import_dipole_components(self.uA, self.uB, self.uC, file=int_file)
        except IOError:
            self.uA.set(0)
            self.uB.set(0)
            self.uC.set(0)

    def write_single(self, file=None, all_qdc=True):
        """
        Run when 'Write Pickett Files' button is pressed.

        Generates *.par, *.var, *.cat, *.out, and *.int files using information from GUI.
        Optionally generates spectral simulation.

        Parameters:
            file (str):
                File name. If None, file explorer will open, and user can name the file there.
                Default: None
            all_qdc (bool):
                Set whether to include zero-valued quartic distortion constants in *.par/*.var
                files.
                Default: True
        """
        A = self.A.get()
        B = self.B.get()
        C = self.C.get()
        A_err = self.A_err.get()
        B_err = self.B_err.get()
        C_err = self.C_err.get()
        DJ = self.DJ.get()
        DJK = self.DJK.get()
        DK = self.DK.get()
        dJ = self.dJ.get()
        dK = self.dK.get()
        DJ_err = self.DJ_err.get()
        DJK_err = self.DJK_err.get()
        DK_err = self.DK_err.get()
        dJ_err = self.dJ_err.get()
        dK_err = self.dK_err.get()
        uA = self.uA.get()
        uB = self.uB.get()
        uC = self.uC.get()
        max_freq = self.max_freq.get()
        T = self.T.get()
        Jmax = self.Jmax.get()
        start_freq = self.start_freq.get()
        end_freq = self.end_freq.get()
        line_width = self.line_width.get()
        spin_1 = self.spin_1.get()
        chi_aa_1 = self.chi_aa_1.get()
        chi_bbcc_1 = self.chi_bbcc_1.get()
        chi_ab_1 = self.chi_ab_1.get()
        chi_bc_1 = self.chi_bc_1.get()
        chi_ac_1 = self.chi_ac_1.get()
        chi_aa_1_err = self.chi_aa_1_err.get()
        chi_bbcc_1_err = self.chi_bbcc_1_err.get()
        chi_ab_1_err = self.chi_ab_1_err.get()
        chi_bc_1_err = self.chi_bc_1_err.get()
        chi_ac_1_err = self.chi_ac_1_err.get()
        spin_2 = self.spin_2.get()
        chi_aa_2 = self.chi_aa_2.get()
        chi_bbcc_2 = self.chi_bbcc_2.get()
        chi_ab_2 = self.chi_ab_2.get()
        chi_bc_2 = self.chi_bc_2.get()
        chi_ac_2 = self.chi_ac_2.get()
        chi_aa_2_err = self.chi_aa_2_err.get()
        chi_bbcc_2_err = self.chi_bbcc_2_err.get()
        chi_ab_2_err = self.chi_ab_2_err.get()
        chi_bc_2_err = self.chi_bc_2_err.get()
        chi_ac_2_err = self.chi_ac_2_err.get()
        spin_3 = self.spin_3.get()
        chi_aa_3 = self.chi_aa_3.get()
        chi_bbcc_3 = self.chi_bbcc_3.get()
        chi_ab_3 = self.chi_ab_3.get()
        chi_bc_3 = self.chi_bc_3.get()
        chi_ac_3 = self.chi_ac_3.get()
        chi_aa_3_err = self.chi_aa_3_err.get()
        chi_bbcc_3_err = self.chi_bbcc_3_err.get()
        chi_ab_3_err = self.chi_ab_3_err.get()
        chi_bc_3_err = self.chi_bc_3_err.get()
        chi_ac_3_err = self.chi_ac_3_err.get()
        if not all_qdc:
            if DJ in [0, '[0.]']:
                DJ = None
            if DJK in [0, '[0.]']:
                DJK = None
            if DK in [0, '[0.]']:
                DK = None
            if dJ in [0, '[0.]']:
                dJ = None
            if dK in [0, '[0.]']:
                dK = None
        if spin_1 == 0:
            spin_1 = None
        if chi_aa_1 in [0, '[0.]']:
            chi_aa_1 = None
        if chi_bbcc_1 in [0, '[0.]']:
            chi_bbcc_1 = None
        if chi_ab_1 in [0, '[0.]']:
            chi_ab_1 = None
        if chi_bc_1 in [0, '[0.]']:
            chi_bc_1 = None
        if chi_ac_1 in [0, '[0.]']:
            chi_ac_1 = None
        if spin_2 == 0:
            spin_2 = None
        if chi_aa_2 in [0, '[0.]']:
            chi_aa_2 = None
        if chi_bbcc_2 in [0, '[0.]']:
            chi_bbcc_2 = None
        if chi_ab_2 in [0, '[0.]']:
            chi_ab_2 = None
        if chi_bc_2 in [0, '[0.]']:
            chi_bc_2 = None
        if chi_ac_2 in [0, '[0.]']:
            chi_ac_2 = None
        if spin_3 == 0:
            spin_3 = None
        if chi_aa_3 in [0, '[0.]']:
            chi_aa_3 = None
        if chi_bbcc_3 in [0, '[0.]']:
            chi_bbcc_3 = None
        if chi_ab_3 in [0, '[0.]']:
            chi_ab_3 = None
        if chi_bc_3 in [0, '[0.]']:
            chi_bc_3 = None
        if chi_ac_3 in [0, '[0.]']:
            chi_ac_3 = None
        if file is None:
            file = page_funcs.save_file()
        basename = os.path.basename(file)
        file_dir = os.path.dirname(file)
        Pickett.copy_spfit_spcat_piform(self.controller.pickett_dir, file_dir)
        fname = basename.split('.')[0]
        os.chdir(file_dir)

        int_file = Pickett.Int_File(
            muA=uA, muB=uB, muC=uC, A=A, B=B, C=C, temp=T, fend=Jmax, fqlim=max_freq)
        int_file.save(fname=fname)

        par = Pickett.Par_Var(
            A=A, B=B, C=C, A_err=A_err, B_err=B_err, C_err=C_err, DJ=DJ, DJK=DJK, DK=DK, dJ=dJ,
            dK=dK, DJ_err=DJ_err, DJK_err=DJK_err, DK_err=DK_err, dJ_err=dJ_err, dK_err=dK_err,
            spin_1=spin_1, chi_aa_1=chi_aa_1, chi_bbcc_1=chi_bbcc_1, chi_ab_1=chi_ab_1,
            chi_bc_1=chi_bc_1, chi_ac_1=chi_ac_1, chi_aa_1_err=chi_aa_1_err,
            chi_bbcc_1_err=chi_bbcc_1_err, chi_ab_1_err=chi_ab_1_err, chi_bc_1_err=chi_bc_1_err,
            chi_ac_1_err=chi_ac_1_err, spin_2=spin_2, chi_aa_2=chi_aa_2, chi_bbcc_2=chi_bbcc_2,
            chi_ab_2=chi_ab_2, chi_bc_2=chi_bc_2, chi_ac_2=chi_ac_2, chi_aa_2_err=chi_aa_2_err,
            chi_bbcc_2_err=chi_bbcc_2_err, chi_ab_2_err=chi_ab_2_err, chi_bc_2_err=chi_bc_2_err,
            chi_ac_2_err=chi_ac_2_err, spin_3=spin_3, chi_aa_3=chi_aa_3, chi_bbcc_3=chi_bbcc_3,
            chi_ab_3=chi_ab_3, chi_bc_3=chi_bc_3, chi_ac_3=chi_ac_3, chi_aa_3_err=chi_aa_3_err,
            chi_bbcc_3_err=chi_bbcc_3_err, chi_ab_3_err=chi_ab_3_err, chi_bc_3_err=chi_bc_3_err,
            chi_ac_3_err=chi_ac_3_err)
        var = Pickett.Par_Var(
            A=A, B=B, C=C, A_err=A_err, B_err=B_err, C_err=C_err, DJ=DJ, DJK=DJK, DK=DK, dJ=dJ,
            dK=dK, DJ_err=DJ_err, DJK_err=DJK_err, DK_err=DK_err, dJ_err=dJ_err, dK_err=dK_err,
            spin_1=spin_1, chi_aa_1=chi_aa_1, chi_bbcc_1=chi_bbcc_1, chi_ab_1=chi_ab_1,
            chi_bc_1=chi_bc_1, chi_ac_1=chi_ac_1, chi_aa_1_err=chi_aa_1_err,
            chi_bbcc_1_err=chi_bbcc_1_err, chi_ab_1_err=chi_ab_1_err, chi_bc_1_err=chi_bc_1_err,
            chi_ac_1_err=chi_ac_1_err, spin_2=spin_2, chi_aa_2=chi_aa_2, chi_bbcc_2=chi_bbcc_2,
            chi_ab_2=chi_ab_2, chi_bc_2=chi_bc_2, chi_ac_2=chi_ac_2, chi_aa_2_err=chi_aa_2_err,
            chi_bbcc_2_err=chi_bbcc_2_err, chi_ab_2_err=chi_ab_2_err, chi_bc_2_err=chi_bc_2_err,
            chi_ac_2_err=chi_ac_2_err, spin_3=spin_3, chi_aa_3=chi_aa_3, chi_bbcc_3=chi_bbcc_3,
            chi_ab_3=chi_ab_3, chi_bc_3=chi_bc_3, chi_ac_3=chi_ac_3, chi_aa_3_err=chi_aa_3_err,
            chi_bbcc_3_err=chi_bbcc_3_err, chi_ab_3_err=chi_ab_3_err, chi_bc_3_err=chi_bc_3_err,
            chi_ac_3_err=chi_ac_3_err)
        par.save(fname=fname, extension='.par', all_qdc=False)
        var.save(fname=fname, extension='.var', all_qdc=False)
        Pickett.spcat_run(fname)
        cat_file = fname + '.cat'
        cat = Pickett.Cat(file=cat_file)
        max_freq_mhz = max_freq * 1000
        filtered_cat = cat.filter(freq_min=start_freq, freq_max=max_freq_mhz)
        filtered_line_list = cat.line_list(dictionary=filtered_cat)
        if self.sim_spec.get() == 1:
            sim = cat.simulate(
                filtered_line_list, freq_min=start_freq, freq_max=end_freq, fwhm=line_width,
                save=True, fname=fname)

    def isotopomers(self):
        """
        Run when 'Write Pickett Files: Set of Isotopomers' button is pressed.

        Write Pickett files for all 13C isotopomers of a molecule.

        Must provide *.csv file containing the rigid rotor constants for the isotopomers.
        Use RotConstPredictions.isotopomer_constants() to generate this file. Select this file
        from the file dialog box that opens when this method runs.
        """
        file = page_funcs.open_file(
            ftype='csv', title='CSV Containing Isotopomer Rigid Rotor Constants')
        if file:
            fname = os.path.splitext(os.path.abspath(file))[0]
            Pickett.copy_spfit_spcat_piform(self.controller.pickett_dir, os.path.dirname(file))
            os.chdir(os.path.dirname(file))
            df = pd.read_csv(file)
            carbons = df.loc[(df['isotope'] == '13C')]
            carbons = carbons.reset_index()
            for x in range(len(carbons)):
                row = carbons.loc[x]
                i = row['index']
                isotopomer_fname = fname + '_C' + str(i)
                self.A.set(row['A'])
                self.B.set(row['B'])
                self.C.set(row['C'])
                self.write_single(file=isotopomer_fname)

    def piform_LaTeX(self, table_type):
        """
        Run when either of the LaTeX buttons are pressed.

        The button that is pressed determines what is passed as table_type.

        If table_type == line_list:
            Run Pickett.Piform.line_list_LaTeX(), which generates a LaTeX table containing assigned
            transitions.
        If table_type == rot_const:
            Run Pickett.Piform.rot_const_LaTeX(), which generates a LaTeX table containing
            rotational constants.

        Compile output file in LaTeX to render the table.

        Parameters:
            table_type (str):
                Either 'line_list' or 'rot_const'.
         """
        piform = Pickett.Piform(self.piform_file.get())
        if piform:
            num_qns = int(self.num_qns.get())
            preamble = self.preamble.get()
            caption = self.caption_TB.get("1.0", "end-1c")
            if caption == 'None':
                caption = None
            bname = os.path.splitext(self.piform_file.get())[0]
            fname = page_funcs.save_file(initialfile=bname, ftype='tex', defaultextension='.tex')
            if table_type == 'line_list':
                piform.line_list_LaTeX(
                    num_qns=num_qns, preamble=preamble, caption=caption, save=True, fname=fname)
            elif table_type == 'rot_const':
                zero_qdc = askyesnocancel(
                    title='Zero-Valued Quartic Distortion Constants',
                    message='Include zero-valued quartic distortion constants in the table?')
                piform.rot_const_LaTeX(
                    num_qns=num_qns, preamble=preamble, caption=caption, show_zero_qdc=zero_qdc,
                    save=True, fname=fname)


def import_rigid_rotor(A_var, B_var, C_var, file=None):
    """
    Import rigid rotor constants from file to tkinter variables that can be displayed on the GUI.

    Supports a number of file types. See PageFormat.ftype_dict['rigidrotor']
    for accepted file types. File path is optional. If no file is given,
    file dialog will be opened where you can select a file.

    Parameters:
        A_var (tk.DoubleVar):
            A rigid rotor constant.
        B_var (tk.DoubleVar):
            B rigid rotor constant.
        C_var (tk.DoubleVar):
            C rigid rotor constant.
        file (str):
            File path. Optional. If no file is given, file dialog is opened where you can select
            a file.
            Default: None
    """
    if file is None:
        file = page_funcs.open_file(ftype='rigidrotor')  # todo
    if not file:
        return
    else:
        try:
            ext = os.path.splitext(file)[1]
            if ext in ['.in', '.IN']:
                file_list = [row for row in open(file, 'r')]
                RC_line = int(file_list.index(
                    '# GROUND STATE A, B AND C ROTATIONAL CONSTANTS:\n') + 1)
                stripped_RC = re.sub(' +', ' ', file_list[RC_line]).strip().split(' ')
                RC = [abs(float(x)) for x in stripped_RC[0:3]]
                A, B, C = RC[0], RC[1], RC[2]
            elif ext in ['.out', '.OUT', '.log', '.LOG']:
                out_list = [row for row in open(file, 'r')]
                RC_line = out_list[out_list.index(' Rotational constants (MHZ):\n') + 1]
                stripped_RC = re.sub(' +', ' ', RC_line).strip().split(' ')
                RC = [abs(float(x)) for x in stripped_RC[0:3]]
                A, B, C = RC[0], RC[1], RC[2]
            elif ext in ['.par', '.PAR', '.var', '.VAR']:
                par_var = Pickett.Par_Var(file=file)
                A, B, C = '{:.8f}'.format(float(par_var.attributes['A'])), '{:.8f}'.format(
                    float(par_var.attributes['B'])), '{:.8f}'.format(float(par_var.attributes['C']))
            elif ext in ['.pi', '.PI']:
                piform = Pickett.Piform(file=file)
                A, B, C = piform.dict['a'], piform.dict['b'], piform.dict['c']
        except ValueError as e:
            A, B, C = 'Error', 'Error', 'Error'
        A_var.set(A)
        B_var.set(B)
        C_var.set(C)


def import_dipole_components(A_var, B_var, C_var, file=None):
    """
    Import dipole components from file to tkinter variables that can be displayed on the GUI.

    Supports a number of file types. See PageFormat.ftype_dict['dipole']
    for accepted file types. File path is optional. If no file is given,
    file dialog is opened where you can select a file.

    Parameters:
        A_var (tk.DoubleVar):
            A dipole component.
        B_var (tk.DoubleVar):
            B dipole component.
        C_var (tk.DoubleVar):
            C dipole component.
        file (str):
            File path. Optional. If no file is given, file dialog is opened where you can select
            a file.
            Default: None
    """
    if file is None:
        file = page_funcs.open_file(ftype='dipole')
    if not file:
        return
    else:
        try:
            ext = os.path.splitext(file)[1]
            if ext in ['.out', '.OUT', '.log', '.LOG']:
                out_list = [row for row in open(file, 'r')]
                dipole_line = out_list[out_list.index(' Dipole moment (Debye):\n') + 1]
                stripped_dipole = re.sub(' +', ' ', dipole_line).strip().split(' ')
                dipole_components = [abs(float(x)) for x in stripped_dipole[0:3]]
                muA, muB, muC = dipole_components[0], dipole_components[1], dipole_components[2]
            elif ext in ['.int', '.INT']:
                int_file = Pickett.Int_File(file=file)
                muA, muB, muC = int_file.dict['muA'], int_file.dict['muB'], int_file.dict['muC']
        except ValueError:
            muA, muB, muC = 'Error', 'Error', 'Error'
        A_var.set(muA)
        B_var.set(muB)
        C_var.set(muC)


def import_quartic_distortion(DJ_var, DJK_var, DK_var, dJ_var, dK_var, file=None):
    """
    Import quartic distortion constants from file to tkinter variables that can be displayed on GUI.

    Supports a number of file types. See PageFormat.ftype_dict['qdc'] for accepted file types.
    File path is optional. If no file is given, file dialog is opened where you can select a file.

    Parameters:
        DJ_var (tk.DoubleVar):
            DJ distortion constant.
        DJK_var (tk.DoubleVar):
            DJK distortion constant.
        DK_var (tk.DoubleVar):
            DK distortion constant.
        dJ_var (tk.DoubleVar):
            dJ distortion constant.
        dK_var (tk.DoubleVar):
            dK distortion constant.
        file (str):
            File path. Optional. If no file is given, file dialog is opened where you can select
            a file.
            Default: None
    """
    if file is None:
        file = page_funcs.open_file(ftype='qdc')
    if not file:
        return
    else:
        try:
            ext = os.path.splitext(file)[1]
            if ext in ['.in', '.IN']:
                file_list = [row for row in open(file, 'r')]
                distortion = [file_list.index(
                    '# GROUND STATE <DJ>, <DJK> & <DK> WATSON D DISTORTION CONSTANTS:\n') + 1,
                              file_list.index(
                                  '# GROUND STATE <dJ> & <dK> WATSON D DISTORTION:\n') + 1]
                DC = []
                for index in distortion:
                    DC.extend(re.sub(' +', ' ', file_list[index]).strip().split(' '))
                DC = [float(x) for x in DC]
                DJ, DJK, DK, dJ, dK = DC[0], DC[1], DC[2], DC[3], DC[4]
            elif ext in ['.par', '.PAR', '.var', '.VAR']:
                par_var = Pickett.Par_Var(file=file)
                DJ = par_var.attributes['DJ']
                DJK = par_var.attributes['DJK']
                DK = par_var.attributes['DK']
                dJ = par_var.attributes['dJ']
                dK = par_var.attributes['dK']
            elif ext in ['.pi', '.PI']:
                piform = Pickett.Piform(file=file)
                DJ = piform.dict['DJ']
                DJK = piform.dict['DJK']
                DK = piform.dict['DK']
                dJ = piform.dict['dJ']
                dK = piform.dict['dK']
        except ValueError:
            DJ, DJK, DK, dJ, dK = 'Error', 'Error', 'Error', 'Error', 'Error'
        x = ((DJ, DJ_var), (DJK, DJK_var), (DK, DK_var),
             (dJ, dJ_var), (dK, dK_var))
        for const, var in x:
            if const not in [-0.00000000000, 0.00000000000, '[0.]', '-0.0E-003', '0.0E-003', None]:
                var.set("{0:.11f}".format(float(const)))
            else:
                var.set(0)


def import_quadrupolar_constants(
        spin_1_var, aa_1_var, bbcc_1_var, ab_1_var, bc_1_var, ac_1_var,
        spin_2_var, aa_2_var, bbcc_2_var, ab_2_var, bc_2_var, ac_2_var,
        spin_3_var, aa_3_var, bbcc_3_var, ab_3_var, bc_3_var, ac_3_var,
        file=None):
    """
    Import quadrupolar constants from file for up to three nuclei to tkinter variables.

    tkinter variables can be displayed on GUI.
    Supports a number of file types. See PageFormat.ftype_dict['quick_import']
    for accepted file types. File path is optional. If no file is given, file
    dialog is opened where you can select a file.

    Parameters:
        spin_1_var(tk.DoubleVar):
            nuclear spin of nucleus 1
        aa_1_var (tk.DoubleVar):
            chi_aa quad constant of nucleus 1
        bbcc_1_var (tk.DoubleVar):
            chi_bbcc quad constant of nucleus 1
        ab_1_var (tk.DoubleVar):
            chi_ab quad constant of nucleus 1
        bc_1_var (tk.DoubleVar):
            chi_bc quad constant of nucleus 1
        ac_1_var (tk.DoubleVar):
            chi_ac quad constant of nucleus 1
        spin_2_var(tk.DoubleVar):
            nuclear spin of nucleus 2
        aa_2_var (tk.DoubleVar):
            chi_aa quad constant of nucleus 2
        bbcc_2_var (tk.DoubleVar):
            chi_aabb quad constant of nucleus 2
        ab_2_var (tk.DoubleVar):
            chi_ab quad constant of nucleus 2
        bc_2_var (tk.DoubleVar):
            chi_bc quad constant of nucleus 2
        ac_2_var (tk.DoubleVar):
            chi_ac quad constant of nucleus 2
        spin_3_var(tk.DoubleVar):
            nuclear spin of nucleus 3
        aa_3_var (tk.DoubleVar):
            chi_aa quad constant of nucleus 3
        bbcc_3_var (tk.DoubleVar):
            chi_bbcc quad constant of nucleus 3
        ab_3_var (tk.DoubleVar):
            chi_ab quad constant of nucleus 3
        bc_3_var (tk.DoubleVar):
            chi_bc quad constant of nucleus 3
        ac_3_var (tk.DoubleVar):
            chi_ac quad constant of nucleus 3
        file (str):
            File path. Optional. If no file is given, file dialog is opened where you can select
            a file.
            Default: None
    """
    if file is None:
        file = page_funcs.open_file(ftype='quick_import')
    if not file:
        return
    else:
        try:
            ext = os.path.splitext(file)[1]
            if ext in ['.par', '.PAR', '.var', '.VAR']:
                par_var = Pickett.Par_Var(file=file)
                spin_1 = par_var.attributes['spin_1']
                aa_1 = par_var.attributes['chi_aa_1']
                bbcc_1 = par_var.attributes['chi_bbcc_1']
                ab_1 = par_var.attributes['chi_ab_1']
                bc_1 = par_var.attributes['chi_bc_1']
                ac_1 = par_var.attributes['chi_ac_1']
                spin_2 = par_var.attributes['spin_2']
                aa_2 = par_var.attributes['chi_aa_2']
                bbcc_2 = par_var.attributes['chi_bbcc_2']
                ab_2 = par_var.attributes['chi_ab_2']
                bc_2 = par_var.attributes['chi_bc_2']
                ac_2 = par_var.attributes['chi_ac_2']
                spin_3 = par_var.attributes['spin_3']
                aa_3 = par_var.attributes['chi_aa_3']
                bbcc_3 = par_var.attributes['chi_bbcc_3']
                ab_3 = par_var.attributes['chi_ab_3']
                bc_3 = par_var.attributes['chi_bc_3']
                ac_3 = par_var.attributes['chi_ac_3']
                spins = ((spin_1, spin_1_var), (spin_2, spin_2_var), (spin_3, spin_3_var))
            elif ext in ['.pi', '.PI']:
                piform = Pickett.Piform(file=file)
                spin_1 = 0
                spin_2 = 0
                spin_3 = 0
                aa_1 = piform.dict['chi_aa_1']
                bbcc_1 = piform.dict['chi_bbcc_1']
                ab_1 = piform.dict['chi_ab_1']
                bc_1 = piform.dict['chi_bc_1']
                ac_1 = piform.dict['chi_ac_1']
                aa_2 = piform.dict['chi_aa_2']
                bbcc_2 = piform.dict['chi_bbcc_2']
                ab_2 = piform.dict['chi_ab_2']
                bc_2 = piform.dict['chi_bc_2']
                ac_2 = piform.dict['chi_ac_2']
                aa_3 = piform.dict['chi_aa_3']
                bbcc_3 = piform.dict['chi_bbcc_3']
                ab_3 = piform.dict['chi_ab_3']
                bc_3 = piform.dict['chi_bc_3']
                ac_3 = piform.dict['chi_ac_3']
        except ValueError:
            spin_1 = 'Error'
            aa_1 = 'Error'
            bbcc_1 = 'Error'
            ab_1 = 'Error'
            bc_1 = 'Error'
            ac_1 = 'Error'
            spin_2 = 'Error'
            aa_2 = 'Error'
            bbcc_2 = 'Error'
            ab_2 = 'Error'
            bc_2 = 'Error'
            ac_2 = 'Error'
            spin_3 = 'Error'
            aa_3 = 'Error'
            bbcc_3 = 'Error'
            ab_3 = 'Error'
            bc_3 = 'Error'
            ac_3 = 'Error'
        spins = ((spin_1, spin_1_var), (spin_2, spin_2_var), (spin_3, spin_3_var))
        x = ((aa_1, aa_1_var), (bbcc_1, bbcc_1_var), (ab_1, ab_1_var), (bc_1, bc_1_var),
             (ac_1, ac_1_var), (aa_2, aa_2_var), (bbcc_2, bbcc_2_var), (ab_2, ab_2_var),
             (bc_2, bc_2_var), (ac_2, ac_2_var), (aa_3, aa_3_var), (bbcc_3, bbcc_3_var),
             (ab_3, ab_3_var), (bc_3, bc_3_var), (ac_3, ac_3_var))
        for const, var in x:
            if const not in [-0.00000000000, 0.00000000000, '[0.]', '-0.0E-003', '0.0E-003', None]:
                var.set("{0:.11f}".format(float(const)))
            else:
                var.set(0)
        if spins:
            for const, var in spins:
                var.set("{0:.0f}".format(float(const)))
