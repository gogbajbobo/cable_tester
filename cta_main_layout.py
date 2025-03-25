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

from app import CableTesterApplication
from cta_left_frame import setup_left_frame

DATA_PATH = os.path.join(os.path.curdir, "data")


def create_layout(self: CableTesterApplication):
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
    setup_left_frame(self, left_frame)

    # Middle Frame - Data View
    self.setup_middle_frame(middle_frame)

    # Right Frame - System Information
    self.setup_right_frame(right_frame)
