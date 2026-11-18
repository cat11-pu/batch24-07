import ntpath
import os
import tempfile

ALLOWED_EXTENSIONS = {".png", ".jpg"}
MAX_SIZE = 1024

_MIME_TYPES = {
    ".png": {"image/png"},
    ".jpg": {"image/jpeg"},
}

_MAGIC_BYTES = {
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
}


def _filename_value(filename):
    try:
        name = os.fspath(filename)
    except TypeError as exc:
        raise ValueError("filename must be text") from exc
    if not isinstance(name, str):
        raise ValueError("filename must be text")
    if not name or "\x00" in name:
        raise ValueError("invalid filename")
    return name


def _validate_filename(filename):
    name = _filename_value(filename)
    if "/" in name or "\\" in name:
        raise ValueError("filename must not contain path separators")
    if os.path.isabs(name) or ntpath.splitdrive(name)[0]:
        raise ValueError("filename must not be an absolute path")
    if name in (".", ".."):
        raise ValueError("invalid filename")
    return name


def _normalize_content_type(content_type):
    if not isinstance(content_type, str):
        return None
    return content_type.split(";", 1)[0].strip().lower()


def _content_bytes(content):
    if not isinstance(content, (bytes, bytearray, memoryview)):
        return None
    return bytes(content)


def validate_upload(filename, content, content_type=None):
    try:
        name = _validate_filename(filename)
    except (TypeError, ValueError):
        return False

    extension = os.path.splitext(name)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False

    data = _content_bytes(content)
    if data is None or not data or len(data) > MAX_SIZE:
        return False

    if content_type is not None:
        mime_type = _normalize_content_type(content_type)
        if mime_type not in _MIME_TYPES[extension]:
            return False

    if not data.startswith(_MAGIC_BYTES[extension]):
        return False

    return True


def safe_filename(filename):
    name = _filename_value(filename).replace("\\", "/")
    _, name = ntpath.splitdrive(name)
    name = name.rsplit("/", 1)[-1]
    if name in ("", ".", ".."):
        raise ValueError("invalid filename")
    return name


def save_upload(filename, content, dest_dir, content_type=None):
    if not validate_upload(filename, content, content_type):
        raise ValueError("invalid upload")

    name = safe_filename(filename)
    dest = os.fsdecode(os.fspath(dest_dir))
    if not dest or "\x00" in dest:
        raise ValueError("invalid destination")

    os.makedirs(dest, exist_ok=True)
    root = os.path.realpath(dest)
    if not os.path.isdir(root):
        raise ValueError("destination is not a directory")

    final_path = os.path.join(root, name)
    if os.path.commonpath((root, os.path.abspath(final_path))) != root:
        raise ValueError("destination escapes target directory")

    fd, temporary_path = tempfile.mkstemp(prefix=".upload-", dir=root)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
        os.replace(temporary_path, final_path)
    except BaseException:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise

    return final_path
