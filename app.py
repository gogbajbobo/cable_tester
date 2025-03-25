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

DATA_PATH = os.path.join(os.path.curdir, "data")


class COMPortApplication:
    def __init__(self, root):
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

        # Create the main layout
        self.create_layout()

        # Initialize logs
        self.log("Application started")

        # Update initial ports and tables lists
        self.update_ports_list()
        self.update_tables_list()

    def create_layout(self):
        # Создаем корневой PanedWindow с горизонтальной ориентацией
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create frames for the three sections
        left_frame = ttk.LabelFrame(main_paned, text="Control Panel")

        # Вложенный PanedWindow для средней и правой частей
        right_paned = tk.PanedWindow(main_paned, orient=tk.HORIZONTAL)

        middle_frame = ttk.LabelFrame(right_paned, text="Data View")
        right_frame = ttk.LabelFrame(right_paned, text="System Information")

        # Добавляем фреймы в соответствующие PanedWindow
        main_paned.add(left_frame)
        main_paned.add(right_paned)

        right_paned.add(middle_frame)
        right_paned.add(right_frame)

        # Установка начальных позиций разделителей после отрисовки окна
        self.root.update()
        total_width = self.root.winfo_width() - 20  # Учитываем отступы

        main_paned.sash_place(0, int(total_width * 0.2), 0)
        right_paned.sash_place(0, int(total_width * 0.5), 0)

        # Left Frame - Control Panel
        self.setup_left_frame(left_frame)

        # Middle Frame - Data View
        self.setup_middle_frame(middle_frame)

        # Right Frame - System Information
        self.setup_right_frame(right_frame)

    def on_table_selected(self, event=None):
        """Обрабатывает выбор таблицы из выпадающего списка"""
        selected_table = self.selected_table.get()

        if not selected_table:
            self.log("No table selected")
            return

        self.log(f"Table selected: {selected_table}")

        try:
            # Загружаем выбранную таблицу
            if selected_table.endswith(".csv"):
                self.table_data = pd.read_csv(selected_table)
            elif selected_table.endswith(".xlsx"):
                self.table_data = pd.read_excel(selected_table)
            else:
                self.log(f"Unsupported file format: {selected_table}")
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

    def setup_left_frame(self, frame):
        # Tables section
        ttk.Label(frame, text="Tables:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        ttk.Button(
            frame, text="Update Tables List", command=self.update_tables_list
        ).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.tables_combobox = ttk.Combobox(frame, textvariable=self.selected_table)
        self.tables_combobox.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        # Привязываем обработчик события выбора
        self.tables_combobox.bind("<<ComboboxSelected>>", self.on_table_selected)

        # COM Ports section
        ttk.Label(frame, text="COM Ports:").grid(
            row=3, column=0, padx=5, pady=5, sticky="w"
        )
        ttk.Button(
            frame, text="Update COM Ports List", command=self.update_ports_list
        ).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.ports_combobox = ttk.Combobox(frame, textvariable=self.selected_port)
        self.ports_combobox.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        # Contact count
        ttk.Label(frame, text="Number of Contacts:").grid(
            row=6, column=0, padx=5, pady=5, sticky="w"
        )
        ttk.Entry(frame, textvariable=self.contact_count).grid(
            row=7, column=0, padx=5, pady=5, sticky="ew"
        )

        # Control buttons
        ttk.Button(frame, text="Start Process", command=self.start_process).grid(
            row=8, column=0, padx=5, pady=5, sticky="ew"
        )
        ttk.Button(frame, text="Stop Process", command=self.stop_process).grid(
            row=9, column=0, padx=5, pady=5, sticky="ew"
        )

        # Configure grid weights for left frame
        frame.grid_columnconfigure(0, weight=1)

    def setup_middle_frame(self, frame):
        # Создаем фрейм для изображений вверху
        images_frame = ttk.Frame(frame)
        images_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Создаем Canvas для размещения изображений
        images_canvas = tk.Canvas(images_frame, height=150)
        images_canvas.pack(fill="x", expand=True)

        # Список путей к изображениям (замените на свои пути)
        # Можно добавить поиск изображений в директории
        image_paths = self.find_images()

        # Хранилище для ссылок на изображения (чтобы избежать сборки мусора)
        self.image_references: list[ImageTk.PhotoImage | None] = []

        # Загрузка и отображение изображений
        if image_paths:
            # Вычисляем размер для каждого изображения
            img_width = min(
                150, (images_canvas.winfo_width() or 800) // max(1, len(image_paths))
            )
            img_height = 150

            self.image_references = [None] * len(image_paths)

            # Загружаем и отображаем изображения
            for i, img_path in enumerate(image_paths):
                try:
                    # Загружаем изображение
                    pil_img = self.load_and_resize_image(
                        img_path, img_width, img_height
                    )
                    if pil_img:
                        tk_img = ImageTk.PhotoImage(pil_img)
                        self.image_references.append(tk_img)  # Сохраняем ссылку

                        # Вычисляем позицию
                        x_pos = i * img_width

                        # Отображаем изображение
                        images_canvas.create_image(x_pos, 0, image=tk_img, anchor="nw")

                        # Добавляем подпись (имя файла)
                        file_name = os.path.basename(img_path)
                        images_canvas.create_text(
                            x_pos + img_width // 2,
                            img_height - 10,
                            text=file_name,
                            fill="black",
                            font=("Arial", 8),
                            anchor="s",
                        )

                except Exception as e:
                    self.log(f"Error loading image {img_path}: {str(e)}")

            # Обновляем размер canvas, чтобы вместить все изображения
            images_canvas.config(scrollregion=images_canvas.bbox("all"))
        else:
            # Если изображений нет, показываем сообщение
            images_canvas.create_text(
                images_canvas.winfo_width() // 2,
                75,
                text="No images found",
                fill="gray",
                font=("Arial", 12),
            )

        # Обработчик изменения размера
        def on_canvas_resize(event):
            if image_paths:
                # Очищаем canvas
                images_canvas.delete("all")

                # Пересчитываем размеры
                new_img_width = min(150, event.width // max(1, len(image_paths)))

                # Перерисовываем изображения
                for i, img_path in enumerate(image_paths):
                    try:
                        # Загружаем и изменяем размер изображения
                        pil_img = self.load_and_resize_image(
                            img_path, new_img_width, img_height
                        )
                        tk_img = ImageTk.PhotoImage(pil_img)

                        self.image_references[i] = tk_img  # Обновляем ссылку

                        # Вычисляем позицию
                        x_pos = i * new_img_width

                        # Отображаем изображение
                        images_canvas.create_image(x_pos, 0, image=tk_img, anchor="nw")

                        # Добавляем подпись
                        file_name = os.path.basename(img_path)
                        images_canvas.create_text(
                            x_pos + new_img_width // 2,
                            img_height - 10,
                            text=file_name,
                            fill="black",
                            font=("Arial", 8),
                            anchor="s",
                        )

                    except Exception as e:
                        self.log(f"Error resizing image {img_path}: {str(e)}")

        # Привязываем обработчик
        images_canvas.bind("<Configure>", on_canvas_resize)

        # Data view section with header
        ttk.Label(frame, text="Received Data and Corresponding Table Data:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )

        # Create Treeview for data display
        columns = ("Received Data", "Table Data")
        self.data_tree = ttk.Treeview(frame, columns=columns, show="headings")

        # Set column headings
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=150)

        self.data_tree.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self.data_tree.yview
        )
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.data_tree.configure(yscrollcommand=scrollbar.set)

        # Configure grid weights for middle frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(
            2, weight=1
        )  # Изменено с 1 на 2, так как добавили строку с изображениями

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
        # self.log(f"load_and_resize_image: {width} {height}")

        # Загружаем изображение
        img = Image.open(image_path)

        # self.log(f"img open: {img.width} {img.height}")

        # Вычисляем соотношение сторон
        img_ratio = img.width / img.height

        # self.log(f"img_ratio: {img_ratio}")

        # Вычисляем новые размеры, сохраняя соотношение сторон
        if img_ratio > 1:  # Широкое изображение
            new_width = width
            new_height = int(width / img_ratio)
        else:  # Высокое или квадратное изображение
            new_height = height
            new_width = int(height * img_ratio)

        # self.log(f"here: {new_width} {new_height}")

        # Изменяем размер изображения
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # self.log(f"here: {new_width} {new_height}")

        return img

    def setup_right_frame(self, frame):
        # Create notebook for different logs
        notebook = ttk.Notebook(frame)
        notebook.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Application logs tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Application Logs")

        self.logs_text = tk.Text(logs_frame, wrap="word")
        self.logs_text.pack(fill="both", expand=True)
        logs_scrollbar = ttk.Scrollbar(logs_frame, command=self.logs_text.yview)
        logs_scrollbar.pack(side="right", fill="y")
        self.logs_text.configure(yscrollcommand=logs_scrollbar.set)

        # Configure grid weights for right frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

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
    app = COMPortApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
