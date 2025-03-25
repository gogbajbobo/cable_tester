import serial
import serial.tools.list_ports

from app import CableTesterApplication


def update_ports_list(self: CableTesterApplication):
    """Update the list of available COM ports"""
    self.log("Updating COM ports list")

    ports = [port.device for port in serial.tools.list_ports.comports()]
    self.ports_combobox["values"] = ports

    if ports:
        self.ports_combobox.current(0)
        self.log(f"Found {len(ports)} COM ports")
    else:
        self.log("No COM ports found")
