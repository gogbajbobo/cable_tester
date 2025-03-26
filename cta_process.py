import threading
import time
import os
import pandas as pd

from app import CableTesterApplication, DATA_PATH, COM_STATE
from cta_ports import open_serial_connection, close_serial_connection, read_data
from cta_tables import load_selected_table


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

        load_selected_table(self)
        open_serial_connection(self)

        # Start the process thread
        self.com_state = COM_STATE.PREINIT
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
    self.com_state = COM_STATE.NONE

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
