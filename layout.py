import tkinter as tk
from tkinter import ttk

from app import CableTesterApplication

from left_frame import setup_left_frame
from middle_frame import setup_middle_frame
from right_frame import setup_right_frame


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
    setup_middle_frame(self, middle_frame)

    # Right Frame - System Information
    setup_right_frame(self, right_frame)
