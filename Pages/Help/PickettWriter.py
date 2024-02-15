"""
Author: Channing West
Changelog: 8/14/2022
"""
from tkinter import Text, WORD
from tkinter.ttk import Frame
from Pages.PageFormat import PageFormat

e = "\n\
    Pickett Writer Help\n\n\
        - Buttons:\n\
                IMPORT\n\
                    Depending on which IMPORT button is pressed, import either rigid rotor constants, quartic distortion constants, or dipole components from accepted file extensions.\n\
                        File extensions supported:\n\
                            - Rigid rotor: *.pi, *.par, *.var, *.in, *.out, *.log \n\
                            - Quartic distortion: *.pi, *.par, *.var, *.in\n\
                            - Dipole Components: *.int, *.out, *.log\n\
                QUICK_IMPORT\n\
                    Search for rigid rotor constants, quartic distortion constants, quadrupolar constants, and dipole components from a set of Pickett files (*.par, *.var, *.cat, *.out, and *.int).\n\
                    Any file from the set of Pickett files can be selected, assuming the other files exist in the same directory and have the same base name. For example, if 'molecule.par' is uploaded, \n\
                    the dipole components are found 'molecule.int'.\n\
                WRITE PICKETT FILES\n\
                    Generate *.par, *.var, *.cat, *.out, and *.int files using GUI values. Optionally generate spectral simulation.\n\
                WRITE PICKETT FILES: SET OF ISOTOPOMERS\n\
                    Write Pickett files for all 13C isotopomers of a molecule.\n\
                        - To use this button, you need to have produced a *.csv file containing the rotational constants of the isotopomers. This can be generated in the 'Predict Rotational Constants' module.\n\
                LATEX: LINE LIST\n\
                    Generate a LaTeX table containing assigned transitions. Table includes quantum numbers, frequencies, and obs. - calc. values for each assigned transition.\n\
                LATEX: ROT. CONSTANTS\n\
                    Generate a LaTeX table containing rotational constants. Table includes rotational constants, number of assigned transitions, and RMS of the fit.\n\
        - Checkbuttons:\n\
                FIX\n\
                    Check to fix the constant, thus, setting the uncertainty to 1e-20.\n\
                SIMULATE\n\
                    Check to produce spectral simulation after writing Pickett files.\n\
                PREAMBLE\n\
                    Check to write preamble in output of LaTeX tables. Include preamble for new LaTeX document. Not necessary if planning to add table to existing LaTeX document.\n\
        - Entry Boxes:\n\
                # of quant. num.\n\
                    This value is required to create the correct unmber of columns in the table.\n\
                    For no quads -> 3\n\
                    For 1 quad constant -> 4\n\
                    etc.\n\n\
    ===============================================================================================================================================================================\n\n\n\
    General Help\n\n\
        Save and load page setups:\n\
                - Some pages have the following buttons near the top of the page allowing the user to save and reload page setups.\n\
                - Buttons:\n\
                        SAVE SETUP\n\
                            Save values from entry boxes, radiobuttons, check boxes, notes, omitted points in *.pickle file. Easily reproduce previous calculations by loading this file at a later time using the LOAD button. \n\
                            Calculation outputs are not saved in *.pickle files in order to reduce file size. To plot outputs, calculations must be performed again. Imported files must be in the same location as when the *.pickle\n\
                            file was saved\n\
                        LOAD SETUP\n\
                            Load previously saved values for entry boxes, radiobuttons, check boxes, notes, omitted points from *.pickle. Easily reproduce previous calculations. However, calculation outputs are not saved in *.pickle\n\
                            files. Calculations must to performed again to plot results.\n\
                        DEFAULTS\n\
                            Restore entry boxes, radiobuttons, check boxes, notes, omitted points to their default values.\n\n\
        Buttons at the bottom of all pages:\n\
                BACK TO NAVIGATOR\n\
                    Go to navigator page.\n\
                SETTINGS\n\
                    Redirect to page where program settings can be changed. Changes to settings are saved on program exit.\n\
                HELP\n\
                    Redirect to page specific instructions for use.\n\
                EXIT APPLICATION\n\
                    Close program."


class pickettWriterHelp(Frame):
    """ Generate help page for PickettWriter. """
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Pickett Writer Help"
        h10 = 'Helvetica 10'
        f1 = Frame(frame)
        f1.grid(row=0, column=0)
        tb = Text(f1, width=200, height=60, relief='sunken', font=h10, wrap=WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')

