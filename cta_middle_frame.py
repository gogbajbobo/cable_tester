import tkinter as tk
from tkinter import ttk
import os

from app import CableTesterApplication
import cta_images

IMAGE_MAX_SIZE = 150


def setup_middle_frame(self: CableTesterApplication, frame: ttk.LabelFrame):
    # Создаем фрейм для изображений вверху
    images_frame = ttk.Frame(frame)
    images_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # Создаем Canvas для размещения изображений
    self.images_canvas = tk.Canvas(images_frame, height=IMAGE_MAX_SIZE)
    self.images_canvas.pack(fill="x", expand=True)

    put_images_into_canvas(self)

    # Обработчик изменения размера
    def on_canvas_resize(event):
        if self.image_paths:
            # Очищаем canvas
            self.images_canvas.delete("all")
            update_canvas_with_images(self)

    # Привязываем обработчик
    self.images_canvas.bind("<Configure>", on_canvas_resize)

    # Data view section with header
    ttk.Label(frame, text="Table Data:").grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )

    # Create Treeview for data display
    self.data_tree = ttk.Treeview(frame, columns=(), show="headings")

    self.data_tree.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

    # Add scrollbar
    scrollbar = ttk.Scrollbar(
        frame, orient="vertical", command=self.data_tree.yview
    )
    scrollbar.grid(row=2, column=1, sticky="ns")
    self.data_tree.configure(yscrollcommand=scrollbar.set)

    # Создаем фрейм для нижней части
    bottom_frame = ttk.LabelFrame(frame, text="Process Information")
    bottom_frame.grid(
        row=3, column=0, padx=5, pady=10, sticky="nsew", columnspan=2
    )

    # Создаем фрейм для двух изображений
    img_status_frame = ttk.Frame(bottom_frame)
    img_status_frame.pack(fill="x", padx=5, pady=5)

    # Создаем левую и правую части для изображений
    left_img_frame = ttk.LabelFrame(img_status_frame, text="Откуда")
    left_img_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    right_img_frame = ttk.LabelFrame(img_status_frame, text="Куда")
    right_img_frame.pack(
        side="right", fill="both", expand=True, padx=5, pady=5
    )

    cta_images.load_process_images(self, left_img_frame, right_img_frame)

    # Создаем фрейм для текстовой информации
    text_status_frame = ttk.Frame(bottom_frame)
    text_status_frame.pack(fill="x", padx=5, pady=10)

    # Создаем метки с большим жирным шрифтом
    status_font = ("Arial", 16, "bold")

    self.status_line1 = tk.StringVar(value="Маркировка:")
    self.status_line2 = tk.StringVar(value="Цвет: ")

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


def update_data_view(self: CableTesterApplication):
    self.log("update_data_view")
    put_images_into_canvas(self)

    """Update the middle frame with received and corresponding table data"""
    # Add to the treeview
    # self.data_tree.insert("", "end", values=(received, table_data))

    # Auto-scroll to the bottom
    self.data_tree.yview_moveto(1)

    # Limit the number of items (optional)
    items = self.data_tree.get_children()
    if len(items) > 100:  # Keep only the last 100 entries
        self.data_tree.delete(items[0])


def update_canvas_with_images(self: CableTesterApplication):
    # Вычисляем размер для каждого изображения
    img_width = min(
        IMAGE_MAX_SIZE,
        (self.images_canvas.winfo_width() or 800)
        // max(1, len(self.image_paths)),
    )
    create_images(
        self,
        self.images_canvas,
        img_width,
        IMAGE_MAX_SIZE,
    )


def put_images_into_canvas(self):
    self.image_paths = cta_images.find_images(self)
    self.images_canvas.delete("all")

    # Загрузка и отображение изображений
    if self.image_paths:
        self.image_references = [None] * len(self.image_paths)
        update_canvas_with_images(self)

        # Обновляем размер canvas, чтобы вместить все изображения
        self.images_canvas.config(scrollregion=self.images_canvas.bbox("all"))
    else:
        # Если изображений нет, показываем сообщение
        self.images_canvas.create_text(
            10,
            75,
            text="No images found",
            fill="gray",
            font=("Arial", 12),
            anchor=tk.W,
        )


def create_images(
    self: CableTesterApplication,
    images_canvas: tk.Canvas,
    img_width,
    img_height,
):
    cta_images.prepare_images_for_canvas(self, img_width, img_height)

    for i, tk_img in enumerate(self.image_references):
        x_pos = i * img_width
        if tk_img:
            images_canvas.create_image(x_pos, 0, image=tk_img, anchor="nw")
        else:
            self.images_canvas.create_text(
                # 0,
                x_pos + img_width // 2,
                img_height // 2,
                text="No image found",
                fill="gray",
                font=("Arial", 12),
                anchor=tk.S,
            )

        # Добавляем подпись (имя файла)
        file_name = os.path.basename(self.image_paths[i])
        images_canvas.create_text(
            x_pos + img_width // 2,
            img_height - 10,
            text=file_name,
            fill="black",
            font=("Arial", 8),
            anchor="s",
        )


# Методы для обновления статуса
def update_status_line1(self: CableTesterApplication, text, color="blue"):
    self.status_line1.set(text)
    self.status_label1.configure(foreground=color)


def update_status_line2(self: CableTesterApplication, text, color="darkgreen"):
    self.status_line2.set(text)
    self.status_label2.configure(foreground=color)
