"""
Author: Channing West
Changelog: 4/24/2020

"""

import tkinter as tk
import tkinter.ttk as ttk
from Pages.PageFormat import PageFormat
import Pages.PageFormat as page_funcs
from Spectrum import Spectrum
from TkAgg_Plotting import PlotManager, SpecPlot
import os
from tkinter import messagebox
import testing

h10b = 'Helvetica 10 bold'
pad2_e = {'padx': 2, 'pady': 2, 'sticky': 'e'}
pad2_w = {'padx': 2, 'pady': 2, 'sticky': 'w'}
pad2_ew = {'padx': 2, 'pady': 2, 'sticky': 'ew'}
pad2 = {'padx': 2, 'pady': 2}
right_h10b = {'justify': tk.RIGHT, 'font': 'Helvetica 10 bold'}
center_h10b = {'justify': tk.CENTER, 'font': 'Helvetica 10 bold'}
pad5_ns = {'padx': 5, 'pady': 5, 'sticky': 'ns'}
pad5_ew = {'padx': 5, 'pady': 5, 'sticky': 'ew'}


class SpecExplorer(ttk.Frame):
    """
    Generate GUI for viewing broadband molecular rotational spectra.

    BUTTONS in caps

    NAVIGATION BAR
        HOME: Return plot to original zoom.
        BACK: Return to previous zoom/pan setting.
        FORWARD: Undo BACK
        PAN: click and drag plot. Scroll to zoom along one axis.
        ZOOM: select a region of the plot to zoom into focus.
        ADJUST MARGINS: Adjust the dimensions of the plot. Useful for figures.
        SAVE IMAGE: Save an image of the plot. Not interactive.
    SAVE
        Saves values from all entry boxes, combo boxes, radiobuttons, check boxes, notes, omitted
        points. While this allows the user to easily reproduce previously performed calculations,
        it does not save outputs from these calculations. Therefore, to plot any outputs,
        calculations must to performed again.
    LOAD
        Load values for all entry boxes, combo boxes, radiobuttons, check boxes, notes, omitted
        points from a previously save session. While this allows the user to easily reproduce
        previously performed calculations, it does not save outputs from these calculations.
        Therefore, to plot any outputs, calculations must to performed again.
    DEFAULTS
        Restores all entry boxes, combo boxes, radiobuttons, check boxes, notes, omitted points to
        default values.
    PLOT
        Update plot.

    Sections
        1.  Main section
            Consists of 12 data series. Used to plot different spectra.

            Files:
                This is where the file path is displayed after a spectrum has been chosen from the
                file explorer. You could also manually enter a file path.
            BROWSE:
                Browse files with accepted file extensions.
            Show:
                Check box to display the spectrum on the plot.
            Invert:
                Check box to invert the spectrum.
            Color:
                Choose from a number of different colors.
            Marker:
                Choosing a marker results in marking where the data points are along the line plot.
            Weight:
                Line weight of the line plot.
            Scale:
                Apply a scale factor to the spectrum.
            Label:
                Label in legend
        2.  Axis Labels
            Plot Title
            X-axis Title
            Y-axis Title
        3.  Manually Adjust Axes
            x and y-axis are independent. If you wish to manually set the bounds and/or ticks along
            one axis, the other axis can be controlled automatically by leaving 'Auto' in entry
            boxes.

            Manual Mode:
                If box is checked, you can manually adjust axes limits. If box is unchecked, axes
                are automatically set.
            Freq. Min.:
                lower bound
            Freq. Max.:
                upper bound
            Intensity Min.:
                lower bound
            Intensity Max.:
                upper bound
            X Ticks and Y Ticks:
                Accepts 1 or 3 entries. If 1 item, sets number of ticks for axis range and
                automatically selects start and end values. If 3 items, first is the lower bound
                tick value, second item is the upper bound tick value, and third item is the number
                of total ticks.
            Minor Ticks:
                Include ticks between major, labeled ticks.
        4.  Plot Legend
            Show:
                Check box to add legend to plot.
            Font:
                font size.
            Position:
                Where the legend is located.
        5.  Notes
            Add notes that are saved when SAVE is called.
    """
    default = {
        'sel_freq': 'None Selected',
        'sel_int': 'None Selected',

        'zoom_mode': 0,

        'plot_title': 'Spectrum',
        'xlabel': 'Frequency / MHz',
        'ylabel': 'Intensity / mV',

        'freq_min': 'Auto',
        'freq_max': 'Auto',
        'int_min': 'Auto',
        'int_max': 'Auto',
        'x_inc': 'Auto',
        'y_inc': 'Auto',
        'minor_ticks': 0,
        'legend_show': 0,
        'legend_font': 12,
        'legend_loc': 0,
        'manual_mode': 0,
        'show_legend': 0,

        'fpath0': 'None', 'fpath1': 'None', 'fpath2': 'None', 'fpath3': 'None',
        'fpath4': 'None', 'fpath5': 'None', 'fpath6': 'None', 'fpath7': 'None',
        'fpath8': 'None', 'fpath9': 'None', 'fpath10': 'None',
        'fpath11': 'None',

        'copy0': 'None', 'copy1': 'None', 'copy2': 'None', 'copy3': 'None',
        'copy4': 'None', 'copy5': 'None', 'copy6': 'None', 'copy7': 'None',
        'copy8': 'None', 'copy9': 'None', 'copy10': 'None',
        'copy11': 'None',

        'show0': 1, 'show1': 0, 'show2': 0, 'show3': 0, 'show4': 0, 'show5': 0,
        'show6': 0, 'show7': 0, 'show8': 0, 'show9': 0, 'show10': 0,
        'show11': 0,

        'invert0': 0, 'invert1': 0, 'invert2': 0, 'invert3': 0, 'invert4': 0,
        'invert5': 0, 'invert6': 0, 'invert7': 0, 'invert8': 0, 'invert9': 0,
        'invert10': 0, 'invert11': 0,

        'scale0': 1, 'scale1': 1, 'scale2': 1, 'scale3': 1, 'scale4': 1,
        'scale5': 1, 'scale6': 1, 'scale7': 1, 'scale8': 1, 'scale9': 1,
        'scale10': 1, 'scale11': 1,

        'color0': 'black', 'color1': 'red', 'color2': 'blue', 'color3': 'green',
        'color4': 'cyan', 'color5': 'purple', 'color6': 'lime',
        'color7': 'gold', 'color8': 'teal', 'color9': 'salmon',
        'color10': 'darkblue', 'color11': 'sienna',

        'marker0': 'None', 'marker1': 'None', 'marker2': 'None',
        'marker3': 'None', 'marker4': 'None', 'marker5': 'None',
        'marker6': 'None', 'marker7': 'None', 'marker8': 'None',
        'marker9': 'None', 'marker10': 'None', 'marker11': 'None',

        'weight0': '1.5', 'weight1': '1.5', 'weight2': '1.5', 'weight3': '1.5',
        'weight4': '1.5', 'weight5': '1.5', 'weight6': '1.5', 'weight7': '1.5',
        'weight8': '1.5', 'weight9': '1.5', 'weight10': '1.5', 'weight11': '1.5',

        'label0': '1', 'label1': '2', 'label2': '3', 'label3': '4',
        'label4': '5', 'label5': '6', 'label6': '7', 'label7': '8',
        'label8': '9', 'label9': '10', 'label10': '11', 'label11': '12'}

    def __init__(self, master, controller):
        # tracemalloc.start()
        c = tk.CENTER
        r = tk.RIGHT
        ttk.Frame.__init__(self, master)
        self.page = PageFormat(self, controller)
        self.frame = self.page.frame
        self.controller = controller

        self.page_title = "Broadband MRR Toolbox - Spectrum Explorer"

        self.notes = tk.StringVar()

        self.sel_freq = tk.StringVar()
        self.sel_int = tk.StringVar()
        self.sel_freq.set(SpecExplorer.default['sel_freq'])
        self.sel_int.set(SpecExplorer.default['sel_int'])
        self.dict = {}

        self.plot = PlotManager(
            frame=self.frame, figsize=(16, 9), dpi=100, subplotshape=111,
            zoom_mode=SpecExplorer.default['zoom_mode'],
            plot_title=SpecExplorer.default['plot_title'], xlabel=SpecExplorer.default['xlabel'],
            ylabel=SpecExplorer.default['ylabel'], x_min=SpecExplorer.default['freq_min'],
            x_max=SpecExplorer.default['freq_max'], y_min=SpecExplorer.default['int_min'],
            y_max=SpecExplorer.default['int_max'], x_inc=SpecExplorer.default['x_inc'],
            y_inc=SpecExplorer.default['y_inc'], minor_ticks=SpecExplorer.default['minor_ticks'],
            legend_show=SpecExplorer.default['legend_show'],
            legend_font=SpecExplorer.default['legend_font'],
            legend_loc=SpecExplorer.default['legend_loc'], left=0.05, right=0.98, top=0.96,
            bottom=0.06, row=0, column=0, columnspan=2, toolbar=True, toolrow=1, toolcol=0,
            toolpadx=5, toolpady=2, toolsticky='w')

        self.plot.canvas.mpl_connect(
            'pick_event', lambda event: page_funcs.mpl_click(event, self.sel_freq, self.sel_int))

        self.s0 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath0'],
            show=SpecExplorer.default['show0'],
            invert=SpecExplorer.default['invert0'],
            scale=SpecExplorer.default['scale0'],
            color=SpecExplorer.default['color0'],
            marker=SpecExplorer.default['marker0'],
            weight=SpecExplorer.default['weight0'],
            legend=SpecExplorer.default['label0'])

        self.s1 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath1'],
            show=SpecExplorer.default['show1'],
            invert=SpecExplorer.default['invert1'],
            scale=SpecExplorer.default['scale1'],
            color=SpecExplorer.default['color1'],
            marker=SpecExplorer.default['marker1'],
            weight=SpecExplorer.default['weight1'],
            legend=SpecExplorer.default['label1'])

        self.s2 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath2'],
            show=SpecExplorer.default['show2'],
            invert=SpecExplorer.default['invert2'],
            scale=SpecExplorer.default['scale2'],
            color=SpecExplorer.default['color2'],
            marker=SpecExplorer.default['marker2'],
            weight=SpecExplorer.default['weight2'],
            legend=SpecExplorer.default['label2'])

        self.s3 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath3'],
            show=SpecExplorer.default['show3'],
            invert=SpecExplorer.default['invert3'],
            scale=SpecExplorer.default['scale3'],
            color=SpecExplorer.default['color3'],
            marker=SpecExplorer.default['marker3'],
            weight=SpecExplorer.default['weight3'],
            legend=SpecExplorer.default['label3'])

        self.s4 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath4'],
            show=SpecExplorer.default['show4'],
            invert=SpecExplorer.default['invert4'],
            scale=SpecExplorer.default['scale4'],
            color=SpecExplorer.default['color4'],
            marker=SpecExplorer.default['marker4'],
            weight=SpecExplorer.default['weight4'],
            legend=SpecExplorer.default['label4'])

        self.s5 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath5'],
            show=SpecExplorer.default['show5'],
            invert=SpecExplorer.default['invert5'],
            scale=SpecExplorer.default['scale5'],
            color=SpecExplorer.default['color5'],
            marker=SpecExplorer.default['marker5'],
            weight=SpecExplorer.default['weight5'],
            legend=SpecExplorer.default['label5'])

        self.s6 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath6'],
            show=SpecExplorer.default['show6'],
            invert=SpecExplorer.default['invert6'],
            scale=SpecExplorer.default['scale6'],
            color=SpecExplorer.default['color6'],
            marker=SpecExplorer.default['marker6'],
            weight=SpecExplorer.default['weight6'],
            legend=SpecExplorer.default['label6'])

        self.s7 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath7'],
            show=SpecExplorer.default['show7'],
            invert=SpecExplorer.default['invert7'],
            scale=SpecExplorer.default['scale7'],
            color=SpecExplorer.default['color7'],
            marker=SpecExplorer.default['marker7'],
            weight=SpecExplorer.default['weight7'],
            legend=SpecExplorer.default['label7'])

        self.s8 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath8'],
            show=SpecExplorer.default['show8'],
            invert=SpecExplorer.default['invert8'],
            scale=SpecExplorer.default['scale8'],
            color=SpecExplorer.default['color8'],
            marker=SpecExplorer.default['marker8'],
            weight=SpecExplorer.default['weight8'],
            legend=SpecExplorer.default['label8'])

        self.s9 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath9'],
            show=SpecExplorer.default['show9'],
            invert=SpecExplorer.default['invert9'],
            scale=SpecExplorer.default['scale9'],
            color=SpecExplorer.default['color9'],
            marker=SpecExplorer.default['marker9'],
            weight=SpecExplorer.default['weight9'],
            legend=SpecExplorer.default['label9'])

        self.s10 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath10'],
            show=SpecExplorer.default['show10'],
            invert=SpecExplorer.default['invert10'],
            scale=SpecExplorer.default['scale10'],
            color=SpecExplorer.default['color10'],
            marker=SpecExplorer.default['marker10'],
            weight=SpecExplorer.default['weight10'],
            legend=SpecExplorer.default['label10'])

        self.s11 = SpecPlot(
            self.plot.ax, fpath=SpecExplorer.default['fpath11'],
            show=SpecExplorer.default['show11'],
            invert=SpecExplorer.default['invert11'],
            scale=SpecExplorer.default['scale11'],
            color=SpecExplorer.default['color11'],
            marker=SpecExplorer.default['marker11'],
            weight=SpecExplorer.default['weight11'],
            legend=SpecExplorer.default['label11'])

        h = 'horizontal'
        ttk.Separator(self.frame, orient=h).grid(row=3, column=0, columnspan=2, **pad5_ew)
        ttk.Separator(self.frame, orient=h).grid(row=5, column=0, columnspan=2, **pad5_ew)
        ttk.Separator(self.frame, orient=h).grid(row=7, column=0, columnspan=2, **pad5_ew)
        frame_0 = ttk.Frame(self.frame)
        frame_0.grid(row=4, column=0, columnspan=2)
        ttk.Separator(frame_0, orient='vertical').grid(row=0, column=0, **pad5_ns)
        ttk.Separator(frame_0, orient='vertical').grid(row=0, column=2, **pad5_ns)
        frame_1 = ttk.Frame(frame_0)
        frame_1.grid(row=0, column=1, columnspan=1)
        sel_frame = ttk.Frame(self.frame)
        sel_frame.grid(row=2, column=0, sticky='w')
        sel_freq_L = ttk.Label(sel_frame, text='x', justify=r)
        sel_int_L = ttk.Label(sel_frame, text='y', justify=r)
        sel_freq_E = ttk.Entry(sel_frame, textvariable=self.sel_freq, justify=c)
        sel_int_E = ttk.Entry(sel_frame, textvariable=self.sel_int, justify=c)
        sel_freq_L.grid(row=0, column=0, **pad2_w)
        sel_int_L.grid(row=1, column=0, **pad2_w)
        sel_freq_E.grid(row=0, column=1, **pad2_w)
        sel_int_E.grid(row=1, column=1, **pad2_w)

        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=2, column=1, sticky='e')
        update = ttk.Button(buttons_frame, text='Plot', style='h10b.TButton',
                            command=self.update_plot, width=20)
        clear = ttk.Button(
            buttons_frame, text='Defaults', style='h10b.TButton', width=20,
            command=lambda: page_funcs.clear_page(
                SpecExplorer.default, self.attribute_dict, self.plot,
                textbox_dict=self.text_box_dict))
        save = ttk.Button(
            buttons_frame, text='Save', style='h10b.TButton', width=20,
            command=lambda: page_funcs.save_page(self.attribute_dict, self.text_box_dict))
        update.grid(row=0, column=0, **pad2_e)
        clear.grid(row=0, column=1, **pad2_e)
        save.grid(row=1, column=0, **pad2_e)

        paths_L = ttk.Label(frame_1, text='Files', justify=c, style='h10b.TLabel')
        show_L = ttk.Label(frame_1, text='Show', justify=c, style='h10b.TLabel', width=7)
        invert_L = ttk.Label(frame_1, text='Invert', justify=c, style='h10b.TLabel', width=7)
        color_L = ttk.Label(frame_1, text='Color', justify=c, style='h10b.TLabel')
        scale_L = ttk.Label(frame_1, text='Scale', justify=c, style='h10b.TLabel')
        marker_L = ttk.Label(frame_1, text='Marker', justify=c, style='h10b.TLabel')
        line_weight_L = ttk.Label(frame_1, text='Weight', justify=c, style='h10b.TLabel')
        legend_names_L = ttk.Label(frame_1, text='Label', justify=c, style='h10b.TLabel')
        paths_L.grid(row=0, column=1, **pad2)
        show_L.grid(row=0, column=3, **pad2)
        invert_L.grid(row=0, column=4, **pad2)
        color_L.grid(row=0, column=5, **pad2)
        marker_L.grid(row=0, column=6, **pad2)
        line_weight_L.grid(row=0, column=7, **pad2)
        scale_L.grid(row=0, column=8, **pad2)
        legend_names_L.grid(row=0, column=9, **pad2)

        s0_L = ttk.Label(frame_1, text='1 :', **right_h10b)
        s1_L = ttk.Label(frame_1, text='2 :', **right_h10b)
        s2_L = ttk.Label(frame_1, text='3 :', **right_h10b)
        s3_L = ttk.Label(frame_1, text='4 :', **right_h10b)
        s4_L = ttk.Label(frame_1, text='5 :', **right_h10b)
        s5_L = ttk.Label(frame_1, text='6 :', **right_h10b)
        s6_L = ttk.Label(frame_1, text='7 :', **right_h10b)
        s7_L = ttk.Label(frame_1, text='8 :', **right_h10b)
        s8_L = ttk.Label(frame_1, text='9 :', **right_h10b)
        s9_L = ttk.Label(frame_1, text='10 :', **right_h10b)
        s10_L = ttk.Label(frame_1, text='11 :', **right_h10b)
        s11_L = ttk.Label(frame_1, text='12 :', **right_h10b)
        s0_L.grid(row=1, column=0, **pad2)
        s1_L.grid(row=2, column=0, **pad2)
        s2_L.grid(row=3, column=0, **pad2)
        s3_L.grid(row=4, column=0, **pad2)
        s4_L.grid(row=5, column=0, **pad2)
        s5_L.grid(row=6, column=0, **pad2)
        s6_L.grid(row=7, column=0, **pad2)
        s7_L.grid(row=8, column=0, **pad2)
        s8_L.grid(row=9, column=0, **pad2)
        s9_L.grid(row=10, column=0, **pad2)
        s10_L.grid(row=11, column=0, **pad2)
        s11_L.grid(row=12, column=0, **pad2)

        s0_E = ttk.Entry(frame_1, textvariable=self.s0.fpath, justify=c, width=115)
        s1_E = ttk.Entry(frame_1, textvariable=self.s1.fpath, justify=c, width=115)
        s2_E = ttk.Entry(frame_1, textvariable=self.s2.fpath, justify=c, width=115)
        s3_E = ttk.Entry(frame_1, textvariable=self.s3.fpath, justify=c, width=115)
        s4_E = ttk.Entry(frame_1, textvariable=self.s4.fpath, justify=c, width=115)
        s5_E = ttk.Entry(frame_1, textvariable=self.s5.fpath, justify=c, width=115)
        s6_E = ttk.Entry(frame_1, textvariable=self.s6.fpath, justify=c, width=115)
        s7_E = ttk.Entry(frame_1, textvariable=self.s7.fpath, justify=c, width=115)
        s8_E = ttk.Entry(frame_1, textvariable=self.s8.fpath, justify=c, width=115)
        s9_E = ttk.Entry(frame_1, textvariable=self.s9.fpath, justify=c, width=115)
        s10_E = ttk.Entry(frame_1, textvariable=self.s10.fpath, justify=c, width=115)
        s11_E = ttk.Entry(frame_1, textvariable=self.s11.fpath, justify=c, width=115)
        s0_E.grid(row=1, column=1, **pad2)
        s1_E.grid(row=2, column=1, **pad2)
        s2_E.grid(row=3, column=1, **pad2)
        s3_E.grid(row=4, column=1, **pad2)
        s4_E.grid(row=5, column=1, **pad2)
        s5_E.grid(row=6, column=1, **pad2)
        s6_E.grid(row=7, column=1, **pad2)
        s7_E.grid(row=8, column=1, **pad2)
        s8_E.grid(row=9, column=1, **pad2)
        s9_E.grid(row=10, column=1, **pad2)
        s10_E.grid(row=11, column=1, **pad2)
        s11_E.grid(row=12, column=1, **pad2)

        eb_lst = [s0_E, s1_E, s2_E, s3_E, s4_E, s5_E, s6_E, s7_E, s8_E, s9_E, s10_E, s11_E]
        load = ttk.Button(
            buttons_frame, text='Load', style='h10b.TButton', width=20,
            command=lambda: page_funcs.load_page(
                self.attribute_dict, tb_dict=self.text_box_dict, eb_var=eb_lst))
        load.grid(row=1, column=1, **pad2_e)

        f = 'spec'
        s0_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s0.fpath, eb_var=s0_E, ftype=f))
        s1_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s1.fpath, eb_var=s1_E, ftype=f))
        s2_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s2.fpath, eb_var=s2_E, ftype=f))
        s3_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s3.fpath, eb_var=s3_E, ftype=f))
        s4_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s4.fpath, eb_var=s4_E, ftype=f))
        s5_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s5.fpath, eb_var=s5_E, ftype=f))
        s6_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s6.fpath, eb_var=s6_E, ftype=f))
        s7_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s7.fpath, eb_var=s7_E, ftype=f))
        s8_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s8.fpath, eb_var=s8_E, ftype=f))
        s9_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s9.fpath, eb_var=s9_E, ftype=f))
        s10_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s10.fpath, eb_var=s10_E, ftype=f))
        s11_browse = ttk.Button(
            frame_1, text='Browse', style='h8b.TButton',
            command=lambda: page_funcs.write_path(self.s11.fpath, eb_var=s11_E, ftype=f))
        s0_browse.grid(row=1, column=2, **pad2)
        s1_browse.grid(row=2, column=2, **pad2)
        s2_browse.grid(row=3, column=2, **pad2)
        s3_browse.grid(row=4, column=2, **pad2)
        s4_browse.grid(row=5, column=2, **pad2)
        s5_browse.grid(row=6, column=2, **pad2)
        s6_browse.grid(row=7, column=2, **pad2)
        s7_browse.grid(row=8, column=2, **pad2)
        s8_browse.grid(row=9, column=2, **pad2)
        s9_browse.grid(row=10, column=2, **pad2)
        s10_browse.grid(row=11, column=2, **pad2)
        s11_browse.grid(row=12, column=2, **pad2)

        s0_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s0.show)
        s1_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s1.show)
        s2_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s2.show)
        s3_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s3.show)
        s4_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s4.show)
        s5_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s5.show)
        s6_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s6.show)
        s7_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s7.show)
        s8_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s8.show)
        s9_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s9.show)
        s10_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s10.show)
        s11_show_checkbox = ttk.Checkbutton(frame_1, variable=self.s11.show)
        s0_show_checkbox.grid(row=1, column=3, **pad2)
        s1_show_checkbox.grid(row=2, column=3, **pad2)
        s2_show_checkbox.grid(row=3, column=3, **pad2)
        s3_show_checkbox.grid(row=4, column=3, **pad2)
        s4_show_checkbox.grid(row=5, column=3, **pad2)
        s5_show_checkbox.grid(row=6, column=3, **pad2)
        s6_show_checkbox.grid(row=7, column=3, **pad2)
        s7_show_checkbox.grid(row=8, column=3, **pad2)
        s8_show_checkbox.grid(row=9, column=3, **pad2)
        s9_show_checkbox.grid(row=10, column=3, **pad2)
        s10_show_checkbox.grid(row=11, column=3, **pad2)
        s11_show_checkbox.grid(row=12, column=3, **pad2)

        s0_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s0.invert)
        s1_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s1.invert)
        s2_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s2.invert)
        s3_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s3.invert)
        s4_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s4.invert)
        s5_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s5.invert)
        s6_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s6.invert)
        s7_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s7.invert)
        s8_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s8.invert)
        s9_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s9.invert)
        s10_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s10.invert)
        s11_invert_checkbox = ttk.Checkbutton(frame_1, variable=self.s11.invert)
        s0_invert_checkbox.grid(row=1, column=4, **pad2)
        s1_invert_checkbox.grid(row=2, column=4, **pad2)
        s2_invert_checkbox.grid(row=3, column=4, **pad2)
        s3_invert_checkbox.grid(row=4, column=4, **pad2)
        s4_invert_checkbox.grid(row=5, column=4, **pad2)
        s5_invert_checkbox.grid(row=6, column=4, **pad2)
        s6_invert_checkbox.grid(row=7, column=4, **pad2)
        s7_invert_checkbox.grid(row=8, column=4, **pad2)
        s8_invert_checkbox.grid(row=9, column=4, **pad2)
        s9_invert_checkbox.grid(row=10, column=4, **pad2)
        s10_invert_checkbox.grid(row=11, column=4, **pad2)
        s11_invert_checkbox.grid(row=12, column=4, **pad2)

        colors = ('black', 'red', 'blue', 'green', 'cyan', 'purple',
                  'lime', 'gold', 'teal', 'salmon', 'darkblue', 'sienna')
        self.s0_color_menu = ttk.Combobox(frame_1, textvariable=self.s0.color, justify=c, width=13)
        s1_color_menu = ttk.Combobox(frame_1, textvariable=self.s1.color, justify=c, width=13)
        s2_color_menu = ttk.Combobox(frame_1, textvariable=self.s2.color, justify=c, width=13)
        s3_color_menu = ttk.Combobox(frame_1, textvariable=self.s3.color, justify=c, width=13)
        s4_color_menu = ttk.Combobox(frame_1, textvariable=self.s4.color, justify=c, width=13)
        s5_color_menu = ttk.Combobox(frame_1, textvariable=self.s5.color, justify=c, width=13)
        s6_color_menu = ttk.Combobox(frame_1, textvariable=self.s6.color, justify=c, width=13)
        s7_color_menu = ttk.Combobox(frame_1, textvariable=self.s7.color, justify=c, width=13)
        s8_color_menu = ttk.Combobox(frame_1, textvariable=self.s8.color, justify=c, width=13)
        s9_color_menu = ttk.Combobox(frame_1, textvariable=self.s9.color, justify=c, width=13)
        s10_color_menu = ttk.Combobox(frame_1, textvariable=self.s10.color, justify=c, width=13)
        s11_color_menu = ttk.Combobox(frame_1, textvariable=self.s11.color, justify=c, width=13)

        color_menus = [
            self.s0_color_menu, s1_color_menu, s2_color_menu, s3_color_menu, s4_color_menu,
            s5_color_menu, s6_color_menu, s7_color_menu, s8_color_menu, s9_color_menu,
            s10_color_menu, s11_color_menu]
        for menu in color_menus:
            menu['values'] = colors
        self.s0_color_menu.grid(row=1, column=5, **pad2)
        s1_color_menu.grid(row=2, column=5, **pad2)
        s2_color_menu.grid(row=3, column=5, **pad2)
        s3_color_menu.grid(row=4, column=5, **pad2)
        s4_color_menu.grid(row=5, column=5, **pad2)
        s5_color_menu.grid(row=6, column=5, **pad2)
        s6_color_menu.grid(row=7, column=5, **pad2)
        s7_color_menu.grid(row=8, column=5, **pad2)
        s8_color_menu.grid(row=9, column=5, **pad2)
        s9_color_menu.grid(row=10, column=5, **pad2)
        s10_color_menu.grid(row=11, column=5, **pad2)
        s11_color_menu.grid(row=12, column=5, **pad2)

        markers = ('None', '.', 'o', 'x', 'D', '^', 'v')
        s0_marker_menu = ttk.Combobox(frame_1, textvariable=self.s0.marker, justify=c, width=13)
        s1_marker_menu = ttk.Combobox(frame_1, textvariable=self.s1.marker, justify=c, width=13)
        s2_marker_menu = ttk.Combobox(frame_1, textvariable=self.s2.marker, justify=c, width=13)
        s3_marker_menu = ttk.Combobox(frame_1, textvariable=self.s3.marker, justify=c, width=13)
        s4_marker_menu = ttk.Combobox(frame_1, textvariable=self.s4.marker, justify=c, width=13)
        s5_marker_menu = ttk.Combobox(frame_1, textvariable=self.s5.marker, justify=c, width=13)
        s6_marker_menu = ttk.Combobox(frame_1, textvariable=self.s6.marker, justify=c, width=13)
        s7_marker_menu = ttk.Combobox(frame_1, textvariable=self.s7.marker, justify=c, width=13)
        s8_marker_menu = ttk.Combobox(frame_1, textvariable=self.s8.marker, justify=c, width=13)
        s9_marker_menu = ttk.Combobox(frame_1, textvariable=self.s9.marker, justify=c, width=13)
        s10_marker_menu = ttk.Combobox(frame_1, textvariable=self.s10.marker, justify=c, width=13)
        s11_marker_menu = ttk.Combobox(frame_1, textvariable=self.s11.marker, justify=c, width=13)

        marker_menus = [
            s0_marker_menu, s1_marker_menu, s2_marker_menu, s3_marker_menu, s4_marker_menu,
            s5_marker_menu, s6_marker_menu, s7_marker_menu, s8_marker_menu, s9_marker_menu,
            s10_marker_menu, s11_marker_menu]
        for menu in marker_menus:
            menu['values'] = markers
        s0_marker_menu.grid(row=1, column=6, **pad2)
        s1_marker_menu.grid(row=2, column=6, **pad2)
        s2_marker_menu.grid(row=3, column=6, **pad2)
        s3_marker_menu.grid(row=4, column=6, **pad2)
        s4_marker_menu.grid(row=5, column=6, **pad2)
        s5_marker_menu.grid(row=6, column=6, **pad2)
        s6_marker_menu.grid(row=7, column=6, **pad2)
        s7_marker_menu.grid(row=8, column=6, **pad2)
        s8_marker_menu.grid(row=9, column=6, **pad2)
        s9_marker_menu.grid(row=10, column=6, **pad2)
        s10_marker_menu.grid(row=11, column=6, **pad2)
        s11_marker_menu.grid(row=12, column=6, **pad2)

        weights = ('0.25', '0.5', '0.75', '1', '1.5', '2', '3')
        s0_weight_menu = ttk.Combobox(frame_1, textvariable=self.s0.weight, justify=c, width=13)
        s1_weight_menu = ttk.Combobox(frame_1, textvariable=self.s1.weight, justify=c, width=13)
        s2_weight_menu = ttk.Combobox(frame_1, textvariable=self.s2.weight, justify=c, width=13)
        s3_weight_menu = ttk.Combobox(frame_1, textvariable=self.s3.weight, justify=c, width=13)
        s4_weight_menu = ttk.Combobox(frame_1, textvariable=self.s4.weight, justify=c, width=13)
        s5_weight_menu = ttk.Combobox(frame_1, textvariable=self.s5.weight, justify=c, width=13)
        s6_weight_menu = ttk.Combobox(frame_1, textvariable=self.s6.weight, justify=c, width=13)
        s7_weight_menu = ttk.Combobox(frame_1, textvariable=self.s7.weight, justify=c, width=13)
        s8_weight_menu = ttk.Combobox(frame_1, textvariable=self.s8.weight, justify=c, width=13)
        s9_weight_menu = ttk.Combobox(frame_1, textvariable=self.s9.weight, justify=c, width=13)
        s10_weight_menu = ttk.Combobox(frame_1, textvariable=self.s10.weight, justify=c, width=13)
        s11_weight_menu = ttk.Combobox(frame_1, textvariable=self.s11.weight, justify=c, width=13)

        weight_menus = [
            s0_weight_menu, s1_weight_menu, s2_weight_menu, s3_weight_menu, s4_weight_menu,
            s5_weight_menu, s6_weight_menu, s7_weight_menu, s8_weight_menu, s9_weight_menu,
            s10_weight_menu, s11_weight_menu]
        for menu in weight_menus:
            menu['values'] = weights
        s0_weight_menu.grid(row=1, column=7, **pad2)
        s1_weight_menu.grid(row=2, column=7, **pad2)
        s2_weight_menu.grid(row=3, column=7, **pad2)
        s3_weight_menu.grid(row=4, column=7, **pad2)
        s4_weight_menu.grid(row=5, column=7, **pad2)
        s5_weight_menu.grid(row=6, column=7, **pad2)
        s6_weight_menu.grid(row=7, column=7, **pad2)
        s7_weight_menu.grid(row=8, column=7, **pad2)
        s8_weight_menu.grid(row=9, column=7, **pad2)
        s9_weight_menu.grid(row=10, column=7, **pad2)
        s10_weight_menu.grid(row=11, column=7, **pad2)
        s11_weight_menu.grid(row=12, column=7, **pad2)

        s0_scale_E = ttk.Entry(frame_1, textvariable=self.s0.scale, justify=c)
        s1_scale_E = ttk.Entry(frame_1, textvariable=self.s1.scale, justify=c)
        s2_scale_E = ttk.Entry(frame_1, textvariable=self.s2.scale, justify=c)
        s3_scale_E = ttk.Entry(frame_1, textvariable=self.s3.scale, justify=c)
        s4_scale_E = ttk.Entry(frame_1, textvariable=self.s4.scale, justify=c)
        s5_scale_E = ttk.Entry(frame_1, textvariable=self.s5.scale, justify=c)
        s6_scale_E = ttk.Entry(frame_1, textvariable=self.s6.scale, justify=c)
        s7_scale_E = ttk.Entry(frame_1, textvariable=self.s7.scale, justify=c)
        s8_scale_E = ttk.Entry(frame_1, textvariable=self.s8.scale, justify=c)
        s9_scale_E = ttk.Entry(frame_1, textvariable=self.s9.scale, justify=c)
        s10_scale_E = ttk.Entry(frame_1, textvariable=self.s10.scale, justify=c)
        s11_scale_E = ttk.Entry(frame_1, textvariable=self.s11.scale, justify=c)
        s0_scale_E.grid(row=1, column=8, **pad2)
        s1_scale_E.grid(row=2, column=8, **pad2)
        s2_scale_E.grid(row=3, column=8, **pad2)
        s3_scale_E.grid(row=4, column=8, **pad2)
        s4_scale_E.grid(row=5, column=8, **pad2)
        s5_scale_E.grid(row=6, column=8, **pad2)
        s6_scale_E.grid(row=7, column=8, **pad2)
        s7_scale_E.grid(row=8, column=8, **pad2)
        s8_scale_E.grid(row=9, column=8, **pad2)
        s9_scale_E.grid(row=10, column=8, **pad2)
        s10_scale_E.grid(row=11, column=8, **pad2)
        s11_scale_E.grid(row=12, column=8, **pad2)

        s0_legend_E = ttk.Entry(frame_1, textvariable=self.s0.legend, justify=c)
        s1_legend_E = ttk.Entry(frame_1, textvariable=self.s1.legend, justify=c)
        s2_legend_E = ttk.Entry(frame_1, textvariable=self.s2.legend, justify=c)
        s3_legend_E = ttk.Entry(frame_1, textvariable=self.s3.legend, justify=c)
        s4_legend_E = ttk.Entry(frame_1, textvariable=self.s4.legend, justify=c)
        s5_legend_E = ttk.Entry(frame_1, textvariable=self.s5.legend, justify=c)
        s6_legend_E = ttk.Entry(frame_1, textvariable=self.s6.legend, justify=c)
        s7_legend_E = ttk.Entry(frame_1, textvariable=self.s7.legend, justify=c)
        s8_legend_E = ttk.Entry(frame_1, textvariable=self.s8.legend, justify=c)
        s9_legend_E = ttk.Entry(frame_1, textvariable=self.s9.legend, justify=c)
        s10_legend_E = ttk.Entry(frame_1, textvariable=self.s10.legend, justify=c)
        s11_legend_E = ttk.Entry(frame_1, textvariable=self.s11.legend, justify=c)
        s0_legend_E.grid(row=1, column=9, **pad2)
        s1_legend_E.grid(row=2, column=9, **pad2)
        s2_legend_E.grid(row=3, column=9, **pad2)
        s3_legend_E.grid(row=4, column=9, **pad2)
        s4_legend_E.grid(row=5, column=9, **pad2)
        s5_legend_E.grid(row=6, column=9, **pad2)
        s6_legend_E.grid(row=7, column=9, **pad2)
        s7_legend_E.grid(row=8, column=9, **pad2)
        s8_legend_E.grid(row=9, column=9, **pad2)
        s9_legend_E.grid(row=10, column=9, **pad2)
        s10_legend_E.grid(row=11, column=9, **pad2)
        s11_legend_E.grid(row=12, column=9, **pad2)

        frame_2 = ttk.Frame(self.frame)
        frame_2.grid(row=6, column=0, columnspan=2)
        axis_label_frame = ttk.Frame(frame_2)
        axis_label_frame.grid(row=0, column=1, sticky='n')
        axis_adjust_frame = ttk.Frame(frame_2)
        axis_adjust_frame.grid(row=0, column=3, sticky='n')
        legend_frame = ttk.Frame(frame_2)
        legend_frame.grid(row=0, column=5, sticky='n')
        notes_frame = ttk.Frame(frame_2)
        notes_frame.grid(row=0, column=7, sticky='nw')

        x50y5_ns = {'padx': 50, 'pady': 5, 'sticky': 'ns'}
        ttk.Separator(frame_2, orient='vertical').grid(row=0, column=0, **x50y5_ns)
        ttk.Separator(frame_2, orient='vertical').grid(row=0, column=2, **x50y5_ns)
        ttk.Separator(frame_2, orient='vertical').grid(row=0, column=4, **x50y5_ns)
        ttk.Separator(frame_2, orient='vertical').grid(row=0, column=6, **x50y5_ns)
        ttk.Separator(frame_2, orient='vertical').grid(row=0, column=8, padx=5, pady=5, sticky='ns')

        plot_params_L = ttk.Label(axis_label_frame, text='Axes Labels', **center_h10b)
        plot_title_L = ttk.Label(axis_label_frame, text='Plot Title', style='h8b.TLabel', justify=r)
        xlabel_L = ttk.Label(axis_label_frame, text='X-axis Title', style='h8b.TLabel', justify=r)
        ylabel_L = ttk.Label(axis_label_frame, text='Y-axis Title', style='h8b.TLabel', justify=r)
        plot_title_E = ttk.Entry(axis_label_frame, textvariable=self.plot.plot_title, justify=c)
        xlabel_E = ttk.Entry(axis_label_frame, textvariable=self.plot.xlabel, justify=c)
        ylabel_E = ttk.Entry(axis_label_frame, textvariable=self.plot.ylabel, justify=c)
        plot_params_L.grid(row=0, column=0, columnspan=2, **pad2)
        plot_title_L.grid(row=1, column=0, **pad2_e)
        xlabel_L.grid(row=2, column=0, **pad2_e)
        ylabel_L.grid(row=3, column=0, **pad2_e)
        plot_title_E.grid(row=1, column=1, **pad2_w)
        xlabel_E.grid(row=2, column=1, **pad2_w)
        ylabel_E.grid(row=3, column=1, **pad2_w)

        adjust_mode_L = ttk.Label(axis_adjust_frame, text='Manually Adjust Axes', **right_h10b)
        manual_L = ttk.Label(axis_adjust_frame, text='Manual Mode', style='h8b.TLabel', justify=r)
        x_min_L = ttk.Label(axis_adjust_frame, text='Freq. Min', style='h8b.TLabel', justify=r)
        x_max_L = ttk.Label(axis_adjust_frame, text='Freq. Max', style='h8b.TLabel', justify=r)
        y_min_L = ttk.Label(axis_adjust_frame, text='Intensity Min', style='h8b.TLabel', justify=r)
        y_max_L = ttk.Label(axis_adjust_frame, text='Intensity Max', style='h8b.TLabel', justify=r)
        x_inc_L = ttk.Label(axis_adjust_frame, text='X Ticks', style='h8b.TLabel', justify=r)
        y_inc_L = ttk.Label(axis_adjust_frame, text='Y Ticks', style='h8b.TLabel', justify=r)
        minor_ticks_L = ttk.Label(
            axis_adjust_frame, text='Minor Ticks', style='h8b.TLabel', justify=r)
        adjust_mode_checkbox = ttk.Checkbutton(axis_adjust_frame, variable=self.plot.zoom_mode)
        freq_min_E = ttk.Entry(axis_adjust_frame, textvariable=self.plot.xmin, justify=c)
        freq_max_E = ttk.Entry(axis_adjust_frame, textvariable=self.plot.xmax, justify=c)
        int_min_E = ttk.Entry(axis_adjust_frame, textvariable=self.plot.ymin, justify=c)
        int_max_E = ttk.Entry(axis_adjust_frame, textvariable=self.plot.ymax, justify=c)
        x_inc_E = ttk.Entry(axis_adjust_frame, textvariable=self.plot.x_inc, justify=c)
        y_inc_E = ttk.Entry(axis_adjust_frame, textvariable=self.plot.y_inc, justify=c)
        minor_ticks_checkbox = ttk.Checkbutton(axis_adjust_frame, variable=self.plot.minor_ticks)
        adjust_mode_L.grid(row=0, column=0, columnspan=2, **pad2)
        manual_L.grid(row=1, column=0, **pad2_e)
        x_min_L.grid(row=2, column=0, **pad2_e)
        x_max_L.grid(row=3, column=0, **pad2_e)
        y_min_L.grid(row=4, column=0, **pad2_e)
        y_max_L.grid(row=5, column=0, **pad2_e)
        x_inc_L.grid(row=6, column=0, **pad2_e)
        y_inc_L.grid(row=7, column=0, **pad2_e)
        minor_ticks_L.grid(row=8, column=0, **pad2_e)
        adjust_mode_checkbox.grid(row=1, column=1, padx=50, pady=2, sticky='w')
        freq_min_E.grid(row=2, column=1, **pad2_w)
        freq_max_E.grid(row=3, column=1, **pad2_w)
        int_min_E.grid(row=4, column=1, **pad2_w)
        int_max_E.grid(row=5, column=1, **pad2_w)
        x_inc_E.grid(row=6, column=1, **pad2_w)
        y_inc_E.grid(row=7, column=1, **pad2_w)
        minor_ticks_checkbox.grid(row=8, column=1, padx=50, pady=2, sticky='w')

        legend_params_L = ttk.Label(legend_frame, text='Plot Legend', **center_h10b)
        legend_show_L = ttk.Label(legend_frame, text='Show', style='h8b.TLabel', justify=r)
        legend_font_L = ttk.Label(legend_frame, text='Font', style='h8b.TLabel', justify=r)
        legend_loc_L = ttk.Label(legend_frame, text='Position', style='h8b.TLabel', justify=r)
        legend_show_checkbox = ttk.Checkbutton(legend_frame, variable=self.plot.legend_show)
        legend_font_E = ttk.Entry(legend_frame, textvariable=self.plot.legend_font, justify=c)

        top_right_radio = ttk.Radiobutton(
            legend_frame, text='Top Right', style='h8.TRadiobutton', variable=self.plot.legend_loc,
            value=0)
        bottom_right_radio = ttk.Radiobutton(
            legend_frame, text='Bottom Right', style='h8.TRadiobutton',
            variable=self.plot.legend_loc, value=1)
        top_left_radio = ttk.Radiobutton(
            legend_frame, text='Top Left', style='h8.TRadiobutton', variable=self.plot.legend_loc,
            value=2)
        bottom_left_radio = ttk.Radiobutton(
            legend_frame, text='Bottom Left', style='h8.TRadiobutton',
            variable=self.plot.legend_loc, value=3)
        legend_params_L.grid(row=0, column=0, columnspan=2, **pad2)
        legend_show_L.grid(row=1, column=0, **pad2_e)
        legend_font_L.grid(row=2, column=0, **pad2_e)
        legend_loc_L.grid(row=3, column=0, **pad2_e)
        legend_show_checkbox.grid(row=1, column=1, padx=50, pady=2, sticky='w')
        legend_font_E.grid(row=2, column=1, **pad2_w)
        top_right_radio.grid(row=3, column=1, **pad2_w)
        bottom_right_radio.grid(row=4, column=1, **pad2_w)
        top_left_radio.grid(row=5, column=1, **pad2_w)
        bottom_left_radio.grid(row=6, column=1, **pad2_w)

        notes_L = ttk.Label(notes_frame, text='Notes', **center_h10b)
        self.notes_textbox = tk.Text(
            notes_frame, relief='sunken', font='Helvetica 8', height=14, wrap=tk.WORD)
        self.notes_textbox.delete('1.0', tk.END)
        self.notes_textbox.insert('1.0', 'None')
        notes_L.grid(row=0, column=0, sticky='nw')
        self.notes_textbox.grid(row=1, column=0, padx=30, sticky='ew')

        self.plot_attribute_dict = {
            'plot_title': self.plot.plot_title, 'xlabel': self.plot.xlabel,
            'ylabel': self.plot.ylabel, 'minor_ticks': self.plot.minor_ticks,
            'manual_mode': self.plot.zoom_mode, 'freq_min': self.plot.xmin,
            'freq_max': self.plot.xmax, 'int_min': self.plot.ymin, 'int_max': self.plot.ymax,
            'x_inc': self.plot.x_inc, 'y_inc': self.plot.y_inc,
            'show_legend': self.plot.legend_show, 'legend_font': self.plot.legend_font,
            'legend_loc': self.plot.legend_loc}

        self.attribute_dict = {
            'plot_title': self.plot.plot_title, 'xlabel': self.plot.xlabel,
            'ylabel': self.plot.ylabel, 'minor_ticks': self.plot.minor_ticks,
            'manual_mode': self.plot.zoom_mode, 'freq_min': self.plot.xmin,
            'freq_max': self.plot.xmax, 'int_min': self.plot.ymin, 'int_max': self.plot.ymax,
            'x_inc': self.plot.x_inc, 'y_inc': self.plot.y_inc,
            'show_legend': self.plot.legend_show, 'legend_font': self.plot.legend_font,
            'legend_loc': self.plot.legend_loc, 'fpath0': self.s0.fpath, 'show0': self.s0.show,
            'invert0': self.s0.invert, 'scale0': self.s0.scale, 'color0': self.s0.color,
            'marker0': self.s0.marker, 'weight0': self.s0.weight, 'label0': self.s0.legend,
            'fpath1': self.s1.fpath, 'show1': self.s1.show, 'invert1': self.s1.invert,
            'scale1': self.s1.scale, 'color1': self.s1.color, 'marker1': self.s1.marker,
            'weight1': self.s1.weight, 'label1': self.s1.legend, 'fpath2': self.s2.fpath,
            'show2': self.s2.show, 'invert2': self.s2.invert, 'scale2': self.s2.scale,
            'color2': self.s2.color, 'marker2': self.s2.marker, 'weight2': self.s2.weight,
            'label2': self.s2.legend, 'fpath3': self.s3.fpath, 'show3': self.s3.show,
            'invert3': self.s3.invert, 'scale3': self.s3.scale, 'color3': self.s3.color,
            'marker3': self.s3.marker, 'weight3': self.s3.weight, 'label3': self.s3.legend,
            'fpath4': self.s4.fpath, 'show4': self.s4.show, 'invert4': self.s4.invert,
            'scale4': self.s4.scale, 'color4': self.s4.color, 'marker4': self.s4.marker,
            'weight4': self.s4.weight, 'label4': self.s4.legend, 'fpath5': self.s5.fpath,
            'show5': self.s5.show, 'invert5': self.s5.invert, 'scale5': self.s5.scale,
            'color5': self.s5.color, 'marker5': self.s5.marker, 'weight5': self.s5.weight,
            'label5': self.s5.legend, 'fpath6': self.s6.fpath, 'show6': self.s6.show,
            'invert6': self.s6.invert, 'scale6': self.s6.scale, 'color6': self.s6.color,
            'marker6': self.s6.marker, 'weight6': self.s6.weight, 'label6': self.s6.legend,
            'fpath7': self.s7.fpath, 'show7': self.s7.show, 'invert7': self.s7.invert,
            'scale7': self.s7.scale, 'color7': self.s7.color, 'marker7': self.s7.marker,
            'weight7': self.s7.weight, 'label7': self.s7.legend, 'fpath8': self.s8.fpath,
            'show8': self.s8.show, 'invert8': self.s8.invert, 'scale8': self.s8.scale,
            'color8': self.s8.color, 'marker8': self.s8.marker, 'weight8': self.s8.weight,
            'label8': self.s8.legend, 'fpath9': self.s9.fpath, 'show9': self.s9.show,
            'invert9': self.s9.invert, 'scale9': self.s9.scale, 'color9': self.s9.color,
            'marker9': self.s9.marker, 'weight9': self.s9.weight, 'label9': self.s9.legend,
            'fpath10': self.s10.fpath, 'show10': self.s10.show, 'invert10': self.s10.invert,
            'scale10': self.s10.scale, 'color10': self.s10.color, 'marker10': self.s10.marker,
            'weight10': self.s10.weight, 'label10': self.s10.legend, 'fpath11': self.s11.fpath,
            'show11': self.s11.show, 'invert11': self.s11.invert, 'scale11': self.s11.scale,
            'color11': self.s11.color, 'marker11': self.s11.marker, 'weight11': self.s11.weight,
            'label11': self.s11.legend}

        self.text_box_dict = {'notes': self.notes_textbox}
        self.page.open_combobox(self.s0_color_menu)
        page_funcs.unbind_combo_scroll(self.s0_color_menu)
        self.page.enter_textbox(self.notes_textbox)
        self.page.exit_textbox(self.notes_textbox)
        self.page.left_click()
        self.series_dict = {
            0: self.s0, 1: self.s1, 2: self.s2, 3: self.s3, 4: self.s4, 5: self.s5, 6: self.s6,
            7: self.s7, 8: self.s8, 9: self.s9, 10: self.s10, 11: self.s11}

    def fpath_changed(self):
        """
        Determine file paths that have been changed.

        Return:
            changed (list of bools):
        """

        series = [self.s0, self.s1, self.s2, self.s3, self.s4, self.s5, self.s6, self.s7, self.s8,
                  self.s9, self.s10, self.s11]
        changed = []
        for x in series:
            params = [(x.fpath, x.series_copy, x.fpath.get(), x.series_copy.get())]
            for current, previous, fpath_get, copy_get in params:
                fpath = current.get()
                copy = previous.get()
                if fpath == copy:
                    changed.append(False)
                else:
                    changed.append(True)
                    previous.set(fpath)
                    previous.get()
        return changed

    def fpath_is_column_of_root(self, x, arr):
        """
        Determine if series holds a column of a multi-spectra matrix by the value of series.fpath.

        When a data series holds data from columns other than the first two (col[0] -> frequency,
        col[1] -> intensity of first spectrum), the series.fpath variable is changed to '{base file
        name}  column  {X}' where {base file name} is the file name of the matrix and X is the
        column of matrix. This information is relayed to the GUI.

        Append file name, series number, and column number to arr.

        Parameters:
            x (int):
                Parameter passed to self.series_dict.
            arr (list):
                Append file name, series number, and column number to arr.
        Return:
            is_column (bool):
                If series holds column of matrix == True
        """
        spec_path = self.series_dict[x].fpath.get()
        split = spec_path.split()
        try:
            if split[-2] == 'column':
                is_column = True
                y = x - 1
                while y > 11:
                    y += -1
                while self.series_dict[y].fpath.get().split()[-2] == 'column':
                    y += -1
                root_spec = self.series_dict[y].fpath.get()
                arr.append((root_spec, x, int(split[-1])))
            else:
                is_column = False
        except IndexError:
            is_column = False
        return is_column

    def fpath_is_root_spec(self, x):
        """
        Determine if series.fpath is the root spectrum name. In other words, not a column of root.

        If series.fpath is root spectrum, check size of spectrum array. If more than 2 columns,
        ask user if they want to expand the columns of the matrix into subsequent data series. If
        they choose to, fpath entry boxes are changed to show the columns they hold.

        Parameters:
            x (int):
                Parameter passed to self.series_dict.
        """
        spec_path = self.series_dict[x].fpath.get()
        spectrum = Spectrum(spec_path)
        self.series_dict[x].series_copy.set(spec_path)
        try:
            spec = spectrum.spectrum
        except AttributeError:
            self.series_dict[x].x = []
            self.series_dict[x].y = []
        if spec.shape[1] > 2:
            bname = os.path.basename(spec_path)
            msg = "Expand matrix using row(s) below? Files in these rows will be overwritten."
            expand_matrix = messagebox.askyesno("Multiple Spectrum Matrix Detected", msg)
            if expand_matrix:
                for c in range(1, spec.shape[1]):
                    try:
                        series_num = x + c - 1
                        self.series_dict[series_num].x = spec[:, 0]
                        self.series_dict[series_num].y = spec[:, c]
                        if c != 1:
                            fpath = 'fpath' + str(x + c - 1)
                            n = bname + '  column  ' + str(c)
                            self.series_dict[series_num].fpath.set(n)
                            self.series_dict[series_num].series_copy.set(n)
                    except KeyError:
                        num_spec = spec.shape[1] - 1
                        msg = "Number of spectra in matrix (" + str(num_spec) + \
                              ") exceeds available number of data series. To view other columns " \
                              "of " + str(bname) + ", change the column numbers in the file paths."
                        messagebox.showerror("Available Space Exceeded", message=msg)
                        break
        else:
            self.series_dict[x].x = spec[:, 0]
            self.series_dict[x].y = spec[:, 1]

    def plot_series(self):
        """ Plot data series using options from the GUI. """
        p = self.controller.picker
        xs, ys, invert, scale, color, marker, weight, label, label_show, picker = \
            [], [], [], [], [], [], [], [], [], []
        for x in self.series_dict.values():
            if x.show.get() == 1:
                scale.append(x.scale.get())
                weight.append(x.weight.get())
                label.append(x.legend.get())
                label_show.append(x.legend.get())
                color.append(x.color.get())
                marker.append(x.marker.get())
                picker.append(p)
                if x.invert.get() == 1:
                    invert.append(True)
                else:
                    invert.append(False)
                if x.fpath.get() != 'None':
                    xs.append(x.x)
                    ys.append(x.y)
        self.plot.plot_lines(
            xs, ys, invert=invert, scale=scale, color=color, marker=marker, weight=weight,
            label=label, picker=picker)

    def update_axes(self):
        """ Adjust axes using options from the GUI. """
        adjust_mode = self.attribute_dict['manual_mode'].get()
        axes_keys = ['freq_min', 'freq_max', 'int_min', 'int_max', 'x_inc', 'y_inc']
        axis_dict = {}
        if adjust_mode == 1:
            for key in axes_keys:
                if self.plot_attribute_dict[key] != SpecExplorer.default[key]:
                    axis_dict[key] = self.plot_attribute_dict[key].get()
                else:
                    axis_dict[key] = SpecExplorer.default[key]
        else:
            for key in axes_keys:
                axis_dict[key] = SpecExplorer.default[key]
        self.plot.set_labels()
        self.plot.zoom(
            xmin=axis_dict['freq_min'], xmax=axis_dict['freq_max'], ymin=axis_dict['int_min'],
            ymax=axis_dict['int_max'], x_inc=axis_dict['x_inc'], y_inc=axis_dict['y_inc'],
            minor_ticks=self.plot.minor_ticks.get())

    @testing.collect_garbage
    @testing.memory_allocation
    def update_plot(self):
        """
        Update plot based on GUI settings. Runs when UPDATE pressed.

        1.  Detect changes to file path variables.
        2.  When a matrix of spectra is uploaded, user has the option to view up to 12
            columns of the matrix by loading columns across multiple data series. For example, rows
            1-5 of the GUI will hold 5 spectra if the user uploads a matrix consisting of 5
            unique spectra. File path variables are updated automatically to reflect that the data
            series represents a particular column of the matrix. To view spectra past col[12],
            change the column number in the file path entry box to the desired column number.
        3.  Axes cleared.
        4.  Line settings (these settings are to the right of the file paths) are collected for all
            data series set to 'show'.
        5.  Scale axes (auto or manual).
        6.  Draw plot.
        """
        series_changed = self.fpath_changed()
        bname_series_col = []
        try:
            for x, i in enumerate(series_changed):
                if i:
                    is_col = self.fpath_is_column_of_root(x, bname_series_col)
                    if not is_col:
                        self.fpath_is_root_spec(x)
            updates = {}
            for root, series, col in bname_series_col:
                if root in updates.keys():
                    updates[root].append((series, col))
                else:
                    updates[root] = [(series, col)]
            for root in updates.keys():
                spectrum = Spectrum(root)
                spec = spectrum.spectrum
                for series, col in updates[root]:
                    self.series_dict[series].x = spec[:, 0]
                    self.series_dict[series].y = spec[:, col]
        except AttributeError:
            pass
        self.plot.ax.cla()
        # self.plot.figure.clf()
        self.plot_series()
        self.update_axes()
        self.plot.canvas.draw()
        self.plot.toolbar.update()
