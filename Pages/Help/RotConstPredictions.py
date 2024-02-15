"""
Author: Channing West
Changelog: 8/14/2022
"""
from tkinter import Text, WORD
from tkinter.ttk import Frame
from Pages.PageFormat import PageFormat

e = "\n\
    Predict Rotational Constants Help\n\n\
        1a. Provide *.out or *.log file to extract optimized rotational constants and dipole components to *.csv file.\n\
                - Upload a single or multiple files from the file explorer. CTRL + click to select multiple files in file explorer.\n\
                - Mixed *.out and *.log files are fine.\n\n\
        1b. Provide *.gjf file(s) to calculate rotational constants of structure(s) and save to *.csv file.\n\n\
                - Upload a single or multiple files from the file explorer. CTRL + click to select multiple files in file explorer.\n\
                - Mixed *.out and *.log files are fine.\n\n\
        2.  Provide *.out or *.log file and experimental rotational constants to calculate the rotational constants of all common isotopomers. Constants are saved in *.csv file.\n\
            In *.csv file, the normal species is labeled 'NS'. The atom numbering reflects the numbering from the *.log/*.out file.\n\n\
    ===============================================================================================================================================================================\n\n\n\
    General Help\n\n\
        Buttons at the bottom of all pages:\n\
                BACK TO NAVIGATOR\n\
                    Go to navigator page.\n\
                SETTINGS\n\
                    Redirect to page where program settings can be changed. Changes to settings are saved on program exit.\n\
                HELP\n\
                    Redirect to page specific instructions for use.\n\
                EXIT APPLICATION\n\
                    Close program."



class rcpHelp(Frame):
    """ Generate help page for RotConstPredictions """
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Predict Rotational Constants Help"
        h10 = 'Helvetica 10'
        f1 = Frame(frame)
        f1.grid(row=0, column=0)
        tb = Text(f1, width=200, height=60,relief='sunken', font=h10, wrap=WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')

