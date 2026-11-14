import pytest
from library import Library

def test_issue_and_return_book(tmp_path):
    lib = Library(tmp_path / "library.db")
    book = lib.add_book("Data Engineering 101", "A. Author", copies=1)
    member = lib.register_member("Demo Reader", "reader@example.test")
    loan = lib.issue_book(book, member, "2026-11-01", "2026-11-15")
    assert lib.search_books("Data")[0]["available"] == 0
    with pytest.raises(ValueError):
        lib.issue_book(book, member, "2026-11-02", "2026-11-16")
    lib.return_book(loan, "2026-11-10")
    assert lib.search_books("Data")[0]["available"] == 1

def test_reject_invalid_book(tmp_path):
    lib = Library(tmp_path / "library.db")
    with pytest.raises(ValueError):
        lib.add_book("", "Nobody")
