import os
from tkinter import ttk
from PIL import Image, ImageTk

from app import CableTesterApplication, DATA_PATH

DEFAULT_IMAGE_SIZE = (256, 256)


def find_image_for_connector(
    self: CableTesterApplication, connector: str
) -> str | None:
    if set(["Изображение", "Разъём"]).issubset(self.table_data.columns):
        condition = self.table_data["Разъём"] == connector
        result = self.table_data.loc[condition]
        if not result.empty:
            return result["Изображение"].values[0]
    return None


def find_images(self: CableTesterApplication):
    """Ищет изображения в директории %DATA_PATH%"""
    image_paths = []

    if "Изображение" in self.table_data.columns:

        images = self.table_data["Изображение"].dropna().to_list()
        # self.log(f"self.table_data['Изображение']\n{images}")

        self.loaded_images = [None] * len(images)

        for i, im_file in enumerate(images):
            im_path = os.path.join(DATA_PATH, im_file.lower())
            image_paths.append(im_path)
            try:
                self.loaded_images[i] = Image.open(im_path)
            except Exception as e:
                self.log_error(f"Can't load image {im_file}: {str(e)}")
                self.loaded_images[i] = None

        self.log(f"Found {len(image_paths)} images")

    return image_paths


def resize_image(img: Image.Image | None, width, height) -> Image.Image | None:
    if (img is None) or (width == 0) or (height == 0):
        return None

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

    return img


def prepare_images_for_canvas(
    self: CableTesterApplication, img_width, img_height
):
    for i, loaded_image in enumerate(self.loaded_images):
        pil_img = resize_image(loaded_image, img_width, img_height)
        if pil_img:
            tk_img = ImageTk.PhotoImage(pil_img)
            self.image_references[i] = tk_img  # Обновляем ссылку
        else:
            self.image_references[i] = None


def load_process_images(
    self: CableTesterApplication,
    left_img_frame,
    right_img_frame,
    conn_value_1=None,
    conn_value_2=None,
):
    left_tk_img = load_process_image(self, left_img_frame, conn_value_1)
    right_tk_img = load_process_image(self, right_img_frame, conn_value_2)
    self.status_img_references = [left_tk_img, right_tk_img]


def load_process_image(
    self: CableTesterApplication,
    img_frame,
    conn_value=None,
):

    # Загружаем изображения для статуса (используем заглушки, замените на свои изображения)
    _img = Image.new("RGB", DEFAULT_IMAGE_SIZE, color="white")

    connector = str(conn_value).split(":")[0]

    if connector:
        conn_im_path = find_image_for_connector(self, connector)
        if conn_im_path:
            try:
                _img = Image.open(
                    os.path.join(DATA_PATH, conn_im_path.lower())
                )
                _img = resize_image(_img, *DEFAULT_IMAGE_SIZE)
            except Exception as e:
                self.log_error(f"Can't load image {conn_im_path}: {str(e)}")

    _tk_img = ImageTk.PhotoImage(_img)

    # Создаем контейнеры для изображений и текста, прижатые к низу
    _container = ttk.Frame(img_frame)
    _container.pack(side="bottom", pady=5)

    # Отображаем изображения
    img_label = ttk.Label(_container, image=_tk_img)
    img_label.pack(padx=10, pady=2)
    ttk.Label(
        _container, text=str(conn_value), font=("Arial", 16, "bold")
    ).pack(padx=10, pady=2)

    return _tk_img
