# library/student.py
from datetime import datetime
from .database import Database

class Student:
    def __init__(self, student_id, student_name, student_password, student_batch):
        self.student_id = student_id
        self.student_name = student_name
        self.student_password = student_password
        self.student_batch = student_batch

    def __str__(self):
        return (
            f"Student ID    : {self.student_id}\n"
            f"Student Name  : {self.student_name}\n"
            f"Student Batch : {self.student_batch}\n"
        )

    def view_books(self):
        db = Database()
        return db.view_books()

    def borrow_book(self, book_id):
        db = Database()
        return db.borrow_book(self, book_id)

    def return_book(self, book_id):
        db = Database()
        return db.return_book(self, book_id)

    def check_fines(self):
        """
        Sum of:
          - Automatic late fines based on borrowed time
          - Any manual fines stored in manual_fines.csv
        """
        db = Database()
        book_list = db.get_all_borrowed_books(self)
        total = 0

        # Automatic fines
        if book_list:
            for book in book_list:
                borrow_date = datetime.strptime(book.borrow_date, '%d-%m-%Y')
                current_date = datetime.now()
                d = (current_date - borrow_date).days
                auto_fine = (d // 7) * 20
                total += auto_fine

        # Manual fines
        manual_total = db.get_manual_fines_for_student(self.student_id)
        total += manual_total

        return total

    def deregister(self):
        db = Database()
        # must have no borrowed books
        borrowed = db.get_all_borrowed_books(self)
        if borrowed:
            return False

        # must have zero fines
        if self.check_fines() > 0:
            return False

        db.deregister(self)
        return True
