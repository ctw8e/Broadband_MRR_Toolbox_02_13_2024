"""
Author: Channing West
Changelog: 8/14/2022
"""
from tkinter import Text, WORD
from tkinter.ttk import Frame
from Pages.PageFormat import PageFormat

e = "\n\
    Enantiomeric Excess Help\n\n\
        1.  Upload files\n\
                - Upload racemic spectrum and enantioenriched spectrum.\n\
                - (Optional) Upload *.cat file for each diastereomer complex. Provide *.cat files for better diastereomer distinction, which results in better filtering. Without species1_cat and species2_cat, more importance is placed\n\
                on peak pick threshold because species1 and species2 are distinguished by peaks from spec2_pp that are not in spec1_pp. For an ee calculation, can be problematic if sample is not of high enantiopurity.\n\
                - Buttons:\n\
                        BROWSE\n\
                            Browse files with accepted file extension.\n\
                        PLOT\n\
                            Plot spec on plot and remove all other series.\n\n\
        2.  Peak pick\n\
                - Enter cutoff threshold. Use PLOT button and NAV BAR zoom to find threshold.\n\
                - Perform peak pick on racemic and enantioenriched spectra. Threshold does not have to be the same between the two spectra.\n\
                - Identified peaks are marked on the spectrum and displayed in the top plot.\n\
                - For a peak to be used in the ee calculation, frequency of the peak must be in the racemic peak pick.\n\
                - If *.cat files are not provided, threshold is very important. Set the threshold of the racemic spectrum low, so the spectra of both diastereomers are captured. Set the threshold of the enantioenriched so that the spectrum\n\
                  of one enantiomer is captured and the spectrum of the other enantiomer is missed.\n\
                - Buttons:\n\
                        RACEMIC\n\
                            Locate peaks in racemic spectrum, save temporary file, mark peaks on spec.\n\
                        ENRICHED\n\
                            Locate peaks in enriched spectrum, save temporary file, mark peaks on spec.\n\n\
        3.  Filter transitions\n\
                - Filter only works if diastereomer *.cat files are provided.\n\
                - Do not worry about values in filter entry boxes if *.cat files are not provided. Entry box values will not be used in calculations.\n\
                - Frequency match threshold refers to the maximum difference between the predicted line position and the experimental line position. If 0.020 MHz is given, a predicted transition does not pass unless a peak in the\n\
                  racemic peak pick is within 0.020 MHz.\n\
                - Dynamic range refers to the minimum accepted intensity with respect to the strongest signal. If 100, a predicted transition does not pass unless it is at least 1/100 the intensity of the strongest predicted transition.\n\
                - Enter desired filter conditions and press 'Calculate Transition Ratios' button. The *.cat files are filtered and find scale factors for each transition between the two spectra.\n\
                - A histogram of scale factors for each diastereomer is generated below.\n\
                - Buttons:\n\
                        CALCULATE TRANSITION RATIOS\n\
                            Calculate [spec1 intensity / spec2 intensity] using filered peak picks. Histograms displayed in plots below.\n\n\
        4.  Filter by Intensity Ratio\n\
                - Filter transitions by scale factors.\n\
                - 3 sigma filter Can be used multiple times. Histogram updated after each press.\n\
                - If the 3 sigma filter achieves a suitable data set, make sure the values in the minimum and maximum entry boxes do not further filter the data when ee calculation is executed.\n\
                - Buttons:\n\
                        3SIGMA FILTER\n\
                            Filter transitions that produce R value more than 3 s.d. away from mean. Update plot. Set appropriate filter boundaries after running 3-sigma filter.\n\n\
        5.  Histogram Parameters\n\
                - Entry Boxes\n\
                        top N:\n\
                            Number of transitions from each diastereomer used to calculate EE. If set to 25, 25 transitions of each diastereomer used, resulting in 625 total ee calculations.\n\
                        tag ee:\n\
                            ee of the chiral tag. Between 0 and 1. If tag ee is unknown, leave at 1. CalculatedEE = analyteEE * tagEE\n\
                        Number of Bins:\n\
                            Number of histogram bins.\n\
                        Color:\n\
                            Bin color.\n\
                - Check Buttons:\n\
                        Border:\n\
                            Apply black border around each bin.\n\
                        Stats. Label:\n\
                            Display label with statistical information about the histogram. Contents of the label include all the values from the Results section. The check buttons beside each result allow you to display certain stats and omit others.\n\
                        Plot Mean:\n\
                            Plot a dashed line through the mean of the histogram.\n\
                - Buttons:\n\
                        CALCULATE EE\n\
                            Run self.calc_ee(). Calculate ee using 'diastereomer_1_analysis.npy' and 'diastereomer_2_analysis.npy'\n\n\
        5.5 Refining Calculation (with 'Selected Point' section)\n\
                - After ee is calculated, the enantioenriched spectrum is displayed in the plot at the top of the page with transitions used in the ee calculation marked. Diastereomers marked with different colors.\n\
                - Zoom on transitions and omit if you find a problem.\n\
                - To omit a transition, left-click the point on the plot and press 'Omit From EE Calc.' button. The point is selected if the frequency populates the entry field beside the 'x' label. It is okay if neighboring frequencies\n\
                  populate this field along with the desired frequency. See NAVIGATION BAR below if you are having trouble selecting points on the plot.\n\
                - The list of omitted transitions can be reset using the 'Reset Omits' button.\n\
                - Buttons:\n\
                        OMIT FROM EE CALC\n\
                            Omit a transition from ee calculation. After point(s) have been omitted, rerun CALCULATE EE.\n\
                        RESET OMITS\n\
                            All transitions excluded from calculations using OMIT will again be eligible for calculation.\n\n\
        6.  Results:\n\
                - Display statistics on ee histogram, including: mean, standard deviation, standard error, max, min. Label displaying stats can be added to plot.\n\
                - Provide 'base_name' shared by all summary files when file dialog opens.\n\
                - Buttons:\n\
                        SAVE OUTPUTS\n\
                            '{base_name}_summary.txt'\n\
                                    Contains information from entry boxes.\n\
                            '{base_name}_dominant_diastereomer.csv'\n\
                                    Diastereomer 1 characterization\n\
                                    col[0] -> transition frequency\n\
                                    col[1] -> intensity in racemic spectrum\n\
                                    col[2] -> intensity in enriched spectrum\n\
                                    col[3] -> col[2]/col[1]\n\
                            '{base_name}_minor_diastereomer.csv'\n\
                                    Diastereomer 2 characterization\n\
                                    col[0] -> transition frequency\n\
                                    col[1] -> intensity in racemic spectrum\n\
                                    col[2] -> intensity in enriched spectrum\n\
                                    col[3] -> col[2]/col[1]\n\
                            '{base_name}_ee_calculations.csv'\n\
                                    Individual ee values.\n\n\
        7.  Adjust Axes\n\
                - Update aspects of ee histogram without recalculating, including: bin color, border, stats label, plot mean.\n\
                - Buttons:\n\
                        UPDATE HISTOGRAM\n\
                            Handles histogram, including mean line, color, labels, etc.\n\n\
    ===============================================================================================================================================================================\n\n\n\
    General Help\n\n\
        NAVIGATION BAR (Found below plots):\n\
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


class eeHelp(Frame):
    """ Generate help page for EnantiomericExcess. """
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Enantiomeric Excess Help"
        h10 = 'Helvetica 10'
        f1 = Frame(frame)
        f1.grid(row=0, column=0)
        tb = Text(f1, width=200, height=60,relief='sunken', font=h10, wrap=WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')


