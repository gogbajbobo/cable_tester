import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time
import os
import pandas as pd
from datetime import datetime
from PIL import ImageTk

import layout

DATA_PATH = os.path.join(os.path.curdir, "data")


class CableTesterApplication:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("COM Port Data Manager")
        self.root.geometry("1200x700")

        # Variables
        self.selected_table = tk.StringVar()
        self.selected_port = tk.StringVar()
        self.contact_count = tk.IntVar(value=32)
        self.running = False
        self.tables_list = []
        self.serial_connection = None
        self.thread = None

        # init empty props
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
        layout.create_layout(self)

        # Initialize logs
        self.log("Application started")

    def send_data(self, data):
        """Send data to the COM port"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # Convert to bytes if it's a string
                if isinstance(data, str):
                    data = data.encode("utf-8")

                self.serial_connection.write(data)
                self.log(f"Sent: {data}")
            except Exception as e:
                self.log(f"Error sending data: {str(e)}")

    def update_data_view(self, received, table_data):
        """Update the middle frame with received and corresponding table data"""
        # Add to the treeview
        self.data_tree.insert("", "end", values=(received, table_data))

        # Auto-scroll to the bottom
        self.data_tree.yview_moveto(1)

        # Limit the number of items (optional)
        items = self.data_tree.get_children()
        if len(items) > 100:  # Keep only the last 100 entries
            self.data_tree.delete(items[0])

    def log(self, message):
        """Add a message to the application log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        # Use after to ensure thread safety when updating the UI
        self.root.after(0, lambda: self.logs_text.insert(tk.END, log_message))
        self.root.after(0, lambda: self.logs_text.see(tk.END))

        # Print to console as well for debugging
        print(log_message, end="")


def main():
    root = tk.Tk()
    app = CableTesterApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
