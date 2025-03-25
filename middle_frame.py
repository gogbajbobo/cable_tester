import tkinter as tk
from tkinter import ttk
import os
from PIL import ImageTk

from app import CableTesterApplication
from images import find_images, load_and_resize_image


def setup_middle_frame(self: CableTesterApplication, frame: ttk.LabelFrame):
    # Создаем фрейм для изображений вверху
    images_frame = ttk.Frame(frame)
    images_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # Создаем Canvas для размещения изображений
    images_canvas = tk.Canvas(images_frame, height=150)
    images_canvas.pack(fill="x", expand=True)

    # Список путей к изображениям (замените на свои пути)
    # Можно добавить поиск изображений в директории
    image_paths = find_images(self)

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
                pil_img = load_and_resize_image(self, img_path, img_width, img_height)
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
                    pil_img = load_and_resize_image(
                        self, img_path, new_img_width, img_height
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
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.data_tree.yview)
    scrollbar.grid(row=2, column=1, sticky="ns")
    self.data_tree.configure(yscrollcommand=scrollbar.set)

    # Configure grid weights for middle frame
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(
        2, weight=1
    )  # Изменено с 1 на 2, так как добавили строку с изображениями
