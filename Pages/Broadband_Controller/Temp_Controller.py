"""
Author: Channing West
Changelog: 11/14/2020

"""

import time
from threading import Thread, Event
import tkinter as tk
import tkinter.ttk as ttk
import Instrument_Drivers.Temp_Cont_Driver as temp_driver
import minimalmodbus


# from Instrument_Drivers.Temp_Cont_Driver import connect_all, monitor_all, set_sv_all, pv_sv_tolerance_check


class TempController:
    """
    Generate GUI to control Omega CN7XX temperature controllers.

    Communicate through serial communication using MODBUS protocol.
    Continuous monitoring placed on dedicated thread. Monitoring begins when CONNECT is pressed. 
    A thread is created to periodically check temperature and update GUI. An instance of 
    threading.Event() controls when thread is terminated. While event.clear(), monitoring continues. 
    When event.is_set() is triggered, thread is terminated. See main_controller.py for more info 
    on threading.

    Parameters:
        master (ttk.Frame)
    Attributes:
        self.conn (tk.StringVar):
            Displays connection status
            Default: Closed
        self.sv (tk.StringVar):
            Set point or target temperature
            Units: Celsius
            Default: 40
        self.tolerance (tk.StringVar):
            Max abs(sv - pv) to trigger start when using Automatic Spectrum Collection.
            Units: Celsius
        self.noz1_pv (tk.StringVar):
            Process temperature at nozzle 1 (nozzle closest to receiver antennae).
            Units: Celsius
            Default: searching. . .
        self.noz2_pv (tk.StringVar):
            Process temperature at nozzle 2
            Units: Celsius
            Default: searching. . .
        self.noz3_pv (tk.StringVar):
            Process temperature at nozzle 3
            Units: Celsius
            Default: searching. . .
    Methods:
        connect()
            Connect three temperature controllers. Update GUI.
        monitor(feedback)
            Update PV and SV temperatures on GUI. If feedback=True, PV temperatures are updated
            every 2 seconds on thread.
        set_sv(val)
            Send SV temperature from GUI to temperature controllers.
        pv_sv_tolerance_check(degrees)
            Return True if temp_driver.pv_sv_tolerance_check(degrees) passes.
    BUTTONS
        CONNECT
            Run self.monitor(feedback=True)
        SET
            Run self.set_sv(). Send SV temperature from GUI to temperature controller.
    """
    default = {'connection': 'Closed', 'sv': '40', 'pv': 'searching. . .'}

    def __init__(self, master):
        frame = ttk.Frame(master)
        frame.grid(row=2, column=0, padx=20, pady=3, sticky='nw')

        self.conn = tk.StringVar()
        self.sv = tk.StringVar()
        self.tolerance = tk.StringVar()
        self.noz1_pv = tk.StringVar()
        self.noz2_pv = tk.StringVar()
        self.noz3_pv = tk.StringVar()
        self.conn.set(TempController.default['connection'])
        self.sv.set(TempController.default['sv'])
        self.noz1_pv.set(TempController.default['pv'])
        self.noz2_pv.set(TempController.default['pv'])
        self.noz3_pv.set(TempController.default['pv'])

        self.event = Event()

        temp_label_fmt = {'justify': 'right', 'style': 'h10b.TLabel', 'width': 11, 'anchor': 'e'}
        h14bL_width25 = {'style': 'h14b.TLabel', 'width': 25}
        h10bL_r = {'style': 'h10b.TLabel', 'justify': 'right'}
        h10L_c = {'style': 'h10.TLabel', 'justify': 'center'}
        h8bB_width5 = {'style': 'h8b.TButton', 'width': 5}
        h8bB_width8 = {'style': 'h8b.TButton', 'width': 8}
        x4y3w = {'padx': 4, 'pady': 3, 'sticky': 'w'}
        x4y3 = {'padx': 4, 'pady': 3}
        x4y10ew = {'padx': 4, 'pady': 10, 'sticky': 'ew'}

        tempcont_section_L = ttk.Label(frame, text='Temperature Controllers', **h14bL_width25)
        tempcont_conn_L = ttk.Label(frame, text='Connection', **temp_label_fmt)
        self.conn = ttk.Label(frame, text='Closed', style='red10b.TLabel')
        sep4 = ttk.Separator(frame, orient='horizontal')
        sv_L = ttk.Label(frame, text='Set Point', **temp_label_fmt)
        sv_units = ttk.Label(frame, text='\u00B0C', **h10bL_r)
        sep5 = ttk.Separator(frame, orient='horizontal')
        pv_L_1 = ttk.Label(frame, text='Nozzle 1', **temp_label_fmt)
        pv_units_1 = ttk.Label(frame, text='\u00B0C', **h10bL_r)
        pv_L_2 = ttk.Label(frame, text='Nozzle 2', **temp_label_fmt)
        pv_units_2 = ttk.Label(frame, text='\u00B0C', **h10bL_r)
        pv_L_3 = ttk.Label(frame, text='Nozzle 3', **temp_label_fmt)
        pv_units_3 = ttk.Label(frame, text='\u00B0C', **h10bL_r)
        tempcont_section_L.grid(row=0, column=0, columnspan=3, pady=3, sticky='w')
        tempcont_conn_L.grid(row=1, column=1, **x4y3)
        self.conn.grid(row=1, column=2, **x4y3w)
        sep4.grid(row=2, column=1, columnspan=3, **x4y10ew)
        sv_L.grid(row=3, column=1, **x4y3)
        sv_units.grid(row=3, column=3, **x4y3w)
        sep5.grid(row=6, column=1, columnspan=3, **x4y10ew)
        pv_L_1.grid(row=7, column=1, **x4y3)
        pv_units_1.grid(row=7, column=3, **x4y3w)
        pv_L_2.grid(row=8, column=1, **x4y3)
        pv_units_2.grid(row=8, column=3, **x4y3w)
        pv_L_3.grid(row=9, column=1, **x4y3)
        pv_units_3.grid(row=9, column=3, **x4y3w)

        conn_temp_B = ttk.Button(frame, text='Connect', **h8bB_width8, command=self.monitor)
        sv_CB = ttk.Combobox(frame, textvariable=self.sv, justify='center', width=20)
        sv_CB['values'] = ('20', '30', '40', '50', '60', '70', '80', '90', '100', '110',
                           '120', '130', '140', '150', '160', '170', '180', '190', '200')
        self.noz1_pv_L = ttk.Label(frame, textvariable=self.noz1_pv, **h10L_c)
        self.noz2_pv_L = ttk.Label(frame, textvariable=self.noz2_pv, **h10L_c)
        self.noz3_pv_L = ttk.Label(frame, textvariable=self.noz3_pv, **h10L_c)
        set_temp_B = ttk.Button(frame, text='Set', **h8bB_width5, command=self.set_sv)
        conn_temp_B.grid(row=1, column=0, **x4y3w)
        sv_CB.grid(row=3, column=2, **x4y3)
        set_temp_B.grid(row=3, column=0, **x4y3w)
        self.noz1_pv_L.grid(row=7, column=2, **x4y3)
        self.noz2_pv_L.grid(row=8, column=2, **x4y3)
        self.noz3_pv_L.grid(row=9, column=2, **x4y3)

    def connect(self):
        """ 
        Connect three temperature controllers. Update GUI. Return three TemperatureController 
        instances. 
        """
        # todo find error type and implement try/except
        try:
            tc1, tc2, tc3 = temp_driver.connect_all()
            self.conn.configure(
                text='Connected', foreground='green3', font=('Helvetica', '10', 'bold'))
            return tc1, tc2, tc3
        except minimalmodbus.NoResponeError:
            self.conn.configure(
                text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))

    def monitor(self, feedback=True):
        """
        Update PV and SV temperatures on GUI. If feedback=True, PV temperatures are updated 
        every 2 seconds on thread.

        Parameters:
            feedback (bool):
                If true, PV temperatures are queried continually.
                If false, PV temperatures are queried once.
        """
        self.event.clear()

        def thread_func():
            while not self.event.is_set():
                time.sleep(2)
                pv, sv = temp_driver.monitor_all()
                self.noz1_pv.set(pv[0])
                self.noz2_pv.set(pv[1])
                self.noz3_pv.set(pv[2])
            self.conn.configure(
                text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))
            self.noz1_pv.set(TempController.default['pv'])
            self.noz2_pv.set(TempController.default['pv'])
            self.noz3_pv.set(TempController.default['pv'])
        try:
            pv, sv = temp_driver.monitor_all()
            self.conn.configure(
                text='Connected', foreground='green3', font=('Helvetica', '10', 'bold'))
            if int(sv[0]) == int(sv[1]) == int(sv[2]):
                self.sv.set(int(sv[0]))
            else:
                self.sv.set(str(sv))
            self.noz1_pv.set(pv[0])
            self.noz2_pv.set(pv[1])
            self.noz3_pv.set(pv[2])
            if feedback:
                t = Thread(name='temp monitor', target=thread_func)
                t.start()
        except minimalmodbus.NoResponseError:
            self.conn.configure(
                text='Disconnected', foreground='red', font=('Helvetica', '10', 'bold'))

    def set_sv(self, val=None):
        """ Send SV temperature from GUI to temperature controllers. """
        self.event.set()
        if val is None:
            val = int(self.sv.get())
        temp_driver.set_sv_all(val)

    def pv_sv_tolerance_check(self, degrees):
        """ Return True if temp_driver.pv_sv_tolerance_check(degrees) passes. """
        check = temp_driver.pv_sv_tolerance_check(degrees)
        return check
