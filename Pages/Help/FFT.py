"""
Author: Channing West
Changelog: 8/14/2022
"""
from tkinter import Text, WORD
from tkinter.ttk import Frame
from Pages.PageFormat import PageFormat

e = "\n\
    FFT Help\n\n\
        1.  Upload Time Domain Files\n\
                - Select one or more *.txt files from file browser.\n\
                - The number of files chosen and total number of FIDs within those files are displayed if files follow naming convention.\n\
                - File names must follow naming convention to perform weighted average correctly.\n\
                - Naming convention:\n\
                        {time}_{sample}_{setup}_{# FIDs}k_{temp}C_{chirp dur}us_{pressure}psig_.{ext}\n\
                            - time: timestamp format: %H_%M_%S\n\
                            - sample: molecular name\n\
                            - setup: 2to8 or 6to18\n\
                            - # FIDS: thousands of FIDS\n\
                            - temperature: nozzle temperature\n\
                            - chirp duration: excitation chirp length\n\
                            - pressure: backing pressure\n\
                            - ext: file extension. *.txt\n\
                - Buttons:\n\
                        BROWSE\n\
                            Browse files with *.ft extension.\n\n\
        2.  Fast Fourier Transform Parameters\n\
                - Use one of the buttons from section 3 or manually enter values for each parameter.\n\n\
        3.  Quick Fill Options\n\
                - Press a button to import parameters into section 2.\n\n\
        4.  FFT Buttons\n\
                - When multiple files are selected from file explorer, user given the option to perform a weighted time-domain average of the files or process each file individually. This option occurs after\n\
                  MAGNITUDE FFT or FULL FFT button is pressed If weighted average is chosen, *.txt file of the weighted average is saved. User can name the file before it is saved.\n\
                - FID, filtered FID, and FFT are plotted after FFT completes, unless multiple files are processed individually.\n\
                - Buttons:\n\
                        MAGNITUDE FFT\n\
                            Sum of squares of real and imaginary parts of FFT. Result is 2 column array.\n\
                        FULL FFT\n\
                            Real and imaginary spectrum. Result is 3 column array.\n\n\
    ===============================================================================================================================================================================\n\
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
        Buttons at the bottom of all pages:\n\
                BACK TO NAVIGATOR\n\
                    Go to navigator page.\n\
                SETTINGS\n\
                    Redirect to page where program settings can be changed. Changes to settings are saved on program exit.\n\
                HELP\n\
                    Redirect to page specific instructions for use.\n\
                EXIT APPLICATION\n\
                    Close program."


class fftHelp(Frame):
    """ Generate help page for FFT. """
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - FFT Help"
        h10 = 'Helvetica 10'
        f1 = Frame(frame)
        f1.grid(row=0, column=0)
        tb = Text(f1, width=200, height=60,relief='sunken', font=h10, wrap=WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')

