"""Small library circulation system using SQLite."""
from __future__ import annotations
import sqlite3
from pathlib import Path

class Library:
    def __init__(self, db_path: str | Path = "library.db"):
        self.db_path = str(db_path)
        with self._connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS books(
              id INTEGER PRIMARY KEY AUTOINCREMENT, isbn TEXT UNIQUE,
              title TEXT NOT NULL, author TEXT NOT NULL,
              total_copies INTEGER NOT NULL CHECK(total_copies >= 0));
            CREATE TABLE IF NOT EXISTS members(
              id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE);
            CREATE TABLE IF NOT EXISTS loans(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              book_id INTEGER NOT NULL REFERENCES books(id),
              member_id INTEGER NOT NULL REFERENCES members(id),
              issued_on TEXT NOT NULL, due_on TEXT NOT NULL, returned_on TEXT);
            """)

    def _connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def add_book(self, title: str, author: str, copies: int = 1, isbn: str = "") -> int:
        if not title.strip() or not author.strip() or copies < 1:
            raise ValueError("Title, author and at least one copy are required.")
        with self._connect() as con:
            cur = con.execute("INSERT INTO books(isbn,title,author,total_copies) VALUES(?,?,?,?)",
                              (isbn.strip() or None, title.strip(), author.strip(), copies))
            return int(cur.lastrowid)

    def register_member(self, name: str, email: str = "") -> int:
        if not name.strip():
            raise ValueError("Member name is required.")
        with self._connect() as con:
            cur = con.execute("INSERT INTO members(name,email) VALUES(?,?)",
                              (name.strip(), email.strip() or None))
            return int(cur.lastrowid)

    def search_books(self, term: str = ""):
        with self._connect() as con:
            return con.execute("""SELECT b.*,
              b.total_copies - (SELECT COUNT(*) FROM loans l
                WHERE l.book_id=b.id AND l.returned_on IS NULL) AS available
              FROM books b WHERE b.title LIKE ? OR b.author LIKE ? ORDER BY b.title""",
              (f"%{term.strip()}%", f"%{term.strip()}%")).fetchall()

    def issue_book(self, book_id: int, member_id: int, issued_on: str, due_on: str) -> int:
        if not issued_on.strip() or not due_on.strip() or due_on < issued_on:
            raise ValueError("A valid issue date and due date are required.")
        with self._connect() as con:
            book = con.execute("""SELECT total_copies,
              (SELECT COUNT(*) FROM loans WHERE book_id=? AND returned_on IS NULL) AS active
              FROM books WHERE id=?""", (book_id, book_id)).fetchone()
            if book is None:
                raise ValueError("Book not found.")
            if book["active"] >= book["total_copies"]:
                raise ValueError("No copies are currently available.")
            cur = con.execute("INSERT INTO loans(book_id,member_id,issued_on,due_on) VALUES(?,?,?,?)",
                              (book_id, member_id, issued_on, due_on))
            return int(cur.lastrowid)

    def return_book(self, loan_id: int, returned_on: str):
        if not returned_on.strip():
            raise ValueError("Return date is required.")
        with self._connect() as con:
            cur = con.execute("""UPDATE loans SET returned_on=?
              WHERE id=? AND returned_on IS NULL""", (returned_on, loan_id))
            if cur.rowcount == 0:
                raise ValueError("Active loan not found or already returned.")

    def list_active_loans(self):
        with self._connect() as con:
            return con.execute("""SELECT l.*, b.title, m.name AS member_name
              FROM loans l JOIN books b ON b.id=l.book_id
              JOIN members m ON m.id=l.member_id
              WHERE l.returned_on IS NULL ORDER BY l.due_on""").fetchall()

def main():
    library = Library()
    print("Library Management System")
    while True:
        print("\n1 Add book  2 Register member  3 Search books  4 Issue book  5 Return book  6 Active loans  0 Exit")
        choice = input("> ").strip()
        try:
            if choice == "1":
                print("Book ID:", library.add_book(input("Title: "), input("Author: "),
                      int(input("Copies: ") or "1"), input("ISBN (optional): ")))
            elif choice == "2":
                print("Member ID:", library.register_member(input("Name: "), input("Email: ")))
            elif choice == "3":
                for row in library.search_books(input("Search: ")):
                    print(dict(row))
            elif choice == "4":
                loan = library.issue_book(int(input("Book ID: ")), int(input("Member ID: ")),
                                          input("Issued YYYY-MM-DD: "), input("Due YYYY-MM-DD: "))
                print("Loan ID:", loan)
            elif choice == "5":
                library.return_book(int(input("Loan ID: ")), input("Returned YYYY-MM-DD: "))
                print("Book returned.")
            elif choice == "6":
                for row in library.list_active_loans():
                    print(dict(row))
            elif choice == "0":
                break
            else:
                print("Choose one of the listed options.")
        except (ValueError, sqlite3.IntegrityError) as exc:
            print("Could not complete operation:", exc)

if __name__ == "__main__":
    main()
