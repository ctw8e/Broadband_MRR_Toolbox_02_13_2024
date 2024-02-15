"""
Author: Channing West
Changelog: 8/14/2022
"""
from tkinter import Text, WORD
from tkinter.ttk import Frame
from Pages.PageFormat import PageFormat

e = "\n\
    Spectrum Explorer Help\n\n\
        1.  Main section\n\
                - Consists of 12 data series. Used to plot different spectra.\n\
                - Entry Boxes:\n\
                        Files:\n\
                            File paths are displayed after a spectrum has been chosen from the file explorer. When a matrix of spectra is uploaded, user has the option to view up to 12 columns of the matrix by loading columns in \n\
                            multiple data series (Multi-spectra, matrices can be generated in the Mixture Analysis page). For example, rows 1-5 of the GUI will hold 5 spectra if the user uploads a matrix consisting of 5 unique \n\
                            spectra. File path variables are updated automatically to reflect the particular column of the matrix. To view spectra past col[12], change the column number in the file path entry box to the desired column number.\n\
                        Scale:\n\
                            Apply a scale factor to the data series.\n\
                        Label:\n\
                            Label in legend. 'Plot legend show' check button must be checked to display legend.\n\
                - Combo Boxes:\n\
                        Marker:\n\
                            Choose a marker to mark data points on the line plot.\n\
                                period - small circle\n\
                                o - large circle\n\
                                x - x\n\
                                D - diamond\n\
                                ^ - triangle, point up\n\
                                v - triangle, point down\n\
                        Weight:\n\
                            Line thickness.\n\
                - Buttons:\n\
                        BROWSE:\n\
                            Open file explorer and browse files with accepted file extensions. File extension filter can be changed from file explorer.\n\n\
        2.  Manually Adjust Axes\n\
                - x and y-axes are independent. Manually set bounds and/or ticks for one axis and leave the other axis automatically controlled by leaving 'Auto' in entry boxes.\n\
                - Check Buttons:\n\
                        Manual Mode:\n\
                            Check box to manually adjust axes limits. If box is unchecked, axes are automatically set regardless of values in entry boxes.\n\
                        Minor Ticks:\n\
                            Check to include ticks between major, labeled ticks.\n\n\
                - Entry Boxes:\n\
                        X Ticks and Y Ticks:\n\
                            - Accepts 1 or 3 numbers, separated by commas.\n\
                            - If 1 number is provided, it is the number of ticks for axis range. Start and end values are selected automatically.\n\
                            - If 3 numbers are provided, first number is the lower bound tick value, second number is the upper bound tick value, and third item is the tick spacing.\n\n\
        3.  Plot Legend\n\
                - Check Buttons:\n\
                        Show:\n\
                            Check box to add a legend to plot.\n\
                - Entry Boxes:\n\
                        Font:\n\
                            Legend font size.\n\
                - Radio Buttons:\n\
                        Position:\n\
                            Legend location.\n\n\
        4.  Notes\n\
                - Add notes that are saved when SAVE is called.\n\n\
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


class specExplorerHelp(Frame):
    """ Generate help page for SpecExplorer. """
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Spectrum Explorer Help"
        h10 = 'Helvetica 10'
        f1 = Frame(frame)
        f1.grid(row=0, column=0)
        tb = Text(f1, width=200, height=60,relief='sunken', font=h10, wrap=WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')

