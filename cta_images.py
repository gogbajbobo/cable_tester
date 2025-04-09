import os
from tkinter import ttk
from PIL import Image, ImageTk

from app import CableTesterApplication, DATA_PATH

DEFAULT_IMAGE_SIZE = (100, 100)


def find_images(self: CableTesterApplication):
    """Ищет изображения в директории %DATA_PATH%"""
    image_paths = []

    if "Изображение" in self.table_data.columns:

        images = self.table_data["Изображение"].dropna().to_list()
        self.log(f"self.table_data['Изображение']\n{images}")

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
    left_im_path=None,
    right_im_path=None,
):
    left_tk_img = load_process_image(self, left_img_frame, left_im_path)
    right_tk_img = load_process_image(self, right_img_frame, right_im_path)
    self.status_img_references = [left_tk_img, right_tk_img]


def load_process_image(
    self: CableTesterApplication,
    img_frame,
    im_path=None,
):
    # Загружаем изображения для статуса (используем заглушки, замените на свои изображения)
    try:
        if im_path:
            _img = Image.open(os.path.join(DATA_PATH, im_path.lower()))
        else:
            _img = Image.new("RGB", DEFAULT_IMAGE_SIZE, color="white")

        _tk_img = ImageTk.PhotoImage(_img)

        # Отображаем изображения
        img_label = ttk.Label(img_frame, image=_tk_img)
        img_label.pack(padx=10, pady=10)
        ttk.Label(img_frame, text=str(im_path)).pack()

        return _tk_img

    except Exception as e:
        self.log(f"Error creating status images: {str(e)}")
        ttk.Label(img_frame, text="Image not available").pack(padx=10, pady=10)
        return None
