import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import os
import pandas as pd
from datetime import datetime
from PIL import ImageTk
from enum import Enum

import cta_layout

DATA_PATH = os.path.join(os.path.curdir, "data")


class COM_STATE(str, Enum):
    NONE = "None"
    PREINIT = "preinit"
    INIT = "init"
    LISTEN = "listen"


class LOG_TAG_CONFIG(str, Enum):
    NONE = "None"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class CableTesterApplication:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cable tester")
        self.root.geometry("1200x700")

        # Variables
        self.selected_table = tk.StringVar()
        self.selected_port = tk.StringVar()
        self.contact_count = tk.IntVar(value=32)
        self.running = False
        self.com_state: COM_STATE = COM_STATE.NONE
        self.tables_list = []
        self.serial_connection = None
        self.thread = None

        # init empty props
        self.left_frame = ttk.LabelFrame()
        self.tables_combobox = ttk.Combobox()
        self.ports_combobox = ttk.Combobox()
        self.data_tree = ttk.Treeview()
        self.logs_text = tk.Text()
        self.table_data = pd.DataFrame()
        self.serial_connection = serial.Serial()
        self.thread = threading.Thread()

        # Хранилище для ссылок на изображения (чтобы избежать сборки мусора)
        self.image_references: list[ImageTk.PhotoImage | None] = []

        # Create the main layout
        cta_layout.create_layout(self)

        # Initialize logs
        self.log_info("Application started")

    def log(self, message, tag=LOG_TAG_CONFIG.NONE):
        """Add a message to the application log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        # Use after to ensure thread safety when updating the UI
        self.root.after(
            0, lambda: self.logs_text.insert(tk.END, log_message, tag)
        )
        self.root.after(0, lambda: self.logs_text.see(tk.END))

        # Print to console as well for debugging
        print(log_message, end="")

    def log_info(self, message):
        return self.log(message, LOG_TAG_CONFIG.INFO)

    def log_warning(self, message):
        return self.log(message, LOG_TAG_CONFIG.WARNING)

    def log_error(self, message):
        return self.log(message, LOG_TAG_CONFIG.ERROR)


def main():
    root = tk.Tk()
    app = CableTesterApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
