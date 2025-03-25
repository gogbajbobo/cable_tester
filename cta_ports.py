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


def send_data(self: CableTesterApplication, data):
    """Send data to the COM port"""
    if self.serial_connection and self.serial_connection.is_open:
        try:
            # Convert to bytes if it's a string
            if isinstance(data, str):
                data = (data + "\n").encode("utf-8")

            self.serial_connection.write(data)
            self.log(f"Sent: {data}")
        except Exception as e:
            self.log(f"Error sending data: {str(e)}")
