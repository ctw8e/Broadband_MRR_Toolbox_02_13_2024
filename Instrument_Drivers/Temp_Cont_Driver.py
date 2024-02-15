"""
Author: Channing West
Changelog: 5/18/2022
"""

import minimalmodbus

PORT = 'COM3'
BAUDRATE = 9600
PARITY = 'E'
BYTESIZE = 7
STOPBITS = 1
TIMEOUT = 0.2


class TemperatureController:
    """
    Control Omega CN7XX temperature controllers by serial connection using the MODBUS protocol.

    Controller settings can be accessed on the physical controller as well as on the Omega
    desktop application.

    Parameters:
        slaveaddress (int):
            Slave address of individual controller.
        port (str):
            Serial port address of the PC controller. Port name of the usb port the controllers are
            connected to. Port identity can be found from PC device manager.
            Default: None
        baudrate (int):
            Baud rate setting of the temperature controller and COM port.
            Default: None
        parity (str):
            Parity bit setting.
            Default: None
        bytesize (int):
            Data length setting.
            Default: None
        stopbits (int):
            Stop bit setting.
            Default: None
        timeout (float):
            Communication timeout setting.
            Units: seconds
            Default: None
    Attributes:
        self.slaveaddress (int):
            Slave address of individual controller.
        self.port (str):
            Serial port address of the PC controller. Port name of the usb port the controllers are
            connected to. Port identity can be found from PC device manager.
            Default: 'COM3'
        self.baudrate (int):
            Baud rate setting of the temperature controller and COM port.
            Default: 9600
        self.parity (str):
            Parity bit setting.
            Default: 'E'
        self.bytesize (int):
            Data length setting.
            Default: 7
        self.stopbits (int):
            Stop bit setting.
            Default: 1
        self.timeout (float):
            Communication timeout setting.
            Units: seconds
            Default: 0.2
        self.heater:
            Instance of minimalmodbus.Instrument.
    Methods:
        read_process_value()
            Return current nozzle temperature.
        write_setpoint_value(temp)
            Set controller target temperature to temp.
            Units: Celsius
        read_setpoint_value()
            Return target temperature.
            Units: Celsius
    """
    def __init__(self, slaveaddress, port=None, baudrate=None, parity=None, bytesize=None,
                 stopbits=None, timeout=None):
        self.slaveaddress = slaveaddress
        self.port = PORT if port is None else port
        self.baudrate = BAUDRATE if baudrate is None else baudrate
        self.parity = PARITY if parity is None else parity
        self.bytesize = BYTESIZE if bytesize is None else bytesize
        self.stopbits = STOPBITS if stopbits is None else stopbits
        self.timeout = TIMEOUT if timeout is None else timeout

        self.heater = minimalmodbus.Instrument(
            self.port, self.slaveaddress, minimalmodbus.MODE_ASCII)
        self.heater.serial.baudrate = self.baudrate
        self.heater.serial.parity = self.parity
        self.heater.serial.bytesize = self.bytesize
        self.heater.serial.stopbits = self.stopbits
        self.heater.serial.timeout = self.timeout

    def read_process_value(self):
        """ Returns current nozzle temperature. Units: Celsius """
        PV = self.heater.read_register(0x4700, 1)
        return PV

    def write_setpoint_value(self, temp):
        """ Set target temperature to temp. Units: Celsius """
        self.heater.write_register(0x4701, temp, 1, functioncode=6)

    def read_setpoint_value(self):
        """ Return target temperature. Units: Celsius """
        SV = self.heater.read_register(0x4701, 1)
        return SV


def connect_all(*args):
    """
    Connect to three Omega CN710 temperature controllers.

    Parameters:
        *args (int):
            slave addresses of temperature controllers.
    Returns:
        controllers (list of TemperatureController objects):
    """
    # todo May need to change addresses since changing temp controllers to external relays.
    controllers = []
    for arg in args:
        cont = TemperatureController(arg)
        controllers.append(cont)
    return controllers


def monitor_all(*args):
    """
    Return process and set point temperatures for all controllers.

    Parameters:
        *args (int):
            slave addresses of temperature controllers.
    Returns:
        pv (list of floats):
            Current nozzle temperatures.
            Units: Celsius
        sv (list of floats):
            Set point temperatures.
            Units: Celsius
    """
    controllers = connect_all(*args)

    pv = []
    sv = []

    for x in controllers:
        y = x.read_process_value()
        z = x.read_setpoint_value()
        pv.append(y)
        sv.append(z)
    return pv, sv


def set_sv_all(temp, *args):
    """
    Change set point temperature for all controllers.

    Parameters:
        temp (int):
            temperature. Units: Celsius.
        *args (ints):
            slave addresses
    """
    controllers = connect_all(*args)

    for x in controllers:
        x.write_setpoint_value(temp)


def pv_sv_tolerance_check(tolerance, *args):
    """
    Compare PV from controllers with SV. If PV > (SV - tolerance), return true.

    Parameters:
        tolerance (int):
            degrees below set point temperature that nozzle temperature must be before data
            collection begins.
            Units: Celsius
        *args (ints):
            slave addresses
    Returns:
        tolerance_test (bool):
            True if all nozzles are within accepted range to begin measurement.
            False if any nozzles are not within accepted range to begin measurement.
    """
    controllers = connect_all(*args)

    tolerance_test = True
    for x in controllers:
        sv = float(x.read_setpoint_value())
        pv = float(x.read_process_value())

        if pv >= (sv - tolerance):
            continue
        else:
            tolerance_test = False
            break
    return tolerance_test


# one, two, three = connect_all()
# c1 = TemperatureController(3)
# c2 = TemperatureController(4)
# c3 = TemperatureController(5)
#
# sv = c1.write_setpoint_value(20)
# print(sv)

