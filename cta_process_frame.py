import tkinter as tk
from tkinter import ttk

from app import CableTesterApplication
import cta_images

IMAGE_MAX_SIZE = 150


def update_process_frame(
    self: CableTesterApplication,
    conn_value_1: str | None = None,
    conn_value_2: str | None = None,
    mark_value: str | None = None,
    color_value: str | None = None,
):

    for w in self.process_frame.winfo_children():
        w.destroy()

    # Создаем фрейм для двух изображений
    img_status_frame = ttk.Frame(self.process_frame)
    img_status_frame.pack(fill="x", padx=5, pady=5)

    # Создаем левую и правую части для изображений
    left_img_frame = ttk.LabelFrame(img_status_frame, text="Откуда")
    left_img_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    right_img_frame = ttk.LabelFrame(img_status_frame, text="Куда")
    right_img_frame.pack(
        side="right", fill="both", expand=True, padx=5, pady=5
    )

    cta_images.load_process_images(
        self, left_img_frame, right_img_frame, conn_value_1, conn_value_2
    )

    # Создаем фрейм для текстовой информации
    text_status_frame = ttk.Frame(self.process_frame)
    text_status_frame.pack(fill="x", padx=5, pady=10)

    # Создаем метки с большим жирным шрифтом
    status_font = ("Arial", 16, "bold")

    self.status_line1 = tk.StringVar(value=f"Маркировка: {mark_value}")
    self.status_line2 = tk.StringVar(value=f"Цвет: {color_value}")

    self.status_label1 = ttk.Label(
        text_status_frame,
        textvariable=self.status_line1,
        font=status_font,
        foreground="blue",
    )
    self.status_label1.pack(fill="x", pady=5)

    self.status_label2 = ttk.Label(
        text_status_frame,
        textvariable=self.status_line2,
        font=status_font,
        foreground="darkgreen",
    )
    self.status_label2.pack(fill="x", pady=5)


# Методы для обновления статуса
def update_status_line1(self: CableTesterApplication, text, color="blue"):
    self.status_line1.set(text)
    self.status_label1.configure(foreground=color)


def update_status_line2(self: CableTesterApplication, text, color="darkgreen"):
    self.status_line2.set(text)
    self.status_label2.configure(foreground=color)
