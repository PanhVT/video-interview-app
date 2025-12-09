import re

from app.core.time_utils import sanitize_name, make_folder_name


def test_ascii_name():
    assert sanitize_name("Alice Bob") == "alice_bob"


def test_diacritics():
    assert sanitize_name("Hồng Anh") == "hong_anh"


def test_hyphen_and_punct():
    assert sanitize_name("Nguyễn-Văn") == "nguyen_van"


def test_non_latin_fallback():
    res = sanitize_name("张伟")
    assert res.startswith("user_")
    assert len(res) <= 48


def test_empty_input_returns_empty():
    assert sanitize_name("") == ""


def test_long_name_truncation():
    long_name = "a" * 100
    res = sanitize_name(long_name)
    assert len(res) <= 48


def test_make_folder_name_format():
    folder = make_folder_name("Alice")
    # Expect at least 6 underscore-separated parts: DD MM YYYY HH mm name
    parts = re.split(r"_+", folder)
    assert len(parts) >= 6
