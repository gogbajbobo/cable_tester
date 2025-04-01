import os
from PIL import Image, ImageTk

from app import CableTesterApplication, DATA_PATH


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
                self.loaded_images[i] = load_image(im_path)
            except Exception as e:
                self.log_error(f"Can't load image {im_file}: {str(e)}")
                self.loaded_images[i] = None

        self.log(f"Found {len(image_paths)} images")

    return image_paths


def load_image(image_path) -> Image.Image:
    img = Image.open(image_path)
    return img


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
