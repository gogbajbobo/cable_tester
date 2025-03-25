import threading
import time
import os
import pandas as pd

from app import CableTesterApplication, DATA_PATH
from cta_ports import open_serial_connection, close_serial_connection, read_data


def start_process(self: CableTesterApplication):
    """Start the main process loop"""
    if self.running:
        self.log("Process is already running")
        return

    if not self.selected_port.get():
        self.log("Error: No COM port selected")
        return

    if not self.selected_table.get():
        self.log("Error: No table selected")
        return

    try:
        self.log(
            f"Starting process with port {self.selected_port.get()} and table {self.selected_table.get()}"
        )

        # Load the selected table
        st = os.path.join(DATA_PATH, self.selected_table.get())
        try:
            if st.endswith(".csv"):
                self.table_data = pd.read_csv(st)
            elif st.endswith(".xlsx") or st.endswith(".xls"):
                self.table_data = pd.read_excel(st)
            self.log(f"Successfully loaded table: {st}")
        except Exception as e:
            self.log(f"Error loading table: {str(e)}")
            return

        open_serial_connection(self)

        # Start the process thread
        self.running = True
        self.thread = threading.Thread(target=lambda: process_loop(self))
        self.thread.daemon = True
        self.thread.start()

    except Exception as e:
        self.log(f"Error starting process: {str(e)}")


def stop_process(self: CableTesterApplication):
    """Stop the main process loop"""
    if not self.running:
        self.log("Process is not running")
        return

    self.log("Stopping process")
    self.running = False

    # Wait for the thread to finish
    if self.thread:
        self.thread.join(timeout=2.0)

    close_serial_connection(self)


def process_loop(self: CableTesterApplication):
    """Main processing loop - runs in a separate thread"""
    self.log("Process loop started")

    while self.running:
        try:
            if not self.serial_connection:
                raise ValueError("self.serial_connection is None")

            read_data(self)

            # Small delay to prevent CPU hogging
            time.sleep(0.01)

        except Exception as e:
            self.log(f"Error in process loop: {str(e)}")
            self.running = False

    self.log("Process loop ended")
