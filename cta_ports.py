import serial
import serial.tools.list_ports

from app import CableTesterApplication, COM_STATE
import cta_tables
import cta_process
import cta_left_frame


def update_ports_list(self: CableTesterApplication):
    """Update the list of available COM ports"""
    self.log("Updating COM ports list")

    ports = [port.device for port in serial.tools.list_ports.comports()]
    self.ports_combobox["values"] = ports

    if ports:
        self.ports_combobox.current(0)
        self.log_info(f"Found {len(ports)} COM ports")
    else:
        self.selected_port.set("")
        self.log_error("No COM ports found")

    cta_left_frame.check_start_state(self)


def open_serial_connection(self: CableTesterApplication):
    # Open the serial connection
    try:
        self.serial_connection = serial.Serial(
            port=self.selected_port.get(),
            baudrate=9600,  # You may need to adjust this
            timeout=1,
        )
        self.log_info(
            f"Successfully opened COM port: {self.selected_port.get()}"
        )
        # send R to reboot device
        send_data(self, "R")
    except Exception as e:
        self.log_error(f"Error opening COM port: {str(e)}")
        return


def close_serial_connection(self: CableTesterApplication):
    # send R to reboot device
    send_data(self, "R")
    # Close the serial connection
    if self.serial_connection and self.serial_connection.is_open:
        self.serial_connection.close()
        self.log("COM port closed")


def read_data(self: CableTesterApplication):
    # Check if there's data to read
    if self.serial_connection and self.serial_connection.in_waiting > 0:
        # Read data from COM port
        data = self.serial_connection.readline().strip()

        # Log received data
        self.log(f"Received: {data}")

        # Convert bytes to string if needed
        if isinstance(data, bytes):
            data = data.decode("utf-8", errors="replace")
            # Process the data and send response
            process_data(self, data)


def process_data(self: CableTesterApplication, data: str):
    """Process the received data and send appropriate response"""
    try:
        # This is a placeholder - implement your actual data processing logic
        # For example, parse the received data and look up values in the table

        # Example implementation:
        value = data.strip()

        _contact_count = self.contact_count.get()

        if self.com_state == COM_STATE.PREINIT:
            if value == "?":
                send_data(self, _contact_count)
                self.log(f"Contact count set to {_contact_count}")
                self.com_state = COM_STATE.INIT

        elif self.com_state == COM_STATE.INIT:
            # Nx — return accepted contact_count (x) value
            # Tx — return contact_count value is too big
            if value.startswith("N"):
                _value = value.removeprefix("N")
                if str(_value) == str(_contact_count):
                    self.log(f"Get confirm set to {_contact_count}")
                    self.com_state = COM_STATE.LISTEN
                else:
                    raise ValueError(
                        "Confirm contact count differ from the origin"
                    )
            elif value.startswith("T"):
                _value = value.removeprefix("T")
                self.log_warning(f"Maximum number of contact: {_value}")
                cta_process.stop_process(self)
                raise ValueError("Set to many contact count")
            else:
                raise ValueError(f"Receive unexpected value: {value}")

        elif self.com_state == COM_STATE.LISTEN:
            # Look up the value in the table (simplified example)
            if value.startswith("P"):
                _value = value.removeprefix("P")
                # look column откуда
                result = cta_tables.find_value_in_table(self, _value)
                if result:
                    line_1, line_2 = result
                    send_data(self, line_1)
                    send_data(self, line_2)
                else:
                    self.log_warning("Nothing to send")
            else:
                raise ValueError(f"Receive unexpected value: {value}")

    except Exception as e:
        self.log_error(f"Error processing data: {str(e)}")


def send_data(self: CableTesterApplication, data):
    """Send data to the COM port"""
    if self.serial_connection and self.serial_connection.is_open:
        try:
            data = (str(data) + "\n").encode("utf-8")

            self.serial_connection.write(data)
            self.log(f"Sent: {data}")
        except Exception as e:
            self.log(f"Error sending data: {str(e)}")
