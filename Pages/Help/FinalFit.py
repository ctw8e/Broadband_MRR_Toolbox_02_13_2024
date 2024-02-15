"""
Author: Channing West
Changelog: 8/14/2022
"""
import tkinter as tk
import tkinter.ttk as ttk
from Pages.PageFormat import PageFormat

e = "\n\
    Final Fit Help\n\n\
        This module does not serve the same purpose as Auto-Fit. The purpose of this module is to automate the Pickett suite (SPCAT, SPFIT, PIFORM, AABS) spectral assignment process if you already have a \n\
        reasonably fit spectrum, like a *.cat file generated using a JB95 fit with reasonable care taken when selecting transition centers. \n\n\
        Logic\n\
            1.  Search for line matches in experimental peak pick and *.cat file.\n\
            2.  Set inital distortion constants in *.par file.\n\
            3.  Run SPFIT.\n\
            4.  Check *.pi file for bad distortion constants.\n\
            5.  Iteratively remove bad distortion constants from *.par, running SPFIT and SPCAT at the end of each iteration.\n\
                    5a. Search *.pi for constants characterized as 'Worst fitted constants, with greater than 20% uncertainty' and remove -> Run SPFIT and SPCAT -> Repeat until all constants pass\n\
                    5b. Search *.pi for constants with standard error greater than constant and remove -> Run SPFIT and SPCAT -> Repeat until all constants pass.\n\
            6.  Iteratively remove transitions over 'Max. obs.-calc.' limit from fit. Run SPFIT and SPCAT at the end of each iteration.\n\
                    Search *.pi for transitions over 'Max. obs.-calc.' value and remove -> Run SPFIT and SPCAT -> Repeat until all assigned transitions under 'Max. obs.-calc.'\n\
            7.  Transitions that pass the 'Max. obs.-calc.' limit are fit to Gaussian line shape, and center frequencies are assigned. Line centers plotted as green dashed lines on plot after fit.\n\
            8.  Final SPFIT.\n\
            9.  Fianl SPCAT.\n\
            10. Display results.\n\n\
        1.  Inputs\n\
                - To fit spectra, *.par and *.int file need to be in the same directory and have the same base name as the *.cat file that is uploaded in this section.\n\
                - Entry Boxes:\n\
                        Peak pick threshold:\n\
                            Minimum experimental transition intensity. Use PLOT and ZOOM to find appropriate threshold.\n\
                        Freq. match:\n\
                            (observed frequency - calculated frequency) limit when finding transition matches before fit.\n\
                        Ka max.:\n\
                            Prolate limit.\n\
                        Dynamic range:\n\
                            Dynamic intensity cutoff with respect to the strongest predicted signal. If 100 is given, predicted transitions less than 1% the intensity of the strongest predicted transition\n\
                            are filtered.\n\
                        Max. obs.-calc.:\n\
                            (observed frequency - calculated frequency) limit from *.pi file. Transitions are removed from fit if greater than value after fit.\n\
                - Buttons:\n\
                        BROWSE\n\
                            Browse files with accepted file extension.\n\
                        PLOT\n\
                            Plot spectrum and remove all other series.\n\n\
        2.  Distortion Constants\n\
                - Constants deemed 'bad constants' by Piform are removed regardless of mode.\n\
                - Radio Buttons:\n\
                        Modes of quartic distortion constants attempted during initial fit.\n\
                                1.  Specific Constants:\n\
                                        Manually select specific quartic distortion constants using checkbuttons.\n\
                                2.  Constants from *.par:\n\
                                        Only use quartic distortion constants found in *.par file.\n\
                        Modes for fitting QDC\n\
                                1.  Floating:\n\
                                        Constants may vary to optimize fit.\n\
                                2.  Fixed:\n\
                                        Constants fixed to initial values. Constants must be found in *.par file to fix value.\n\
        3.  Run - Execute fit. After fit completes, assigned transitions, line centers, omitted transitions, and the the predicted spectrum are displayed in the plot.\n\n\
        4.  Outputs - Entry boxes are populated with calculated values after fit completes.\n\n\
        5.  Notes:\n\
                Info summarizing fit displayed in Notes after fit. Enter any notes you have about the sample or fitting process that may help in the future. Notes are saved when SAVE button is pressed.\n\
                Notes are loaded from *.pickle file when LOAD is pressed and file selected.\n\n\
    ===============================================================================================================================================================================\n\n\n\
    General Help\n\n\
        NAVIGATION BAR (Found below plots)\n\
                - PAN and ZOOM remain active once pressed until they are pressed again.\n\
                - To select a point from the chart, PAN and ZOOM must be deactivated.\n\
                - Buttons:\n\
                        HOME:\n\
                            Return plot to original zoom.\n\
                        BACK:\n\
                            Return to previous zoom/pan setting.\n\
                        FORWARD:\n\
                            Undo BACK\n\
                        PAN:\n\
                            Left click + mouse movement to drag plot.\n\
                            Right click + mouse movement to zoom along an axis.\n\
                        ZOOM:\n\
                            Zoom to a rectangular region. Select the region by left clicking and dragging.\n\
                        ADJUST MARGINS:\n\
                            Adjust plot aspect ratio. Useful for figures.\n\
                        SAVE IMAGE:\n\
                            Save non-interactive plot image.\n\n\
        Buttons to remove transitions from calculations:\n\
                OMIT:\n\
                    Select point from plot. If a point is successfully selected, frequency and intensity will populate the 'Selected Point' entry boxes. PAN and ZOOM must be deactivated to select points.\n\
                    No need to worry if more than one point is selected and occupy the entry boxes. Once entry boxes are filled, press OMIT. Transitions from that frequency will be omitted from calculations.\n\
                    Calculation must be rerun in order to remove omitted points. Transitions manually removed from calculations are designated as so on plot.\n\
                ALLOW:\n\
                    Selected point (selected point(s) occupy 'Selected Point' entry boxes) will be removed from the list of points to exclude from calculations.\n\
                RESET:\n\
                    All transitions manually excluded from calculations using OMIT will again be eligible for calculation.\n\n\
        Save and load page setups:\n\
                - Some pages have the following buttons near the top of the page allowing the user to save and reload page setups.\n\
                - Buttons:\n\
                        SAVE\n\
                            Save values from entry boxes, radiobuttons, check boxes, notes, omitted points in *.pickle file. Easily reproduce previous calculations by loading this file at a later time using the LOAD button. \n\
                            Calculation outputs are not saved in *.pickle files in order to reduce file size. To plot outputs, calculations must be performed again. Imported files must be in the same location as when the *.pickle\n\
                            file was saved\n\
                        LOAD\n\
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


class finalFitHelp(ttk.Frame):
    """ Generate help page for FinalFit. """
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Final Fit Help"
        h10 = 'Helvetica 10'
        f1 = ttk.Frame(frame)
        f1.grid(row=0, column=0)
        tb = tk.Text(f1, width=200, height=60,relief='sunken', font=h10, wrap=tk.WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')

