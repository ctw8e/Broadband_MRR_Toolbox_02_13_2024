"""
Author: Channing West
Changelog: 8/14/2022
"""
from tkinter import Text, WORD
from tkinter.ttk import Frame
from Pages.PageFormat import PageFormat

e = "\n\
    Mixture Analysis Help\n\n\
        1.  Upload Spectra: Build Matrix or Use Existing\n\
                - Upload previously built matrix of spectra or build new matrix by selecting multiple spectra from file explorer. Select multiple spectra by holding CTRL and clicking files.\n\
                - *** To add spectra to the matrix in a particular order, file names MUST BE NUMBERED in ascending order at the beginning of the file names. ***\n\
                - After building a new matrix, the file name entry box automatically updates to the file name of the matrix.\n\
                - Individual spectra typically differ in the nozzle temperature at which they are taken. \n\
                - Buttons:\n\
                        BROWSE\n\
                            Open file explorer where one or more files can be selected. Select > 1 file to build matrix of spectra.\n\
                        BUILD MATRIX\n\
                            Spectra must be over the same frequency region. Build spectra matrix from shared frequency region, keeping a single frequency column. By saving spectra with a single frequency column, memory is saved.\n\
                            After matrix is saved, matrix can be uploaded rather than the set of spectra.\n\n\
        2a. Characterize Transitions: Specific Component\n\
                - Proof of principle.\n\
                - This section is used to verify that transitions of a single molecular species exhibit similar intensity behavior. Requires accurate spectrum fit.\n\
                - Using the spectra matrix and known transition positions, transition intensities across the set of spectra are recorded for all transitions. The mean value along the x-axis, the area under curve, and the width of the\n\
                  curve are used to characterize the behavior of the transition. Transitions from the same molecular species are expected to exhibit similar intensity profiles, so the characterization parameters should be similar.\n\
                - Upload *.cat file of molecular species.\n\
                - Outliers (3 sigma) removed.\n\
                - Entry Boxes:\n\
                        Dynamic Range:\n\
                            Limit the predicted transitions used in the calculation to a relative intensity range.\n\
                        Top N:\n\
                            Limit the number of results shown to only include the top N strongest predicted transitions.Top N does not limit the transitions that are characterized, only the transitions that are displayed in the plot.\n\
                - Buttons:\n\
                        BROWSE\n\
                            Select *.cat file from file explorer.\n\
                        EXECUTE\n\
                            Characterize transitions for a single molecular species using the provided rotational spectra.\n\
                        CHANGE PROJECTION\n\
                            Update data projection plotted.\n\
                        SAVE RESULTS\n\
                            Save *.csv files with results of EXECUTE.\n\
                - Option Menu:\n\
                        DISPLAYED PROJECTION\n\
                            Select a projection of the results to display in the plot.\n\n\
        2b. Characterize Transitions: All Components\n\
                - Use for mixtures with unknown components.\n\
                - Characterize intensity profile of all transitions over the peak pick threshold.\n\
                - Peak pick is performed on all individual spectra in the matrix, if a signal occurs at a particular frequency above the threshold in any spectrum in the matrix, the frequency is added to list for characterization.\n\
                  Using transition intensities from a set of spectra transition intensity is plotted as a function of an external variable (time/FIDs/temperature). The mean value along the x-axis, the area under curve, and the width\n\
                  of the curve are used to characterize the behavior of the transition.\n\
                - Entry Boxes:\n\
                        Peak pick threshold:\n\
                            If a signal occurs over this threshold in any spectrum in the matrix, the frequency is added to the list for intensity profile characterization over the whole set of spectra.\n\
                - Buttons:\n\
                        EXECUTE\n\
                            Characterize transition signal levels for all transitions above threshold in spectra matrix.\n\
                        CHANGE PROJECTION\n\
                            Update data projection plotted. Changing projection does not require recalculation.\n\
                        SAVE RESULTS\n\
                            Save *.csv files with results from EXECUTE.\n\
                - Option Menu:\n\
                        DISPLAYED PROJECTION\n\
                            Select a projection of the results to display in the plot. \n\n\
        3.  Find Clusters\n\
                - Scan the data set for outliers.\n\
                - Bayesian Information Criterion used to determine the number of clusters.\n\
                - Data set is fit to a range of cluster numbers (2-25 clusters). After this is complete, a graph of the BIC vs. # of clusters is displayed. User is asked to input the number of clusters to fit the data. Use the graph\n\
                  to determine an appropriate number of clusters. You want to minimize the BIC without overfitting the data. Typically, there is a large drop in the slope of the graph at some cluster number. This number is a good starting point.\n\
                - Radio Buttons\n\
                        Two modes: \n\
                                DBSCAN - Density Based Spatial Clustering of Applications with Noise\n\
                                    Data points are deemed outliers if no other data points are within a user defined range of the point. \n\
                                GMM - Gaussian Mixture Model \n\
                                    Data points are deemed outliers if they fall outside the user defined percentile of the Gaussian curve. \n\
                - Buttons: \n\
                        EXECUTE\n\
                            Cluster data using a Gaussian Mixture Model. The final clustering of the data is performed using a Gaussian Mixture Model. DBSCAN is only used for outlier detection.\n\
                        SAVE RESULTS\n\
                            Save results from EXECUTE.\n\n\
        4.  Split Spectrum\n\
                - Split raw set of spectra into a set of spectra based on GMM clustering of signal profile characterization.\n\
                - After transitions are assigned to groups based on GMM clustering, transitions belonging to a group are placed in an array with other transitions of the same group. This process is repeated for all GMM groupings.\n\
                  If 10 clusters are found, 10 arrays are created. For visualization purposes, each transition in the GMM cluster based spectra is represented by the transition from the raw spectrum with the strongest signal.\n\
                - Split spectra are color coded and plotted.\n\
                - Radio Buttons:\n\
                        Two modes of spectrum splitting:\n\
                                SOFT CLUSTER\n\
                                    Assign probability of each data point belonging to each cluster. Each transition can be assigned to multiple clusters if the transition has high enough probability.\n\
                                HARD CLUSTER\n\
                                    Assign each data point to the cluster it has the highest probability of belonging.\n\
                - Buttons:\n\
                        EXECUTE\n\
                            Split raw set of spectra into a set of spectra based on GMM clustering of signal profile characterization.\n\
                        SAVE SPECTRA\n\
                            Save file temporarily saved from EXECUTE.\n\n\
        5.  Plot Parameters\n\
                - Buttons:\n\
                        UPDATE PLOT\n\
                            Update plot and axes titles with information from entry boxes.\n\n\
        6.  Notes\n\
                - Enter notes you have about the sample or clustering process that could help in the future. Notes are saved when SAVE button is pressed. Notes are loaded from *.pickle file when LOAD is pressed and file selected.\n\n\
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


class maHelp(Frame):
    """ Generate help page for MixtureAnalysis. """
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        frame = self.page.frame
        self.page_title = "Broadband MRR Toolbox - Mixture Analysis Help"
        h10 = 'Helvetica 10'
        f1 = Frame(frame)
        f1.grid(row=0, column=0)
        tb = Text(f1, width=200, height=60,relief='sunken', font=h10, wrap=WORD)
        tb.insert('1.0', e)
        tb.grid(row=1, column=0)
        tb.config(state='disabled')


