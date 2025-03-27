import os
from PIL import Image

from app import CableTesterApplication, DATA_PATH


def find_images(self: CableTesterApplication):
    """Ищет изображения в директории %DATA_PATH%"""
    image_paths = []

    # Расширения файлов изображений, которые мы ищем
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    if os.path.isdir(DATA_PATH):
        for file in os.listdir(DATA_PATH):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_paths.append(os.path.join(DATA_PATH, file))

        # Ограничиваем количество изображений (опционально)
        if len(image_paths) > 5:
            self.log_warning(f"Found {len(image_paths)} images, showing first 5")
            image_paths = image_paths[:5]
        else:
            self.log(f"Found {len(image_paths)} images")
    else:
        self.log_error(f"Have no data dir {DATA_PATH}")

    return image_paths


def load_and_resize_image(image_path, width, height):
    """Загружает и изменяет размер изображения"""
    # from PIL import Image

    if (width == 0) or (height == 0):
        return None

    # Загружаем изображение
    img = Image.open(image_path)

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
