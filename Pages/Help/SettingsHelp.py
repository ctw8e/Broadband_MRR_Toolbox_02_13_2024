"""
Author: Channing West
Changelog: 8/14/2022
"""
from tkinter import Text, WORD
from tkinter.ttk import Frame
from Pages.PageFormat import PageFormat

e = "\n\
    Settings Help\n\n\
        Settings are updated upon closing the program. Changes do not occur until reopening the program.\n\n\
        1. Width - The width of the program frame in pixels.\n\
        2. Height - The height of the program frame in pixels.\n\
        3. Pickett Directory - Location of SPCAT, SPFIT, and PIFORM executables.\n\
        4. Plot Selection Sensitivity - Data point selection sensitivity within Matplotlib plots. When a click is registered in a plot, all data points within this many pixels are returned.\n\n\
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


class SettingsHelp(Frame):
    """ Generate help page Settings. """
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Settings Help"
        h10 = 'Helvetica 10'
        f1 = Frame(frame)
        f1.grid(row=0, column=0)
        tb = Text(f1, width=200, height=60, relief='sunken', font=h10, wrap=WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')
