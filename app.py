import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time
import os
import pandas as pd
from datetime import datetime
from PIL import ImageTk, Image

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

        # Хранилище для ссылок на изображения (чтобы избежать сборки мусора)
        self.image_references: list[ImageTk.PhotoImage | None] = []

        # Create the main layout
        layout.create_layout(self)

        # Initialize logs
        self.log("Application started")

        # Update initial ports and tables lists
        self.update_ports_list()
        self.update_tables_list()

    def on_table_selected(self, event=None):
        """Обрабатывает выбор таблицы из выпадающего списка"""
        selected_table = self.selected_table.get()

        if not selected_table:
            self.log("No table selected")
            return

        self.log(f"Table selected: {selected_table}")

        try:
            # Загружаем выбранную таблицу
            st = os.path.join(DATA_PATH, selected_table)
            if st.endswith(".csv"):
                self.table_data = pd.read_csv(st)
            elif st.endswith(".xlsx") or st.endswith(".xls"):
                self.table_data = pd.read_excel(st)
            else:
                self.log(f"Unsupported file format: {st}")
                return

            # Получаем информацию о таблице
            rows, cols = self.table_data.shape
            self.log(f"Table loaded: {rows} rows, {cols} columns")

            # Очищаем текущие данные в Treeview
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)

            # Опционально: Показываем превью таблицы (первые несколько строк)
            preview_rows = min(5, rows)  # показываем максимум 5 строк для превью
            for i in range(preview_rows):
                row = self.table_data.iloc[i]
                preview = str(dict(zip(self.table_data.columns[:3], row.values[:3])))
                if len(self.table_data.columns) > 3:
                    preview += (
                        " ... "  # добавляем многоточие, если есть больше столбцов
                    )
                self.data_tree.insert("", "end", values=(f"Preview Row {i}", preview))

            # Если таблица содержит информацию о контактах, обновляем соответствующее поле
            if (
                "contacts" in self.table_data.columns
                or "Contacts" in self.table_data.columns
            ):
                contact_col = (
                    "contacts" if "contacts" in self.table_data.columns else "Contacts"
                )
                # Берем максимальное значение из столбца контактов, если это число
                try:
                    max_contacts = self.table_data[contact_col].max()
                    if pd.notna(max_contacts) and isinstance(
                        max_contacts, (int, float)
                    ):
                        self.contact_count.set(int(max_contacts))
                        self.log(
                            f"Updated contact count to {max_contacts} based on table data"
                        )
                except Exception as e:
                    self.log(f"Could not update contact count from table: {str(e)}")

        except Exception as e:
            self.log(f"Error loading table {selected_table}: {str(e)}")

    def find_images(self):
        """Ищет изображения в текущей директории"""
        image_paths = []

        # Расширения файлов изображений, которые мы ищем
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

        # Ищем изображения в текущей директории
        for file in os.listdir(DATA_PATH):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_paths.append(os.path.join(DATA_PATH, file))

        # Ограничиваем количество изображений (опционально)
        if len(image_paths) > 5:
            self.log(f"Found {len(image_paths)} images, showing first 5")
            image_paths = image_paths[:5]
        else:
            self.log(f"Found {len(image_paths)} images")

        return image_paths

    def load_and_resize_image(self, image_path, width, height):
        """Загружает и изменяет размер изображения"""
        # from PIL import Image

        if (width == 0) or (height == 0):
            return None

        # Загружаем изображение
        img = Image.open(image_path)

        # Вычисляем соотношение сторон
        img_ratio = img.width / img.height

        # Вычисляем новые размеры, сохраняя соотношение сторон
        if img_ratio > 1:  # Широкое изображение
            new_width = width
            new_height = int(width / img_ratio)
        else:  # Высокое или квадратное изображение
            new_height = height
            new_width = int(height * img_ratio)

        # Изменяем размер изображения
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # self.log(f"here: {new_width} {new_height}")

        return img

    def update_tables_list(self):
        """Update the list of available tables"""
        # This is a placeholder - replace with actual table discovery logic
        # For example, scan a directory for CSV or Excel files

        self.log("Updating tables list")

        # Example implementation - looking for CSV and Excel files in current directory
        self.tables_list = []

        for file in os.listdir(DATA_PATH):
            if file.endswith(".csv") or file.endswith(".xlsx") or file.endswith(".xls"):
                self.tables_list.append(file)

        self.tables_combobox["values"] = self.tables_list

        if self.tables_list:
            self.tables_combobox.current(0)
            self.log(f"Found {len(self.tables_list)} tables")
            self.on_table_selected()
        else:
            self.log("No tables found")

    def update_ports_list(self):
        """Update the list of available COM ports"""
        self.log("Updating COM ports list")

        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.ports_combobox["values"] = ports

        if ports:
            self.ports_combobox.current(0)
            self.log(f"Found {len(ports)} COM ports")
        else:
            self.log("No COM ports found")

    def start_process(self):
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
            self.log(f"Contact count set to {self.contact_count.get()}")

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

            # Open the serial connection
            try:
                self.serial_connection = serial.Serial(
                    port=self.selected_port.get(),
                    baudrate=9600,  # You may need to adjust this
                    timeout=1,
                )
                self.log(f"Successfully opened COM port: {self.selected_port.get()}")
            except Exception as e:
                self.log(f"Error opening COM port: {str(e)}")
                return

            # Start the process thread
            self.running = True
            self.thread = threading.Thread(target=self.process_loop)
            self.thread.daemon = True
            self.thread.start()

        except Exception as e:
            self.log(f"Error starting process: {str(e)}")

    def stop_process(self):
        """Stop the main process loop"""
        if not self.running:
            self.log("Process is not running")
            return

        self.log("Stopping process")
        self.running = False

        # Wait for the thread to finish
        if self.thread:
            self.thread.join(timeout=2.0)

        # Close the serial connection
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.log("COM port closed")

    def process_loop(self):
        """Main processing loop - runs in a separate thread"""
        self.log("Process loop started")

        while self.running:
            try:
                if not self.serial_connection:
                    raise ValueError("self.serial_connection is None")
                # Check if there's data to read
                if self.serial_connection.in_waiting > 0:
                    # Read data from COM port
                    data = self.serial_connection.readline().strip()

                    # Convert bytes to string if needed
                    if isinstance(data, bytes):
                        data = data.decode("utf-8", errors="replace")

                    # Log received data
                    self.log(f"Received: {data}")

                    # Process the data and send response
                    self.process_data(data)

                # Small delay to prevent CPU hogging
                time.sleep(0.01)

            except Exception as e:
                self.log(f"Error in process loop: {str(e)}")
                self.running = False

        self.log("Process loop ended")

    def process_data(self, data):
        """Process the received data and send appropriate response"""
        try:
            # This is a placeholder - implement your actual data processing logic
            # For example, parse the received data and look up values in the table

            # Example implementation:
            value = data.strip()

            # Look up the value in the table (simplified example)
            try:
                # Convert to numeric if possible
                numeric_value = (
                    float(value) if value.replace(".", "", 1).isdigit() else value
                )

                # Find matching data in table (this is just an example)
                # You'll need to adapt this to your actual table structure
                if isinstance(numeric_value, (int, float)) and numeric_value < len(
                    self.table_data
                ):
                    row_index = int(numeric_value)
                    table_row = self.table_data.iloc[row_index]
                    response = str(table_row.to_dict())
                else:
                    # Search for the value in the table
                    found = False
                    for idx, row in self.table_data.iterrows():
                        if value in str(row.values):
                            response = str(row.to_dict())
                            found = True
                            break

                    if not found:
                        response = "No matching data found"
            except Exception as e:
                response = f"Error processing data: {str(e)}"

            # Update the middle frame with the data
            self.update_data_view(value, response)

            # Send response back through COM port
            self.send_data(response)

        except Exception as e:
            self.log(f"Error processing data: {str(e)}")

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
