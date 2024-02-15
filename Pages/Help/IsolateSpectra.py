"""
Author: Channing West
Changelog: 8/14/2022
"""
from tkinter import Text, WORD
from tkinter.ttk import Frame
from Pages.PageFormat import PageFormat

e = "\n\
    Isolate Spectra Help\n\n\
        1.  Upload a target spectrum. A copy of this spectrum will be modified.\n\
        2.  Upload up to 3 peak pick spectra. These are used to identify peaks in the target spectrum. \n\
                - *.ft, *.cat, and *.prn file extensions supported. Filter file extension in the file explorer.\n\
        3.  Enter intensity threshold for an experimental spectrum or dynamic range for a simulation. \n\
                - PLOT buttons are useful for finding appropriate values.\n\
        4.  Enter baseline width, the width along the frequency axis targeted for each cut/revealed transition. \n\
                - Baseline width, not FWHM.\n\
                - Width is centered at peak transition intensity.\n\
        5.  Press CUT or REVEAL.\n\
                - CUT removes transitions in Peak Pick Files from Target Spectrum if transitions are above intensity cutoff or dynamic range cutoff.\n\
                - REVEAL removes everything except Peak Pick Files from Target Spectrum if transitions are above intensity cutoff or dynamic range cutoff.\n\
        6.  Display three plots.\n\
                - Top left - unmodified spectrum.\n\
                - top right - selected transitions are marked on the unmodified spectrum. If more than one Peak Pick File is uploaded, unique markers are used for each file.\n\
                - Bottom plot - modified spectrum.\n\
        7.  Press SAVE to name and save modified spectrum.\n\n\
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


class isolateHelp(Frame):
    """ Generate help page IsolateSpectra. """
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Isolate Spectra Help"
        h10 = 'Helvetica 10'
        f1 = Frame(frame)
        f1.grid(row=0, column=0)
        tb = Text(f1, width=200, height=60, relief='sunken', font=h10, wrap=WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')
