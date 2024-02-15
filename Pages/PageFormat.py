"""
Author: Channing West
Changelog: 12/5/2019

"""

import numpy as np
import tkinter as tk
from tkinter import ttk
import os
from tkinter.filedialog import asksaveasfilename, askopenfilename, \
    askopenfilenames, askdirectory
import pickle
import re
import gc

ftype_dict = {None: [('All Files', '*.*')],
              'ft': [('FT Files', '*.ft'), ('All Files', '*.*')],
              '.ft': [('FT Files', '*.ft'), ('All Files', '*.*')],
              '.txt': [('TXT Files', '*.txt'), ('All Files', '*.*')],
              'txt': [('TXT Files', '*.txt'), ('All Files', '*.*')],
              '.prn': [('PRN Files', '*.prn'), ('All Files', '*.*')],
              'prn': [('PRN Files', '*.prn'), ('All Files', '*.*')],
              '.par': [('PAR Files', '*.par'), ('All Files', '*.*')],
              'par': [('PAR Files', '*.par'), ('All Files', '*.*')],
              '.pi': [('PI Files', '*.pi'), ('All Files', '*.*')],
              'pi': [('PI Files', '*.pi'), ('All Files', '*.*')],
              '.var': [('VAR Files', '*.var'), ('All Files', '*.*')],
              'var': [('VAR Files', '*.var'), ('All Files', '*.*')],
              '.cat': [('CAT Files', '*.cat'), ('All Files', '*.*')],
              'cat': [('CAT Files', '*.cat'), ('All Files', '*.*')],
              'int': [('INT Files', '*.int'), ('All Files', '*.*')],
              '.int': [('INT Files', '*.int'), ('All Files', '*.*')],
              'lin': [('LIN Files', '*.lin'), ('All Files', '*.*')],
              '.lin': [('LIN Files', '*.lin'), ('All Files', '*.*')],
              '.out': [('OUT Files', '*.out'), ('All Files', '*.*')],
              'out': [('OUT Files', '*.out'), ('All Files', '*.*')],
              '.log': [('LOG Files', '*.log'), ('All Files', '*.*')],
              'log': [('LOG Files', '*.log'), ('All Files', '*.*')],
              '.in': [('IN Files', '*.in'), ('All Files', '*.*')],
              'in': [('IN Files', '*.in'), ('All Files', '*.*')],
              'in_': [('IN Files', '*.in'), ('All Files', '*.*')],
              '.gjf': [('GJF Files', '*.gjf'), ('All Files', '*.*')],
              'gjf': [('GJF Files', '*.gjf'), ('All Files', '*.*')],
              'pickle': [('Pickle Files', '*.pickle'), ('All Files', '*.*')],
              'csv': [('CSV Files', '*.csv'), ('All Files', '*.*')],
              'tex': [('TEX Files', '*.tex'), ('All Files', '*.*')],
              '.tex': [('TEX Files', '*.tex'), ('All Files', '*.*')],
              'spec': [('FT Files', '*.ft'), ('TXT Files', '*.txt'),
                       ('PRN Files', '*.prn'), ('All Files', '*.*')],
              'pickett': [('All Files', '*.*'), ('PAR Files', '*.par'),
                          ('VAR Files', '*.var'), ('CAT Files', '*.cat'),
                          ('INT Files', '*.int'), ('LIN Files', '*.lin')],
              'gaussian': [('All Files', '*.*'), ('GJF Files', '*.gjf'),
                           ('OUT Files', '*.out'), ('LOG Files', '*.log')],
              'out_log': [('OUT Files', '*.out'), ('LOG Files', '*.log'),
                          ('All Files', '*.*')],
              'dipole': [('All Files', '*.*'), ('OUT Files', '*.out'),
                         ('LOG Files', '*.log'), ('INT Files', '*.int')],
              'rigidrotor': [('All Files', '*.*'), ('PI Files', '*pi'),
                             ('PAR Files', '*.par'), ('VAR Files', '*.var'),
                             ('IN Files', '*.in'), ('OUT Files', '*.out'),
                             ('LOG Files', '*.log')],
              'qdc': [('All Files', '*.*'), ('PAR Files', '*.par'),
                      ('VAR Files', '*.var'), ('PI Files', '*.pi'),
                      ('IN Files', '*.in')],
              'quick_import': [('All Files', '*.*'), ('PAR Files', '*.par'),
                               ('VAR Files', '*.var'), ('PI Files', '*.pi')],
              'ft_cat_prn': [('All Files', '*.*'), ('FT Files', '*.ft'),
                             ('CAT Files', '*.cat'), ('PRN Files', '*.prn')],
              'all': [('All Files', '*.*')]}


class PageFormat(ttk.Frame):
    """
    Set up GUI pages.

    Pressable GUI BUTTONS in caps
    NAVIGATION BAR (Found below plots):
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
    SAVE
        Save values from entry boxes, radiobuttons, check boxes, notes, omitted
        points in *.pickle file. Easily reproduce previous calculations.
        However, calculation outputs are not save in *.pickle files, in order to
        reduce file size. Therefore, to plot any outputs, calculations must to
        performed again.
    LOAD
        Load previously saved values for entry boxes, radiobuttons, check boxes,
        notes, omitted points from *.pickle. Easily reproduce previous
        calculations. However, calculation outputs are not save in *.pickle
        files. Calculations must to performed again to plot results.
    DEFAULTS
        Restore entry boxes, radiobuttons, check boxes, notes, omitted points to
        their default values.
    BACK TO NAVIGATOR
        Go back to page navigator that is displayed at the program startup.
    EXIT APPLICATION
        Close program.

    Parameters:
        master (ttk.Frame):
            All program pages stacked in this frame. Visible frame is raised to top.
        controller (Broadband MRR Toolbox.RotSpec):
            Creates instance of tk.TK().
    Attributes:
        self.canvas (tk.Canvas):
            Governs window size. self.frame is placed in self.canvas.
        self.frame (ttk.Frame):
            Widgets placed in self.frame. Can be larger than self.canvas. Scrollable.
        self.combobox:
            Instance of ttk.Combobox. Can be used to declare class-wide combo box bindings/stylings.
        self.textbox (tk.Text):
            Used to declare class-wide text box bindings/stylings.
    Methods:
        canvas_configure()
            Set scroll region to self.canvas when configure event occurs.
        scroll_canvas(event)
            Set scroll speed for self.canvas.
        scroll_textbox(event, tb)
            Set scroll speed for tk.Text object.
        left_click()
            Bind mouse wheel scrolling to tk.canvas object when left click in tk.Frame.
        unbind_combo_scroll(cb)
            Remove mouse wheel binding from combo box options when combobox is
            not expanded. Avoids accidental change.
        lose_focus(widget)
            Remove mouse wheel binding from all widgets.
        bind_enter_combobox(cb)
            Remove mouse wheel binding from self.canvas when combobox is
            expanded.
        bind_enter_textbox(tb)
            Remove mouse wheel binding from self.canvas when mouse enters a
            tk.Text widget.
        bind_exit_textbox(tb)
            Bind mouse wheel to self.canvas when mouse exits a tk.Text widget.
        save_temp_file(fname, array):
            Save numpy array to a *.npy binary file to temporarily store data
            during a multistep calculation.
        load_temp_file(fname)
            Load numpy array from *.npy binary file to continue calculation
            from intermediate point.
    """

    def __init__(self, master, controller):
        self.controller = controller
        width = controller.width - 25
        height = controller.height - 60
        scroll_canvas = tk.Canvas(master, width=width, height=height, borderwidth=0, bg='#f6f4f2')
        self.canvas = tk.Canvas(scroll_canvas, width=width, height=height, borderwidth=0,
                                bg='#f6f4f2')
        self.frame = ttk.Frame(self.canvas, width=width, height=height, borderwidth=0)
        self.combobox = ttk.Combobox(self.frame)
        self.textbox = tk.Text(self.frame)
        vsb = ttk.Scrollbar(scroll_canvas, orient="vertical", command=self.canvas.yview)
        hsb = ttk.Scrollbar(scroll_canvas, orient="horizontal", command=self.canvas.xview)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.configure(xscrollcommand=hsb.set)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        frame_B = ttk.Frame(scroll_canvas)
        frame_B.pack(side="bottom", fill="x")

        self.style = ttk.Style()
        self.style.configure("h8b.TButton", font=('Helvetica', '8', 'bold'))
        self.style.configure("h8.TButton", font=('Helvetica', '8'))
        self.style.configure("h10b.TButton", font=('Helvetica', '10', 'bold'))
        self.style.configure("h12b.TButton", font=('Helvetica', '12', 'bold'))
        self.style.configure("h14b.TButton", font=('Helvetica', '14', 'bold'))
        self.style.map('h10b.TButton', foreground=[('active', 'blue')])
        self.style.map('h12b.TButton', foreground=[('active', 'blue')])
        self.style.map('h14b.TButton', foreground=[('active', 'blue')])
        self.style.configure(
            "warning.TLabel", foreground='red', wraplength=325, font=('Helvetica', '8', 'bold'))
        self.style.configure("red10b.TLabel", foreground='red', font=('Helvetica', '10', 'bold'))
        self.style.configure("h8b.TLabel", font=('Helvetica', '8', 'bold'))
        self.style.configure("h8.TLabel", font=('Helvetica', '8'))
        self.style.configure("h10b.TLabel", font=('Helvetica', '10', 'bold'))
        self.style.configure("h10bu.TLabel", font=('Helvetica', '10', 'bold', 'underline'))
        self.style.configure("h12b.TLabel", font=('Helvetica', '12', 'bold'))
        self.style.configure("h12bu.TLabel", font=('Helvetica', '12', 'bold', 'underline'))
        self.style.configure("h14b.TLabel", font=('Helvetica', '14', 'bold'))
        self.style.configure("h20b.TLabel", font=('Helvetica', '20', 'bold'))
        self.style.configure("h10.TLabel", font=('Helvetica', '10'))
        self.style.configure("h8.TRadiobutton", font=('Helvetica', '8'))
        self.style.configure("h10b.TRadiobutton", font=('Helvetica', '10', 'bold'))
        self.style.configure("TMenubutton", font=('Helvetica', '8'))

        nav_B = ttk.Button(
            frame_B, text="Back to Navigator", style='h10b.TButton', command=controller.show_nav)
        exit_B = ttk.Button(
            frame_B, text="Exit Application", style='h10b.TButton', command=controller.client_exit)
        settings_B = ttk.Button(
            frame_B, text="Settings", style='h10b.TButton', command=controller.show_settings)
        help_B = ttk.Button(
            frame_B, textvariable=controller.help_str, style='h10b.TButton',
            command=controller.show_help)
        exit_B.pack(side="right", fill="x", expand=True)
        settings_B.pack(side="right", fill="x", expand=True)
        help_B.pack(side="right", fill="x", expand=True)
        nav_B.pack(side="left", fill="x", expand=True)
        scroll_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda event: self.canvas_configure())

    def canvas_configure(self):
        """ Set scroll region to the entire page. """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def scroll_canvas(self):
        """ Bind mouse wheel scrolling to a tk.canvas object. """
        canvas_scroll(self.canvas)

    def scroll_textbox(self, tb):
        """
        Bind mouse wheel scrolling to tb when mouse enters tk.Text.

        Parameters:
            tb (tk.Text)
        """
        enter_textbox_scroll
        self.canvas.bind_all("<MouseWheel>", lambda event: scroll(event, tb))

    def left_click(self):
        """ Bind scrolling to tk.canvas object on left click in tk.Frame. """
        self.frame.bind("<Button-1>", lambda event: self.scroll_canvas())

    def open_combobox(self, cb):
        """
        Remove scrolling from self.canvas when ttk.Combobox is expanded.

        Parameters:
            cb (ttk.Combobox):
        """
        cb.bind('<FocusIn>', lambda event: lose_focus(self.canvas))

    def enter_textbox(self, tb):
        """
        Remove scrolling from self.canvas when mouse enters tk.Text.

        Parameters:
            tb (tk.Text):
        """
        def inner(tb):
            lose_focus(self.canvas)
            self.scroll_textbox(tb)

        tb.bind('<Enter>', lambda event: inner(tb))

    def exit_textbox(self, tb):
        """
        Bind scrolling to self.canvas when mouse exits tk.Text.

        Parameters:
            tb (tk.Text):
        """
        def inner(tb):
            lose_focus(tb)
            self.scroll_canvas()

        tb.bind('<Leave>', lambda event: inner(tb))

    def save_temp_file(self, fname, array):
        """
        Save np.array to *.npy file to store data during multistep calculation.

        Save/Load temporary file to split multistep operations into smaller operations, allowing
        data to be checked and filtered at intermediate spots. Temporary files are saved in the
        'temp' subdirectory.

        Parameters:
            fname (str):
                File name. Saved to 'temp' subdirectory with *.npy extension.
            array (array):
        """
        parent_dir = self.controller.dir
        if os.path.isdir(os.path.join(parent_dir, 'temp')):
            os.chdir(os.path.join(parent_dir, 'temp'))
        else:
            os.mkdir(os.path.join(parent_dir, 'temp'))
            os.chdir(os.path.join(parent_dir, 'temp'))
        np.save(fname, array)

    def load_temp_file(self, fname):
        """
        Load *.npy file to continue calculation from intermediate point.

        Save/Load temporary file to split multistep operations into smaller operations, allowing
        data to be checked and filtered at intermediate spots. Temporary files are saved to the
        'temp' subdirectory.

        Parameters:
            fname (str):
                File name. Saved as *.npy to 'temp' subdir.
        Returns:
            array (array):
        """
        parent_dir = self.controller.dir
        os.chdir(os.path.join(parent_dir, 'temp'))
        array = np.load(fname)
        return array


def mpl_click(event, freq_var, intensity_var):
    """
    When mpl.plot data point is clicked, coordinates are relayed to freq_var and intensity_var.

    All tools on NAVIGATION BAR must be unselected to select data. More than one data point might
    be selected depending on point spacing and picker setting. All selected points are in freq_var
    and intensity_var. This is accomplished by generating lists of strings containing all the data
    points. after the list is made, the tk.vars are set.

    Parameters:
        event:
            event.mouseevent.button == 1
        freq_var (tk.StringVar):
            Holds x coordinates of selected data points.
        intensity_var (tk.StringVar):
            Holds y coordinates of selected data points.
    Return:
        event.artist:
            matplotlib data series that was clicked.
        points (tuple):
            coordinates of selected points
    """
    if event.mouseevent.button == 1:
        line = event.artist
        xdata, ydata = line.get_data()
        ind = event.ind
        points = tuple(zip(xdata[ind], ydata[ind]))
        freqs = ["{:.4f}".format(point[0]) for point in points]
        intens = ["{:.5f}".format(point[1]) for point in points]
        intensity_var.set(intens)
        freq_var.set(freqs)
        return event.artist, points
    else:
        pass


def scroll(event, widget):
    """
    Set scroll speed for widget.

    Parameters:
        event (event):
        widget (tk widget):
            Ex. tk.Canvas, tk.Text, ttk.Combobox
    """
    widget.yview_scroll(int(-1 * (event.delta / 90)), "units")


def canvas_scroll(canvas):
    """ Set scroll speed for canvas. """
    canvas.bind_all("<MouseWheel>", lambda event: scroll(event, canvas))


def enter_textbox_scroll(textbox):
    """ Set scroll speed for textbox. """
    textbox.bind_all("<MouseWheel>", lambda event: scroll(event, textbox))


def lose_focus(widget):
    """ Remove mouse wheel binding from all widgets. """
    widget.unbind_all("<MouseWheel>")


def unbind_combo_scroll(cb):
    """
    Remove scrolling for tk.Combobox options when cb is not expanded.

    Prevents accidental scrolling through options when scrolling self.canvas.

    Parameters:
        cb (ttk.Combobox):
    """
    cb.unbind_class("TCombobox", "<MouseWheel>")


def format_omitted_points(omit_tk_var):
    """
    Return omit_tk_var formatted as a list of floats.

    Parameters:
        omit_tk_var (tk.StringVar):
            tk.StringVar that holds frequencies that should be omitted from a calculation.
    Return:
        points (list of floats):
            List of frequencies represented as floats.
    """
    points = omit_tk_var.get()
    replace = ['(', ')', '[', ']', ',', '"', "'"]
    for r in replace:
        points = points.replace(r, '')
    points = points.split()
    points = [float(x) for x in points]
    return points


def selected_point(func, omit_tk_var, freq_tk_var):
    """
    Add point, remove point, or clear omit_tk_var list.

    freq_tk_var should display freqency to add or remove that point.

    Parameters:
        func (str):
            Reset, omit, or undo.
        omit_tk_var (tk.StringVar):
            Line posiitons omitted.
        freq_tk_var (tk.StringVar):
            Holds currently selected frequencies.
    """
    if func == 'reset':
        omit_tk_var.set('[]')  # todo check if this works
    else:
        freqs = freq_tk_var.get()
        replace = ['(', ')', ',', '"', "'"]
        for r in replace:
            freqs = freqs.replace(r, '')
        freqs = freqs.split()
        freqs = [float(freq) for freq in freqs]

        omitted_points = format_omitted_points(omit_tk_var)
        if func == 'omit':
            for freq in freqs:
                omitted_points.append(float("{0:.4f}".format(freq)))
                omit_tk_var.set(omitted_points)
        if func == 'undo':
            for freq in freqs:
                del omitted_points[omitted_points.index(freq)]
                omit_tk_var.set(omitted_points)


def save_file(initialfile=None, ftype=None, initialdir=None, defaultextension=None):
    """
    Open Save As file explorer and return file path given.

    Parameters:
        initialfile (str):
            Initial proposed file name.
            Default: None
        ftype (str):
            Any key value from ftype_dict.
            Default: None
        initialdir (str):
            Path to directory that is opened.
            Default: None
        defaultextension (str):
            Proposed file extension.
            Default: None
    Return:
        filename (str):             File path of saved file.
    """
    ftype = ftype_dict[ftype]

    if initialdir is None:
        os.chdir(os.path.curdir)
    else:
        os.chdir(initialdir)

    filename = asksaveasfilename(initialfile=initialfile, filetypes=ftype,
                                 defaultextension=defaultextension)
    return filename


def save_page(attr_dict, textbox_dict):
    """
    Save values from entry boxes, radiobuttons, check boxes, notes,
    omitted points.

    Easily reproduce previous calculations. However, results are
    not saved in *.pickle files. Calculations must be performed again to
    plot results.

    Parameters:
        attr_dict (dict):
            Dictionary of all page attributes (entry boxes, radiobuttons, etc.)
        textbox_dict (dict):
            Dictionary of items from tk.Text widgets.
    Return:
        attribute_get_dict (attributes):
            Contains extracted tk variables (strings, integers, floats, etc.).
        fname (str):
            File name.
    """
    attribute_get_dict = {}
    for key, val in attr_dict.items():
        try:
            attribute_get_dict[key] = val.get()
        except AttributeError:
            attribute_get_dict[key] = val
        except KeyError:
            pass
    for key, val in textbox_dict.items():
        attribute_get_dict[key] = val.get("1.0", "end-1c")

    fname = save_file(ftype='all')
    fname = os.path.splitext(fname)[0]
    if fname:
        with open(fname + '.pickle', 'wb') as f:
            pickle.dump(attribute_get_dict, f, pickle.HIGHEST_PROTOCOL)
        return attribute_get_dict, fname


def clear_page(default_dict, attr_dict, *plots, textbox_dict=None):
    """
    Restore page to default state.

    Parameters:
        default_dict (dict):
            Dictionary with defaults of page attributes.
        attr_dict (dict):
            Dictionary of current values of page attributes.
        *plots:
            Instances of TkAgg_Plotting.PlotManager().
        textbox_dict (dict):
            {tk.Text instance: text}
            Default: None
    """
    for key, val in attr_dict.items():
        try:
            val.set(default_dict[key])
        except AttributeError:
            pass
    if textbox_dict:
        for key, val in textbox_dict.items():
            textbox_dict[key].delete('1.0', tk.END)
            textbox_dict[key].insert('1.0', 'None')
    try:
        for plot in plots:
            plot.ax.cla()
            plot.set_labels()
            plot.canvas.draw()
    except AttributeError:
        pass


def open_file(title=None, ftype=None, initialdir=None):
    """
    Open file explorer and return file name if a file is selected.

    Parameters:
        title (str):
            Title that appears at the top of file explorer.
        ftype (str):
            Any of the key values from ftype_dict.
        initialdir (str):
            Directory that is opened when file explorer opened.
    Return
        filename (str):
            File path.
    """
    ftype = ftype_dict[ftype]
    if initialdir is None:
        os.chdir(os.path.curdir)
    else:
        os.chdir(initialdir)
    if title is None:
        title = 'Select a file'
    filename = askopenfilename(title=title, filetypes=ftype)
    if filename == '':
        return
    else:
        return filename


def load_page(attr_dict, *locks, tb_dict=None, eb_var=None):
    """
    Load *.pickle file from previos calculation.
    *.pickle file contains values from entry boxes, radiobuttons, check boxes,
    notes, and omitted points. Easily reproduce previous calculations. However,
    calculation outputs are not saved in *.pickle files. Calculations must to
    performed again to plot results.

    Parameters:
        attr_dict (dict):
            dictionary of page attributes.
        *locks (tk.IntVar):
            1 is locked. 0 is unlocked. Add locks to ensure calculations are done in correct order.
            Add lock for every page section where temporary files are saved. Without locks, if the
            user skips to the last step of the calculation, the temporary files used to compute the
            last step will not reflect the intended data set.
        tb_dict (dict):
            Dictionary of items from tk.Text widgets.
            Default: None
        eb_var (list of ttk.Entry):
            Provide eb_var to display the right most text when path is displayed.
            Default: None
    """
    filename = open_file(ftype='pickle')
    if filename:
        with open(filename, 'rb') as f:
            new_dict = pickle.load(f, encoding='bytes')
        for key, val in new_dict.items():
            try:
                if key == 'omitted_points':
                    val = str(val)
                attr_dict[key].set(new_dict[key])
            except KeyError:
                try:
                    tb_dict[key].delete('1.0', tk.END)
                    tb_dict[key].insert('1.0', val)
                except (TypeError, KeyError) as error:
                    pass
            except AttributeError:
                attr_dict[key] = val
        for lock in locks:
            lock.set(1)
        if eb_var is None:
            eb_var = []
        for eb in eb_var:
            eb.after(1, eb.xview_moveto, 1)


def write_path(tk_var, eb_var=None, ftype=None):
    """
    Set tk_var to single file path. Use to upload a single file path to an entry box.

    Parameters:
        tk_var (tk.StringVar):
        eb_var (ttk.Entry):
            Provide eb_var to display the right most text when path is displayed.
            Default: None
        ftype (str):
            Key value from ftype_dict.
            Default: None
    """
    ftype = ftype_dict[ftype]
    filename = askopenfilename(filetypes=ftype)
    if filename == '':
        return
    file_path = str(os.path.abspath(filename))
    tk_var.set(file_path)
    if eb_var is not None:
        eb_var.after(1, eb_var.xview_moveto, 1)


def write_paths(tk_var, eb_var=None, ftype=None):
    """
    Set tk_var to list of file paths. Use to upload multiple file paths to a single entry box.

    Parameters:
        tk_var (tk.StringVar):
        eb_var (ttk.Entry):
            Provide eb_var to display the right most text when path is displayed.
            Default: None
        ftype (str):
            Key value from ftype_dict.
    """
    ftype = ftype_dict[ftype]
    filenames = askopenfilenames(title='Select files', filetypes=ftype)
    if filenames == '':
        return
    files_list = str(filenames)
    tk_var.set(files_list)
    if eb_var is not None:
        eb_var.after(1, eb_var.xview_moveto, 1)


def write_directory(entrybox):
    """
    Set entrybox to file directory path.

    Parameters:
        entrybox (ttk.Entry):
    """
    dirname = askdirectory(title='Select directory')
    if dirname:
        entrybox.delete(0, tk.END)
        entrybox.insert(0, dirname)
        entrybox.after(1, entrybox.xview_moveto, 1)


def list_paths(var):
    """
    Return a list of file paths held in a tk.StringVar.

    Parameters:
        var (tk.StringVar):
            File name(s).
    Return:
        paths (list of str):
            File name(s).
    """
    paths = var.get()
    paths = re.sub(r"\A\(", '', paths)
    paths = re.sub(r"'*", '', paths)
    paths = re.sub(r'\)\Z', '', paths)
    paths = paths.rstrip(',').split(', ')
    return paths


def dir_manager(dstdir, parent_dir):
    """ Check for parent_dir/dstdir. Create pickett_dir if DNE. Change CWD to dstdir"""
    path = os.path.join(parent_dir, dstdir)
    dir_check = os.path.isdir(path)
    if not dir_check:
        os.makedirs(path)
    os.chdir(path)
