# library/librarian.py
from datetime import datetime
from .database import Database
from .book import Book

class Librarian:
    def __init__(self, librarian_id, librarian_name, librarian_password):
        self.librarian_id = librarian_id
        self.librarian_name = librarian_name
        self.librarian_password = librarian_password

    def __str__(self):
        return (
            f"Librarian ID   : {self.librarian_id}\n"
            f"Librarian Name : {self.librarian_name}\n"
        )

    def view_books(self):
        db = Database()
        return db.view_books()

    def add_books(self, book_name, book_author, book_publisher, book_publish_date, book_copies):
        db = Database()
        last_book_id = db.get_last_book_id()
        try:
            new_book_id = int(last_book_id) + 1
        except:
            new_book_id = 1

        if not book_copies:
            book_copies = '1'
        try:
            copies_int = int(book_copies)
            if copies_int < 0:
                raise ValueError("Book copies cannot be negative.")
        except:
            copies_int = 1

        book_obj = Book(
            book_id=str(new_book_id),
            book_name=book_name.strip(),
            book_author=book_author.strip(),
            book_publisher=book_publisher.strip(),
            book_publish_date=book_publish_date.strip(),
            book_copies=str(copies_int)
        )
        db.save_book(book_obj)
        return book_obj

    def update_book(self, book_id, book_name, book_author, book_publisher, book_publish_date, book_copies):
        db = Database()
        if not book_copies:
            book_copies = '1'

        book_obj = Book(
            book_id=book_id.strip(),
            book_name=book_name.strip(),
            book_author=book_author.strip(),
            book_publisher=book_publisher.strip(),
            book_publish_date=book_publish_date.strip(),
            book_copies=book_copies.strip()
        )
        status = db.update_book(book_obj)
        return status, book_obj

    def remove_book(self, book_id):
        db = Database()
        return db.remove_book(book_id.strip())
