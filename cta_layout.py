import tkinter as tk
from tkinter import ttk

from app import CableTesterApplication

from cta_left_frame import setup_left_frame
from cta_middle_frame import setup_middle_frame
from cta_right_frame import setup_right_frame


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

    # Setup Frames
    setup_left_frame(self, left_frame)  # Left Frame - Control Panel
    setup_middle_frame(self, middle_frame)  # Middle Frame - Data View
    setup_right_frame(self, right_frame)  # Right Frame - System Information

    # Configure grid weights
    left_frame.grid_columnconfigure(0, weight=1)

    middle_frame.grid_columnconfigure(0, weight=1)
    middle_frame.grid_rowconfigure(
        2, weight=1
    )  # Изменено с 1 на 2, так как добавили строку с изображениями

    right_frame.grid_columnconfigure(0, weight=1)
    right_frame.grid_rowconfigure(0, weight=1)
