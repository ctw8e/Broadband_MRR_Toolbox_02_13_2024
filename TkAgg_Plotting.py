import numpy as np
import numpy.linalg as LA
import math
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from Pages.Settings import Settings

color_dict = {None: None, 'None': None, 'none': None,
              'black': '0', '0': '0',
              'blue': 'C0', 'tab:blue': 'C0', 'b': 'C0', 'C0': 'C0',
              'orange': 'C1', 'o': 'C1', 'C1': 'C1',
              'green': 'C2', 'g': 'C2', 'C2': 'C2',
              'red': 'C3', 'r': 'C3', 'C3': 'C3',
              'purple': 'C4', 'C4': 'C4', 'brown': 'C5', 'C5': 'C5',
              'pink': 'C6', 'C6': 'C6', 'grey': 'C7', 'C7': 'C7',
              'yellow': 'C8', 'C8': 'C8', 'cyan': 'C9', 'C9': 'C9',
              'chartreuse': 'chartreuse', 'yellowgreen': 'yellowgreen',
              'lime': 'lime', 'gold': 'gold', 'teal': 'teal',
              'salmon': 'salmon', 'darkblue': 'darkblue', 'sienna': 'sienna'}


class SpecPlot:
    """
    Handle matplotlib canvas objects. used in the GUI.

    Attributes:
        fpath (tk.StringVar):
            file path to spectrum.
        series_copy (tk.StringVar):
            copy of fpath to determine if series has changed and needs updating on the plot.
        subplot (mpl.ax object):
            matplotlib Axes object.
        show (tk.IntVar):
            Display data series on plot.
        invert (tk.IntVar):
            Invert data series.
        scale (tk.DoubleVar):
            Scale factor of data series.
        color (tk.StringVar):
            Color of data series.
        marker (tk.StringVar):
            Data point marker of data series.
        weight (tk.StringVar):
            Line weight of data series.
        legend (tk.StringVar):
            Displayed phrase in plot legend.
    """

    def __init__(self, subplot, fpath=None, show=None, invert=None, scale=None,
                 color=None, legend=None, marker=None, weight=None):
        self.fpath = tk.StringVar()
        self.series_copy = tk.StringVar()
        self.fpath.set(fpath) if fpath is not None else None
        fpath = str(self.fpath.get())
        self.series_copy.set(fpath)

        self.subplot = subplot

        self.show = tk.IntVar()
        self.show.set(show) if show is not None else None

        self.invert = tk.IntVar()
        self.invert.set(invert) if invert is not None else None

        self.scale = tk.DoubleVar()
        self.scale.set(scale) if scale is not None else None

        self.color = tk.StringVar()
        self.color.set(color) if color is not None else None

        self.marker = tk.StringVar()
        self.marker.set(marker) if marker is not None else None

        self.weight = tk.StringVar()
        self.weight.set(weight) if weight is not None else None

        self.legend = tk.StringVar()
        self.legend.set(legend) if legend is not None else None


class PlotManager(SpecPlot):
    """
    Handle matplotlib plots: zoom, plot title, axes titles, tick marks, legend.

    NAVIGATION BAR - Nav bars can be found under certain plots throughout the program.
        Buttons:
            HOME:
                Return plot to original zoom.
            BACK:
                Return to previous zoom/pan setting.
            FORWARD:
                Undo BACK
            PAN:
                Left click + mouse movement to drag plot.
                Right click + mouse movement to zoom along an axis.
            ZOOM:
                Zoom to a particular rectangular region.
                Select the region by holding left click and dragging.
            ADJUST MARGINS:
                Adjust plot aspect ratio. Useful for figures.
            SAVE IMAGE:
                Save non-interactive plot image.
    Attributes:
        zoom_mode (tk.IntVar()):
            0 -> auto. 1 -> manual.
        plot_title (tk.StringVar()):
            Plot title.
        xlabel (tk.StringVar()):
            x-axis title.
        ylabel (tk.StringVar()):
            y-axis title.
        zlabel (tk.StringVar()):
            z-axis title.
        x_min (tk.StringVar()):
            Lower bound x-axis.
        x_max (tk.StringVar()):
            Upper bound x-axis.
        y_min (tk.StringVar()):
            Lower bound y-axis.
        y_max (tk.StringVar()):
            Upper bound y-axis.
        z_min (tk.StringVar()):
            Lower bound z-axis.
        z_max (tk.StringVar()):
            Upper bound z-axis.
        x_inc (tk.StringVar()):
            accepts 1 or 3 entries. If only one item, sets number of
            ticks for axis range and automatically selects start and end values.
            If three items, first is the lower bound tick value, second item is
            the upper bound tick value, and third item is the number of total
            ticks.
        y_inc (tk.StringVar()):
            accepts 1 or 3 entries. If only one item, sets number of
            ticks for axis range and automatically selects start and end values.
            If three items, first is the lower bound tick value, second item is
            the upper bound tick value, and third item is the number of total
            ticks.
        z_inc (tk.StringVar()):
            accepts 1 or 3 entries. If only one item, sets number of
            ticks for axis range and automatically selects start and end values.
            If three items, first is the lower bound tick value, second item is
            the upper bound tick value, and third item is the number of total
            ticks.
        minor_ticks (tk.IntVar()):
            0 -> off. 1 -> on.
        legend_show (tk.IntVar()):
            0 -> off. 1 -> on.
        legend_font (tk.IntVar()):
            Legend font size.
        legend_loc (tk.IntVar()):
            0 -> upper right
            1 -> bottom right
            2 -> bottom left
            3 -> upper left
    Methods:
        plot_line(*args, **kwargs)
            Plot a data series on a plot Figure.
        plot_lines(*args, **kwargs)
            Plot multiple data series on a plot Figure.
        scatter_3d_single(*args, **kwargs)
            Plot 3d scatter plot.
        scatter_3d_multiple(*args, **kwargs)
            Plot multiple 3d scatter plot.
        histogram(*args, **kwargs)
            Plot histogram.
        plot_ellipse(*args, **kwargs)
            Draw ellipse on 2d matplotlib axes.
        plot_ellipsoid(*args, **kwargs)
            Draws sphere or ellipsoid on a 3d matplotlib axes.
        set_labels(*args, **kwargs)
            Update plot labels.
        manual_axis_zoom(*args, **kwargs)
            Handles manual axis scaling and sets appropriate tick increments.
        auto_axis_ticks(*args, **kwargs)
            Generates tick marks at non-arbitrary spacing when using autoscale.
        zoom(*args, **kwargs)
            Handles plot zooming, including different combinations of manual
            and auto-scale on different axes.
    """

    def __init__(
            self, frame=None, figsize=None, dpi=None, subplotshape=None, projection=None,
            zoom_mode=None, plot_title=None, xlabel=None, ylabel=None, zlabel=None, x_min=None,
            x_max=None, y_min=None, y_max=None, z_min=None, z_max=None, x_inc=None, y_inc=None,
            z_inc=None, minor_ticks=None, label_show=None, label_list=None, legend_show=None,
            legend_font=None, legend_loc=None, left=None, right=None, top=None, bottom=None,
            row=None, column=None, rowspan=None, columnspan=None, padx=None, pady=None, sticky=None,
            toolbar=True, toolrow=None, toolcol=None, toolcspan=None, toolpadx=None, toolpady=None,
            toolsticky=None):

        self.frame = frame
        self.figsize = figsize
        self.dpi = dpi
        self.subplotshape = subplotshape

        self.figure = Figure(figsize=figsize, dpi=dpi)

        self.zoom_mode = tk.IntVar()
        self.zoom_mode.set(zoom_mode) if zoom_mode is not None else None

        self.plot_title = tk.StringVar()
        self.plot_title.set(plot_title) if plot_title is not None else None

        self.xlabel = tk.StringVar()
        self.xlabel.set(xlabel) if xlabel is not None else None

        self.ylabel = tk.StringVar()
        self.ylabel.set(ylabel) if ylabel is not None else None

        self.zlabel = tk.StringVar()
        self.zlabel.set(zlabel) if zlabel is not None else None

        self.xmin = tk.StringVar()
        self.xmin.set(x_min) if x_min is not None else None

        self.xmax = tk.StringVar()
        self.xmax.set(x_max) if x_max is not None else None

        self.ymin = tk.StringVar()
        self.ymin.set(y_min) if y_min is not None else None

        self.ymax = tk.StringVar()
        self.ymax.set(y_max) if y_max is not None else None

        self.zmin = tk.StringVar()
        self.zmin.set(z_min) if z_min is not None else None

        self.zmax = tk.StringVar()
        self.zmax.set(z_max) if z_max is not None else None

        self.x_inc = tk.StringVar()
        self.x_inc.set(x_inc) if x_inc is not None else None

        self.y_inc = tk.StringVar()
        self.y_inc.set(y_inc) if y_inc is not None else None

        self.z_inc = tk.StringVar()
        self.z_inc.set(z_inc) if z_inc is not None else None

        self.minor_ticks = tk.IntVar()
        self.minor_ticks.set(minor_ticks) if minor_ticks is not None else None

        self.label_show = tk.IntVar()
        self.label_show.set(label_show) if label_show is not None else None

        self.legend_show = tk.IntVar()
        self.legend_show.set(legend_show) if legend_show is not None else None

        self.legend_font = tk.IntVar()
        self.legend_font.set(legend_font) if legend_font is not None else None

        self.legend_loc = tk.IntVar()
        self.legend_loc.set(legend_loc) if legend_loc is not None else None

        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

        self.subplotshape = subplotshape

        self.canvas = FigureCanvasTkAgg(self.figure, frame)
        # self.canvas.draw()
        self.canvas.get_tk_widget().grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=padx, pady=pady,
            sticky=sticky)
        self.ax = self.figure.add_subplot(subplotshape, projection=projection)
        self.set_labels(label_list=label_list)
        self.figure.subplots_adjust(left=left, right=right, top=top, bottom=bottom)

        if toolbar:
            self.toolbarFrame = ttk.Frame(frame, style='Frame1.TFrame')
            self.toolbarFrame.grid(
                row=toolrow, column=toolcol, columnspan=toolcspan, padx=toolpadx, pady=toolpady,
                sticky=toolsticky)
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)
            self.toolbar.configure(background='#f6f4f2')
            self.toolbar._message_label.configure(background='#f6f4f2', font='Helvetica 10 bold')
            self.toolbar.update()

    def plot_line(self, x, y, invert=False, scale_factor=None, color=None, marker=None, weight=None,
                  label=None, linestyle=None, picker=None):
        """
        Plot a data series on a plot Figure.

        See TkAgg_Plotting.plot_line() for information on **kwargs.
        """
        plot_line(
            self.ax, x, y, invert=invert, scale=scale_factor, color=color, marker=marker,
            weight=weight, label=label, linestyle=linestyle, picker=picker)

    def plot_lines(self, x, y, invert=None, scale=None, color=None, marker=None, weight=None,
                   label=None, linestyle=None, picker=None):
        """
        Plot multiple data series on a plot Figure.

        See TkAgg_Plotting.plot_lines() for information on **kwargs.
        """
        plot_lines(
            self.ax, x, y, invert=invert, scale=scale, color=color, marker=marker, weight=weight,
            label=label, linestyle=linestyle, picker=picker)

    def scatter_3d_single(self, x, y, z, color=None, marker=None, label=None):
        """
        Plot 3d scatter plot.

        See TkAgg_Plotting.scatter_3d_single() for information on **kwargs.
        """
        scatter_3d_single(self.ax, x, y, z, color=color, marker=marker, label=label)

    def scatter_3d_multiple(
            self, x_list, y_list, z_list, color=None, marker=None, label=None):
        """
        Plot multiple 3d scatter plot.

        See TkAgg_Plotting.scatter_3d_multiple() for information on **kwargs.
        """
        scatter_3d_multiple(
            self.ax, x_list, y_list, z_list, color=color, marker=marker, label=label)

    def histogram(self, data, bins=None, border=True, color=None, plot_mean=False, toolbar=True):
        """
        Plot histogram.

        See TkAgg_Plotting.plot_histogram() for information on **kwargs.
        """
        plot_histogram(self.ax, data, bins=bins, border=border, color=color, plot_mean=plot_mean)
        if toolbar:
            self.toolbar.update()

    def plot_ellipse(self, covariance_matrix, center=[0, 0], **kwargs):
        """
        Draw ellipse on 2d matplotlib axes.

        See TkAgg_Plotting.plot_ellipse() for information on **kwargs.
        """
        plot_ellipse(self.ax, covariance_matrix, center=center, **kwargs)

    def plot_ellipsoid(self, covariance_matrix, center=[0, 0, 0], subdivisions=10, sigma_mult=2,
                       alpha=0.3, **kwargs):
        """
        Draws sphere or ellipsoid on a 3d matplotlib axes.

        See TkAgg_Plotting.plot_ellipsoid() for information on **kwargs.
        """
        plot_ellipsoid(
            self.ax, covariance_matrix, center=center, subdivisions=subdivisions,
            sigma_mult=sigma_mult, alpha=alpha, **kwargs)

    def set_labels(self, plot_title=None, xlabel=None, ylabel=None, zlabel=None, label_list=None):
        """
        Update plot labels.

        See TkAgg_Plotting.plot_labels() for information on **kwargs.
        """
        plot_title = plot_title if plot_title is not None else self.plot_title.get()
        xlabel = xlabel if xlabel is not None else self.xlabel.get()
        ylabel = ylabel if ylabel is not None else self.ylabel.get()
        zlabel = zlabel if zlabel is not None else self.zlabel.get()

        plot_labels(
            self.ax, title=plot_title, xlabel=xlabel, ylabel=ylabel, zlabel=zlabel,
            label_show=self.label_show.get(), label_list=label_list,
            legend_show=self.legend_show.get(), legend_font=self.legend_font.get(),
            legend_loc=self.legend_loc.get())

    def manual_axis_zoom(self, axis, xmin=None, xmax=None, x_inc=None, ymin=None, ymax=None,
                         y_inc=None, zmin=None, zmax=None, z_inc=None):
        """
        Handles manual axis scaling and sets appropriate tick increments.

        See TkAgg_Plotting.manual_axis_zoom() for information on **kwargs.
        """
        if axis == 'x':
            min = xmin if xmin is not None else self.xmin.get()
            max = xmax if xmax is not None else self.xmax.get()
            ticks = x_inc if x_inc is not None else self.x_inc.get()
        elif axis == 'y':
            min = ymin if ymin is not None else self.ymin.get()
            max = ymax if ymax is not None else self.ymax.get()
            ticks = y_inc if y_inc is not None else self.y_inc.get()
        elif axis == 'z':
            min = zmin if zmin is not None else self.zmin.get()
            max = zmax if zmax is not None else self.zmax.get()
            ticks = z_inc if z_inc is not None else self.z_inc.get()
        manual_axis_zoom(self.ax, axis, min=min, max=max, ticks=ticks)

    def auto_axis_ticks(self, axis):
        """
        Generates tick marks at non-arbitrary spacing when using autoscale.

        See TkAgg_Plotting.auto_axis_ticks() for information on **kwargs.
        """
        auto_axis_ticks(self.ax, axis)

    def zoom(self, xmin=None, xmax=None, ymin=None, ymax=None, x_inc=None, y_inc=None,
             minor_ticks=False):
        """
        Handles zooming, including different combinations of manual and auto zoom on different axes.

        See TkAgg_Plotting.zoom() for information on **kwargs.
        """
        xmin = xmin if xmin is not None else self.xmin.get()
        xmax = xmax if xmax is not None else self.xmax.get()
        ymin = ymin if ymin is not None else self.ymin.get()
        ymax = ymax if ymax is not None else self.ymax.get()
        x_inc = x_inc if x_inc is not None else self.x_inc.get()
        y_inc = y_inc if y_inc is not None else self.y_inc.get()
        mt = minor_ticks if minor_ticks is not None else self.minor_ticks.get()
        zoom(
            self.ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, x_inc=x_inc, y_inc=y_inc,
            minor_ticks=mt)


def plot_labels(
        ax, title=None, xlabel=None, ylabel=None, zlabel=None, label_show=False, label_list=None,
        legend_show=False, legend_list=None, legend_font=None, legend_loc=None):
    """
    Update plot labels.

    When running this method for instance of PlotManager, perform
    plot.canvas.draw() after.

    Parameters:
        ax (mpl.ax object):
            matplotlib Axes object.
        title (str):
            Plot title.
        xlabel (str):
            x-axis label.
        ylabel (str):
            y-axis label.
        zlabel (str):
            z-axis label.
        label_show (bool):
            show label box.
        label_list (list of strings):
            list of items to put in the label box.
        legend_show (bool):
            show legend.
        legend_list (list of strings):
            list of items to put in legend.
        legend_font (int):
            legend font.
        legend_loc (int):
            Location of the legend.
    """
    ax.set_title(title) if title is not None else ax.set_title('Spectrum')
    ax.set_xlabel(xlabel) if xlabel is not None else ax.set_xlabel('Frequency / MHz')
    ax.set_ylabel(ylabel) if ylabel is not None else ax.set_ylabel('Intensity / mV')
    try:
        ax.set_zlabel(zlabel) if zlabel is not None else None
    except AttributeError:
        pass
    legend_dict = {0: "upper right", 1: "lower right", 2: "upper left", 3: "lower left"}
    if label_list:
        if label_show:
            props = dict(boxstyle='round, pad=0.6', facecolor='wheat', alpha=0.75)
            textstr = '\n'.join(label_list)
            ax.text(0.85, 0.95, textstr, transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', bbox=props)
    if legend_show:
        if legend_font is None:
            legend_font = 'Helvetica 10 bold'
        if legend_list is not None:
            if legend_loc is None:
                ax.legend(legend_list, loc="upper right", fontsize=legend_font)
            else:
                ax.legend(legend_list, loc=legend_dict[legend_loc], fontsize=legend_font)
        else:
            if legend_loc is None:
                ax.legend(loc="upper right", fontsize=legend_font)
            else:
                ax.legend(loc=legend_dict[legend_loc], fontsize=legend_font)
    else:
        ax.legend().remove()


def plot_line(ax, x, y, invert=False, scale=None, color=None, marker=None,
              weight=None, label=None, linestyle=None, picker=None):
    """
    Plot a single data series on a plot Figure.

    For an instance of PlotManager, run plot.ax.cla() before running this function. Run
    plot.canvas.draw() and plot.toolbar.update() after running this fuction.

    Parameters:
        ax (matplotlib axes):
            axes object.
        x (list or array):
            x values.
        y (list or array):
            y values.
        invert (bool):
            Invert spectrum if True.
        scale (float):
            scale factor to apply to y-axis.
        color (str):
            color of line.
        marker (str):
            data point marker style. (examples: . , ' o)
        weight (str):
            line weight.
        label (str):
            Label that is displayed in the plot legend.
        linestyle (str):
            Style of line. ex. dashed, solid, etc.
        picker (int):
            Makes the series selectable. Mouse can be this many pixels away from feature and still
            select.
    """
    if type(x) is list:
        x = np.array(x)
    if type(y) is list:
        y = np.array(y)
    if invert:  # Inverts spectrum
        if scale in [None, 1]:  # Inverted but no additional scale factor applied
            scale = -1
            y = y * scale
        else:
            if scale > 0:  # Inverted with positive scale factor
                scale = scale * -1
                y = y * scale
            else:  # Inverted with negative scale factor
                y = y * scale
    else:  # Upright spectrum
        if scale in [None, 1]:  # Upright with no scale factor applied
            y = y
        else:  # Upright with scale factor applied
            if scale > 0:  # Upright with positive scale factor applied
                y = y * scale
            else:
                scale = scale * -1
                y = y * scale
    if len(y) == 1:  # I believe this was necessary for plotting a single point (think omitted point).
        y = [y, y]
    else:
        y = y
    if len(x) == 1:  # I believe this was necessary for plotting a single point (think omitted point).
        x = [x, x]
    else:
        x = x
    color = color_dict[color]
    line2d, = ax.plot(
        x, y, color=color, marker=marker, linewidth=weight, label=label, picker=picker,
        linestyle=linestyle)
    return line2d


def plot_histogram(ax, data, bins=None, border=True, color=None, plot_mean=True):
    """
    Plot histogram with common histogram options.

    When running this method for instance of PlotManager, perform plot.ax.cla()
    before and plot.canvas.draw() as well as
    plot.toolbar.update() after running this method.

    Parameters:
        ax (mpl.ax object):
            matplotlib Axes object.
        data (array):
            One dimension array of data.
        bins (int):
            data is split into this many bins.
        border (bool):
            display bins with a black border.
        color (str):
            fill color of the histogram bins.
        plot_mean (bool):
            Option to plot a dashed line through the histogram at the mean.
    """
    bins = int(bins) if bins is not None else 40
    edgecolor = 'black' if border else None
    ax.hist(data, edgecolor=edgecolor, linewidth=1, color=color_dict[color], bins=bins)
    if data != []:
        mean_ee = float("{0:.5f}".format(np.mean(data)))
    else:
        mean_ee = 0
    if plot_mean:
        ymin, ymax = ax.get_ylim()
        ax.plot([mean_ee, mean_ee], [ymin, ymax + ymax * 0.1], linestyle='dashed',
                color=color_dict['orange'])
    else:
        try:
            ax.fpath([], [])
        except AttributeError:
            pass


def plot_ellipse(ax, covariance_matrix, center=[0, 0, 0], **kwargs):
    """
    Draw ellipse on 2d matplotlib axes.

    For an instance of PlotManager, run plot.ax.cla() before running this function. Run
    plot.canvas.draw() and plot.toolbar.update() after running this fuction.

    Parameters:
        ax (matplotlib axes):
            axes object.
        covariance_matrix (array-like):
            array describing the shape and direction of the ellipse.
        center (list):
            location of ellipse center.
    """
    if covariance_matrix.shape == (2, 2):
        u, s, v = np.linalg.svd(covariance_matrix)
        angle = np.degrees(np.arctan2(u[1, 0], u[0, 0]))
        width, height = 2 * np.sqrt(s)
    else:
        angle = 0
        width, height = 2 * np.sqrt(covariance_matrix)
    for nsig in range(1, 4):
        ellipse = patches.Ellipse(center, width * nsig, height * nsig, angle, **kwargs)
        ellipse.set_clip_box(ax.bbox)
        ax.add_artist(ellipse)
        ax.set_aspect('equal', 'datalim')


def plot_ellipsoid(ax, covariance_matrix, center=[0, 0, 0], subdivisions=10, sigma_mult=2,
                   alpha=0.3, **kwargs):
    """
    Draws sphere or ellipsoid on a 3d matplotlib axes.

    For an instance of PlotManager, run plot.ax.cla() before running this function. Run
    plot.canvas.draw() after running this fuction. running this method.
    Matplotlib toolbar does not work with 3d plot.

    Parameters:
        ax (matplotlib axes):
            axes object.
        center (list):
            ellipsoid center.
        covariance_matrix (array-like):
            array describing the shape and direction of the ellipse.
        subdivisions (int):
            number of subdivisions (subdivision^2 points sampled on the surface).
        sigma_mult (float):
            number of standard deviations for scaling.
        alpha (float):
            opacity of the shape.
    """
    pi = np.pi
    cos = np.cos
    sin = np.sin
    if covariance_matrix.shape == (3, 3):
        eig_vals, eig_vecs = LA.eig(covariance_matrix)

        norms = [np.linalg.norm(eig_vecs[:, 0] * eig_vals[0]),
                 np.linalg.norm(eig_vecs[:, 1] * eig_vals[1]),
                 np.linalg.norm(eig_vecs[:, 2] * eig_vals[2])]

        enum_norms = np.array([[col, x] for col, x in enumerate(norms)])
        sort_norms = enum_norms[(-enum_norms[:, 1]).argsort()]

        pas_1 = eig_vecs[:, int(sort_norms[0, 0])]
        pas_2 = eig_vecs[:, int(sort_norms[1, 0])]
        pas_3 = eig_vecs[:, int(sort_norms[2, 0])]

        norm_1 = np.sqrt(np.linalg.norm(pas_1))
        norm_2 = np.sqrt(np.linalg.norm(pas_2))
        norm_3 = np.sqrt(np.linalg.norm(pas_3))

        a = -1 * np.arctan2(pas_1[1], pas_1[0])
        b = -1 * np.arccos(pas_3[2] / norm_3)
        c = -1 * np.arcsin(pas_1[2] / norm_1)

        pas_1 = pas_1 * eig_vals[int(sort_norms[0, 0])]
        pas_2 = pas_2 * eig_vals[int(sort_norms[1, 0])]
        pas_3 = pas_3 * eig_vals[int(sort_norms[2, 0])]

        rm_00 = (cos(a) * cos(b))
        rm_01 = (cos(a) * sin(b) * sin(c) - sin(a) * cos(c))
        rm_02 = (cos(a) * sin(b) * cos(c) + sin(a) * sin(c))
        rm_10 = (sin(a) * cos(b))
        rm_11 = (sin(a) * sin(b) * sin(c) + cos(a) * cos(c))
        rm_12 = (sin(a) * sin(b) * cos(c) - cos(a) * sin(c))
        rm_20 = (-1 * sin(b))
        rm_21 = (cos(b) * sin(c))
        rm_22 = (cos(b) * cos(c))
        rm = np.array([[rm_00, rm_01, rm_02],
                       [rm_10, rm_11, rm_12],
                       [rm_20, rm_21, rm_22]])

        pas_123 = np.stack((pas_1, pas_2, pas_3))
        down_to_xyz = np.matmul(rm, pas_123)
        norm_x = np.sqrt(LA.norm(down_to_xyz[:, 0]))
        norm_y = np.sqrt(LA.norm(down_to_xyz[:, 1]))
        norm_z = np.sqrt(LA.norm(down_to_xyz[:, 2]))

        phi, theta = np.mgrid[0.0:pi:complex(0, subdivisions),
                     0.0:2.0 * pi:complex(0, subdivisions)]
        x = np.array(sigma_mult * norm_x * sin(phi) * cos(theta)).flatten()
        y = np.array(sigma_mult * norm_y * sin(phi) * sin(theta)).flatten()
        z = np.array(sigma_mult * norm_z * cos(phi)).flatten()
        xyz = np.stack((x, y, z))

        transformed_ellipsoid = xyz
        len_transformed = int(np.sqrt(transformed_ellipsoid.shape[1]))

        x = transformed_ellipsoid[0, :].reshape((len_transformed, len_transformed)) + center[0]
        y = transformed_ellipsoid[1, :].reshape((len_transformed, len_transformed)) + center[1]
        z = transformed_ellipsoid[2, :].reshape((len_transformed, len_transformed)) + center[2]
    ax.plot_surface(x, y, z, alpha=alpha, **kwargs)


def scatter_3d_single(ax, x, y, z, color=None, marker=None, label=None, **kwargs):
    """
    Plot 3-dimensional scatter plot.

    For an instance of PlotManager, run plot.ax.cla() before running this function. Run
    plot.canvas.draw() after running this fuction. running this method.
    Matplotlib toolbar does not work with 3d plot.

    Parameters:
        ax (matplotlib axes):
            axes object.
        x (list or array):
            x values.
        y (list or array):
            y values.
        z (list or array):
            z values.
        color (str):
            color of line.
        marker (str):
            data point marker style. (examples: . , ' o)
        label (str):
            Label that is displayed in the plot legend.
    """
    if type(x) is list:
        x = np.array(x)
    if type(y) is list:
        y = np.array(y)
    if type(z) is list:
        z = np.array(z)
    if marker is None:
        marker = '.'
    color = color_dict[color]
    ax.scatter3D(x, y, z, color=color, marker=marker, linewidth=0, label=label, picker=3, **kwargs)


def scatter_3d_multiple(ax, x, y, z, color=None, marker=None, label=None):
    """
    Plot multiple 3-dimensional data series on a single scatter plot.

    For an instance of PlotManager, run plot.ax.cla() before running this function. Run
    plot.canvas.draw() after running this fuction. running this method.
    Matplotlib toolbar does not work with 3d plot.

    Parameters:
        ax (matplotlib axes):
            axes object.
        x (list or array):
            x values.
        y (list or array):
            y values.
        z (list or array):
            z values.
        color (str):
            color of line.
        marker (str):
            data point marker style. (examples: . , ' o)
        label (str):
            Label that is displayed in the plot legend.
    """
    if color is None:
        color = [None for x in range(len(x))]
    if marker is None:
        marker = [None for x in range(len(x))]
    if label is None:
        label = [None for x in range(len(x))]
    for s in range(len(x)):
        scatter_3d_single(ax, x[s], y[s], z[s], color[s], marker[s], label[s])


def plot_lines(ax, x, y, invert=None, scale=None, color=None, marker=None, weight=None, label=None,
               linestyle=None, picker=None):
    """
    Plot a multiple series on the same plot Figure.

    For an instance of PlotManager, run plot.ax.cla() before running this function. Run
    plot.canvas.draw() and plot.toolbar.update() after running this fuction.

    Parameters:
        ax (matplotlib axes):
            axes object.
        x (list or array of lists):
            x values.
        y (list or array of lists):
            y values.
        invert (list of bools):
            Invert spectrum if True.
        color (str):
            color of line.
        scale (list of floats):
            scale factor to apply to y-axis.
        marker (list of strs):
            data point marker style. (examples: . , ' o)
        weight (list of strs):
            line weight.
        label (list of strs):
            Label that is displayed in the plot legend.
        linestyle (list of strs):
            Style of line. ex. dashed, solid, etc.
        picker (list of ints):
            Makes the series selectable. Mouse can be this many pixels away from feature and still
            select.
    """
    if invert is None:
        invert = [None for x in range(len(x))]
    if scale is None:
        scale = [None for x in range(len(x))]
    if color is None:
        color = [None for x in range(len(x))]
    if marker is None:
        marker = [None for x in range(len(x))]
    if weight is None:
        weight = [None for x in range(len(x))]
    if label is None:
        label = [None for x in range(len(x))]
    if linestyle is None:
        linestyle = [None for x in range(len(x))]
    if picker is None:
        picker = [None for x in range(len(x))]
    for s in range(len(x)):
        plot_line(
            ax, x[s], y[s], invert[s], scale[s], color[s], marker[s], weight[s], label[s],
            linestyle[s], picker[s])


def manual_axis_zoom(ax, axis, min=None, max=None, ticks=None):
    """
    Handles manual axis scaling and sets appropriate tick increments. Runs in
    TkAgg_Plotting.zoom().

    Parameters:
        ax (matplotlib.axes.Axes):
            axes object.
        axis (str):
            'x' or 'y'
        min (float):
            lower bound
        max (float):
            upper bound
        ticks (list):
            accepts 1 or 3 entries. If only one item, set the spacing between ticks. If three items,
            first is the lower bound tick value, second item is the upper bound tick value, and
            third item is the number of total ticks.
    """
    if axis == 'x':
        lim = ax.get_xlim()
    elif axis == 'y':
        lim = ax.get_ylim()
    if min is not None:
        if max is not None:
            if ticks not in [None, 'Auto', ""]:
                ticks = ticks.strip().split(sep=',')
                if len(ticks) > 1:
                    increment = float(ticks[-1])
                    tick_min = float(ticks[0])
                    tick_max = float(ticks[1])
                    num = (tick_max - tick_min) / increment
                    ticks = np.linspace(tick_min, tick_max, num + 1)
                else:
                    num = (float(max) - float(min)) / float(ticks[0])
                    ticks = np.linspace(float(min), float(max), num + 1)
            else:
                ticks = 5
                ticks = np.linspace(float(min), float(max), ticks + 1)
        else:
            min = lim[0]
            max = lim[1]
            ticks = 5
            ticks = np.linspace(float(min), float(max), ticks + 1)
            if ticks in [None, 'Auto', ""]:
                ticks = 5
                ticks = np.linspace(min, max, ticks + 1)
            else:
                ticks = ticks.strip().split(sep=',')
                if len(ticks) > 1:
                    increment = float(ticks[-1])
                    tick_min = float(ticks[0])
                    tick_max = float(ticks[1])
                    num = (tick_max - tick_min) / increment
                    ticks = np.linspace(tick_min, tick_max, num + 1)
                else:
                    num = (float(max) - float(min)) / float(ticks[0])
                    ticks = np.linspace(float(min), float(max), num + 1)
    else:
        min = lim[0]
        max = lim[1]
        if ticks in [None, 'Auto', ""]:
            ticks = 5
            ticks = np.linspace(min, max, ticks + 1)
        else:
            ticks = ticks.strip().split(sep=',')
            if len(ticks) > 1:
                increment = float(ticks[-1])
                tick_min = float(ticks[0])
                tick_max = float(ticks[1])
                num = (tick_max - tick_min) / increment
                ticks = np.linspace(tick_min, tick_max, num + 1)
            else:
                num = (float(max) - float(min)) / float(ticks[0])
                ticks = np.linspace(float(min), float(max), num + 1)
    if axis == 'x':
        ax.set_xticks(ticks)
        ax.set_xlim(float(min), float(max))
    if axis == 'y':
        ax.set_yticks(ticks)
        ax.set_ylim(float(min), float(max))


def auto_axis_ticks(ax, axis):
    """
    Generates tick marks at non-arbitrary spacing when using autoscale.
    Runs in TkAgg_Plotting.zoom().

    Parameters:
        ax (matplotlib.axes.Axes):
            axes object.
        axis (str):
            'x' or 'y'
    """
    accepted_increments = [50000, 250000, 10000,
                           5000, 2000, 1000,
                           500, 250, 100,
                           50, 25, 10,
                           5, 2.5, 1,
                           0.5, 0.25, 0.1,
                           0.05, 0.025, 0.01,
                           0.005, 0.0025, 0.001,
                           0.0005, 0.00025, 0.0001,
                           0.00005, 0.000025, 0.00001,
                           0.000005, 0.0000025, 0.000001,
                           0.0000005, 0.00000025, 0.0000001]
    if axis == 'x':
        lim = ax.get_xlim()
    elif axis == 'y':
        lim = ax.get_ylim()
    delta_lim = lim[1] - lim[0]
    min = lim[0] + ((delta_lim - (10 / 11) * delta_lim) / 2)
    max = lim[1] - ((delta_lim - (10 / 11) * delta_lim) / 2)
    delta = max - min
    min_ticks = 4
    increment_initial = delta / min_ticks

    increment = None
    index = 0
    while increment is None:
        if accepted_increments[index] >= float(increment_initial) >= accepted_increments[index + 1]:
            increment = accepted_increments[index + 1]
            break
        else:
            index += 1
    num_ticks_to_top = abs(math.ceil(max / increment))
    num_ticks_to_bottom = abs(math.floor(min / increment))
    if max > 0 and min >= 0:
        num_ticks = num_ticks_to_top - num_ticks_to_bottom + 1
        bottom_tick = num_ticks_to_bottom * increment
        top_tick = num_ticks_to_top * increment
    elif max > 0 > min:
        num_ticks = num_ticks_to_top + num_ticks_to_bottom + 1
        bottom_tick = -1 * num_ticks_to_bottom * increment
        top_tick = num_ticks_to_top * increment
    elif max <= 0 and min < 0:
        num_ticks = num_ticks_to_bottom - num_ticks_to_top + 1
        bottom_tick = -1 * num_ticks_to_bottom * increment
        top_tick = -1 * num_ticks_to_top * increment
    elif max == 0 and min == 0:
        num_ticks = 0
        bottom_tick = 0
        top_tick = 0
    ticks_auto = np.linspace(bottom_tick, top_tick, num_ticks)
    if axis == 'x':
        ax.set_xticks(ticks_auto)
    elif axis == 'y':
        ax.set_yticks(ticks_auto)


def zoom(ax, xmin='Auto', xmax='Auto', ymin='Auto', ymax='Auto', x_inc=None, y_inc=None,
         minor_ticks=False):
    """
    Handles plot zooming.

    Includes different combinations of manual and auto-scale on different axes.
    Must manually set axes bounds in order to set specific tick values.

    Parameters:
        ax (matplotlib.axes.Axes):
            axes object.
        xmin (str or float):
            Lower x bound.
        xmax (str or float):
            Upper x bound.
        ymin (str or float):
            Lower y bound.
        ymax (str or float):
            Upper y bound.
        x_inc (list):
            Sets ticks in manual_axis_zoom().
        y_inc (list):
            Sets ticks in manual_axis_zoom().
        minor_ticks (bool):
            Turns minor ticks on/off.
    """
    if xmin and xmax == 'Auto':
        if ymin and ymax == 'Auto':
            ax.relim()
            ax.autoscale(enable=True, axis='both', tight=False)
            auto_axis_ticks(ax, 'x')
            auto_axis_ticks(ax, 'y')
        else:
            manual_axis_zoom(ax, axis='y', min=float(ymin), max=float(ymax), ticks=y_inc)
            ax.relim()
            ax.autoscale(enable=True, axis='x', tight=False)
            auto_axis_ticks(ax, 'x')
    else:
        if ymin and ymax == 'Auto':
            manual_axis_zoom(ax, axis='x', min=float(xmin), max=float(xmax), ticks=x_inc)
            ax.relim()
            ax.autoscale(enable=True, axis='y', tight=False)
            auto_axis_ticks(ax, 'y')
        else:
            manual_axis_zoom(ax, axis='x', min=float(xmin), max=float(xmax), ticks=x_inc)
            manual_axis_zoom(ax, axis='y', min=float(ymin), max=float(ymax), ticks=y_inc)
    if minor_ticks:
        ax.minorticks_on()
    else:
        ax.minorticks_off()
