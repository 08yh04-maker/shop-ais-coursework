import os
import uuid

from werkzeug.utils import secure_filename

from flask import current_app

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def save_image(file) -> str | None:
    """Сохраняет загруженный файл и возвращает его имя. Если файла нет — None."""
    if not file or not file.filename:
        return None

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None

    # Уникальное имя: uuid + расширение
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return filename


def delete_image(filename: str | None) -> None:
    """Удаляет файл из папки uploads, если он существует."""
    if not filename:
        return
    path = os.path.join(current_app.root_path, "static", "uploads", filename)
    if os.path.exists(path):
        os.remove(path)