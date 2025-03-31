import os
from PIL import Image

from app import CableTesterApplication, DATA_PATH


def find_images(self: CableTesterApplication):
    """Ищет изображения в директории %DATA_PATH%"""
    image_paths = []

    if "Изображение" in self.table_data.columns:

        images = self.table_data["Изображение"].dropna().to_list()
        self.log(f"self.table_data['Изображение']\n{images}")

        for im_file in images:
            image_paths.append(os.path.join(DATA_PATH, im_file.lower()))

        self.log(f"Found {len(image_paths)} images")

    return image_paths


def load_image(image_path):
    img = Image.open(image_path)
    return img


def resize_image(img, width, height):
    if (width == 0) or (height == 0):
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


def load_and_resize_image(image_path, width, height):
    img = load_image(image_path)
    return resize_image(img, width, height)
