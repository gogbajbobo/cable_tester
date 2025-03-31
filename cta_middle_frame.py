import tkinter as tk
from tkinter import ttk
import os
from PIL import ImageTk

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

            # Пересчитываем размеры
            new_img_width = min(
                IMAGE_MAX_SIZE, event.width // max(1, len(self.image_paths))
            )
            create_images(
                self,
                self.images_canvas,
                self.image_paths,
                new_img_width,
                IMAGE_MAX_SIZE,
            )

    # Привязываем обработчик
    self.images_canvas.bind("<Configure>", on_canvas_resize)

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


def put_images_into_canvas(self):
    self.image_paths = cta_images.find_images(self)
    self.images_canvas.delete("all")

    # Загрузка и отображение изображений
    if self.image_paths:
        # Вычисляем размер для каждого изображения
        img_width = min(
            IMAGE_MAX_SIZE,
            (self.images_canvas.winfo_width() or 800)
            // max(1, len(self.image_paths)),
        )

        self.image_references = [None] * len(self.image_paths)
        create_images(
            self,
            self.images_canvas,
            self.image_paths,
            img_width,
            IMAGE_MAX_SIZE,
        )

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
    image_paths,
    img_width,
    img_height,
):
    for i, img_path in enumerate(image_paths):

        # Вычисляем позицию
        x_pos = i * img_width

        try:
            # Загружаем изображение
            pil_img = cta_images.load_and_resize_image(
                img_path, img_width, img_height
            )
            if pil_img:
                tk_img = ImageTk.PhotoImage(pil_img)
                self.image_references[i] = tk_img  # Обновляем ссылку

                # Отображаем изображение
                images_canvas.create_image(x_pos, 0, image=tk_img, anchor="nw")

        except Exception as e:
            self.images_canvas.create_text(
                # 0,
                x_pos + img_width // 2,
                img_height // 2,
                text="No image found",
                fill="gray",
                font=("Arial", 12),
                anchor=tk.S,
            )
            self.log_error(f"Error loading image {img_path}: {str(e)}")

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
