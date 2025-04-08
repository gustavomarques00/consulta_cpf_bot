from utils.parse_date import parse_date


def test_parse_date():
    """
    Tests the `parse_date` function to ensure it correctly parses various date formats into a standardized format (DD/MM/YYYY HH:MM:SS).
    """
    assert parse_date("2023-10-01") == "01/10/2023 00:00:00"
    assert parse_date("2023-10-01 15:30:00") == "01/10/2023 15:30:00"


def test_parse_date_valid_formats():
    """
    Test `parse_date` with valid date formats.
    """
    assert parse_date("2023-10-01 15:30:00") == "01/10/2023 15:30:00"
    assert parse_date("2023-10-01") == "01/10/2023 00:00:00"


def test_parse_date_invalid_format():
    """
    Test `parse_date` with an invalid date format.
    """
    try:
        parse_date("Invalid date")
    except ValueError as e:
        assert str(e) == "Date format not recognized: Invalid date"


def test_parse_date_edge_cases():
    """
    Test `parse_date` with edge cases.
    """
    assert parse_date("1900-01-01") == "01/01/1900 00:00:00"
    assert parse_date("9999-12-31 23:59:59") == "31/12/9999 23:59:59"


def test_parse_date_with_extra_whitespace():
    """
    Test `parse_date` with extra whitespace in the input.
    """
    assert parse_date(" 2023-10-01 ") == "01/10/2023 00:00:00"
    assert parse_date("  2023-10-01 15:30:00  ") == "01/10/2023 15:30:00"


def test_parse_date_with_different_separators():
    """
    Test `parse_date` with different separators in the input.
    """
    try:
        parse_date("2023/10/01")
    except ValueError as e:
        assert str(e) == "Date format not recognized: 2023/10/01"


def test_parse_date_with_empty_string():
    """
    Test `parse_date` with an empty string.
    """
    try:
        parse_date("")
    except ValueError as e:
        assert str(e) == "Date format not recognized: "


def test_parse_date_with_none():
    """
    Test `parse_date` with None as input.
    """
    try:
        parse_date(None)
    except ValueError as e:
        assert str(e) == "Date format not recognized: None"