import os

import pytest

import upload_guard as ug


def test_1_oversized_content_is_rejected():
    assert ug.validate_upload("a.png", b"x" * 2048) is False


def test_2_content_over_max_size_is_rejected():
    assert ug.validate_upload("a.png", b"x" * (ug.MAX_SIZE + 1)) is False


def test_3_empty_content_is_rejected():
    assert ug.validate_upload("a.png", b"") is False


def test_4_text_html_content_type_is_rejected():
    assert ug.validate_upload("a.png", b"\x89PNG\r\n\x1a\n", "text/html") is False


def test_5_content_type_must_match_extension():
    assert ug.validate_upload("a.png", b"\x89PNG\r\n\x1a\n", "image/jpeg") is False


def test_6_magic_bytes_must_match_extension():
    assert ug.validate_upload("a.png", b"MZ\x90\x00") is False


def test_7_parent_traversal_filename_is_rejected():
    assert ug.validate_upload("../evil.png", b"\x89PNG\r\n\x1a\n") is False


def test_8_absolute_filename_is_rejected():
    assert ug.validate_upload("/tmp/evil.png", b"\x89PNG\r\n\x1a\n") is False


def test_9_null_byte_filename_is_rejected():
    assert ug.validate_upload("evil\x00.png", b"\x89PNG\r\n\x1a\n") is False


def test_10_slash_filename_is_rejected():
    assert ug.validate_upload("sub/evil.png", b"\x89PNG\r\n\x1a\n") is False


def test_11_backslash_filename_is_rejected():
    assert ug.validate_upload("..\\evil.png", b"\x89PNG\r\n\x1a\n") is False


def test_12_drive_letter_filename_is_rejected():
    assert ug.validate_upload("C:\\evil.png", b"\x89PNG\r\n\x1a\n") is False


def test_13_safe_filename_uses_basename():
    assert ug.safe_filename("../x.png") == "x.png"


def test_14_safe_filename_strips_absolute_path():
    assert ug.safe_filename("/etc/x.png") == "x.png"


def test_15_save_upload_stays_inside_destination(tmp_path):
    dest = tmp_path / "dest"
    dest.mkdir()
    with pytest.raises(ValueError):
        ug.save_upload("../escape.png", b"\x89PNG\r\n\x1a\n", str(dest))
