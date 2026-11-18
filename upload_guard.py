import os

ALLOWED_EXTENSIONS = {".png", ".jpg"}
MAX_SIZE = 1024


def validate_upload(filename, content, content_type=None):
    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False
    return True


def safe_filename(filename):
    return filename


def save_upload(filename, content, dest_dir):
    path = os.path.join(dest_dir, safe_filename(filename))
    with open(path, "wb") as handle:
        handle.write(content)
    return path
