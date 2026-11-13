from manuskript.util import parseFilenameFromURL


def test_filename_with_spaces():
    uri = "file:///home/user/Documents/Writing/The%20Mill.msk"
    expected = "/home/user/Documents/Writing/The Mill.msk"

    assert parseFilenameFromURL(uri) == expected


def test_filename_without_spaces():
    uri = "file:///home/user/Documents/Writing/Test.msk"
    expected = "/home/user/Documents/Writing/Test.msk"

    assert parseFilenameFromURL(uri) == expected


def test_reject_http_url():
    assert parseFilenameFromURL("https://example.com/test.msk") is None


def test_filename_with_special_characters():
    uri = "file:///home/user/Documents/Writing/Romance%20%26%20Drama.msk"
    expected = "/home/user/Documents/Writing/Romance & Drama.msk"

    assert parseFilenameFromURL(uri) == expected
