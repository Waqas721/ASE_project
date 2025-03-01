# library/database.py
import csv
import datetime
import os

from .book import Book

class Database:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Database, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.books_file_path = os.path.join('data', 'books.csv')
        self.students_file_path = os.path.join('data', 'students.csv')
        self.librarian_file_path = os.path.join('data', 'librarian.csv')
        self.transactions_file_path = os.path.join('data', 'all_transactions.csv')
        self.borrows_file_path = os.path.join('data', 'all_borrows.csv')
        self.manual_fines_file_path = os.path.join('data', 'manual_fines.csv')

    # ~~~ Book methods ~~~
    def view_books(self):
        books = []
        try:
            with open(self.books_file_path, mode='r', encoding='utf-8') as file:
                csv_file = csv.reader(file)
                for lines in csv_file:
                    if len(lines) < 7:
                        continue
                    book_obj = Book(*lines)
                    books.append(book_obj)
        except FileNotFoundError:
            pass
        return books

    def save_book(self, book_obj):
        data = [
            book_obj.book_id,
            book_obj.book_name,
            book_obj.book_author,
            book_obj.book_publisher,
            book_obj.book_publish_date,
            book_obj.book_availability_status,
            book_obj.book_copies
        ]
        with open(self.books_file_path, mode='a', newline='', encoding='utf-8') as file_obj:
            csv.writer(file_obj).writerow(data)

    def update_book(self, book_obj):
        success = False
        with open(self.books_file_path, mode='r', encoding='utf-8') as file,\
             open('temp_books.csv', mode='w', newline='', encoding='utf-8') as temp_file:

            books = csv.reader(file)
            temp_books = csv.writer(temp_file)
            for row in books:
                if len(row) < 7:
                    temp_books.writerow(row)
                    continue
                if row[0] == book_obj.book_id and not success:
                    success = True
                    data = [
                        book_obj.book_id,
                        book_obj.book_name,
                        book_obj.book_author,
                        book_obj.book_publisher,
                        book_obj.book_publish_date,
                        book_obj.book_availability_status,
                        book_obj.book_copies
                    ]
                    temp_books.writerow(data)
                else:
                    temp_books.writerow(row)

        if success:
            os.remove(self.books_file_path)
            os.rename('temp_books.csv', self.books_file_path)
        else:
            os.remove('temp_books.csv')
        return success

    def remove_book(self, book_id):
        success = False
        removed_book = None
        with open(self.books_file_path, mode='r', encoding='utf-8') as file,\
             open('temp_books.csv', mode='w', newline='', encoding='utf-8') as temp_file:

            books = csv.reader(file)
            temp_books = csv.writer(temp_file)
            for row in books:
                if len(row) < 7:
                    temp_books.writerow(row)
                    continue
                if row[0] == book_id and not success:
                    success = True
                    removed_book = row
                    continue
                temp_books.writerow(row)

        if success:
            os.remove(self.books_file_path)
            os.rename('temp_books.csv', self.books_file_path)
            return Book(*removed_book)
        else:
            os.remove('temp_books.csv')
            return False

    def get_last_book_id(self):
        last = []
        try:
            with open(self.books_file_path, mode='r', encoding='utf-8') as file:
                csv_file = csv.reader(file)
                for lines in csv_file:
                    if len(lines) > 0:
                        last = lines
            return last[0] if last else '0'
        except FileNotFoundError:
            return '0'

    # ~~~ Student methods ~~~
    def authenticate(self, stud_id, stud_password):
        from .student import Student
        try:
            with open(self.students_file_path, mode='r', encoding='utf-8') as file:
                csv_file = csv.reader(file)
                for row in csv_file:
                    if len(row) < 4:
                        continue
                    if row[0] == stud_id and row[2] == stud_password:
                        return Student(row[0], row[1], row[2], row[3])
        except FileNotFoundError:
            pass
        return False

    def fetch_last_student_id(self):
        last = []
        try:
            with open(self.students_file_path, mode='r', encoding='utf-8') as file:
                csv_file = csv.reader(file)
                for row in csv_file:
                    if len(row) > 0:
                        last = row
            return last[0] if last else 'st0000'
        except FileNotFoundError:
            return 'st0000'

    def save_student(self, stud_obj):
        data = [stud_obj.student_id, stud_obj.student_name, stud_obj.student_password, stud_obj.student_batch]
        with open(self.students_file_path, mode='a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow(data)

    def deregister(self, student_obj):
        with open(self.students_file_path, mode='r', newline='', encoding='utf-8') as file_read_obj,\
             open('temp_students.csv', mode='w', newline='', encoding='utf-8') as file_write_object:

            csv_reader = csv.reader(file_read_obj)
            csv_writer = csv.writer(file_write_object)
            for row in csv_reader:
                if len(row) > 0 and row[0] == student_obj.student_id:
                    continue
                csv_writer.writerow(row)

        os.remove(self.students_file_path)
        os.rename('temp_students.csv', self.students_file_path)

    # ~~~ Librarian methods ~~~
    def lib_authenticate(self, lib_id, lib_pass):
        from .librarian import Librarian
        try:
            with open(self.librarian_file_path, mode='r', encoding='utf-8') as file:
                csv_file = csv.reader(file)
                for row in csv_file:
                    if len(row) < 3:
                        continue
                    if row[0] == lib_id and row[2] == lib_pass:
                        return Librarian(row[0], row[1], row[2])
        except FileNotFoundError:
            pass
        return False

    def fetch_last_librarian_id(self):
        last = []
        try:
            with open(self.librarian_file_path, mode='r', encoding='utf-8') as file:
                csv_file = csv.reader(file)
                for row in csv_file:
                    if len(row) > 0:
                        last = row
            return last[0] if last else 'lb0000'
        except FileNotFoundError:
            return 'lb0000'

    def save_librarian(self, lib_obj):
        data = [lib_obj.librarian_id, lib_obj.librarian_name, lib_obj.librarian_password]
        with open(self.librarian_file_path, mode='a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow(data)

    # ~~~ Borrow/Return methods ~~~
    def borrow_book(self, stud_obj, book_id):
        success = False
        with open(self.books_file_path, mode='r', encoding='utf-8') as file,\
             open('temp_books.csv', mode='w', newline='', encoding='utf-8') as temp_file:

            books = csv.reader(file)
            temp_books = csv.writer(temp_file)
            for row in books:
                if len(row) < 7:
                    temp_books.writerow(row)
                    continue
                if row[0] == book_id:
                    try:
                        copies = int(row[6])
                        if copies >= 1:
                            row[6] = str(copies - 1)
                            if copies - 1 <= 0:
                                row[5] = 'False'
                            success = row
                    except:
                        pass
                temp_books.writerow(row)

        if success:
            os.remove(self.books_file_path)
            os.rename('temp_books.csv', self.books_file_path)
            book_obj = Book(*success)
            trans_id, today_date = self.write_to_transaction_and_borrow_file(stud_obj, book_obj, 'b')
            return (trans_id, today_date, book_obj)
        else:
            os.remove('temp_books.csv')
            return False

    def return_book(self, stud_obj, book_id):
        success = False
        with open(self.books_file_path, mode='r', encoding='utf-8') as file,\
             open('temp_books.csv', mode='w', newline='', encoding='utf-8') as temp_file:

            books = csv.reader(file)
            temp_books = csv.writer(temp_file)
            for row in books:
                if len(row) < 7:
                    temp_books.writerow(row)
                    continue
                if row[0] == book_id and not success:
                    try:
                        copies = int(row[6])
                        row[6] = str(copies + 1)
                        row[5] = "True"
                        success = row
                    except:
                        pass
                temp_books.writerow(row)

        if success:
            os.remove(self.books_file_path)
            os.rename('temp_books.csv', self.books_file_path)
            book_obj = Book(*success)
            trans_id = self.write_to_transaction_and_borrow_file(stud_obj, book_obj, 'r')
            self.update_all_borrows_file(stud_obj, book_obj)
            return (trans_id, book_obj)
        else:
            os.remove('temp_books.csv')
            return False

    def get_all_borrowed_books(self, stud_obj):
        """
        Returns a list of Book objects that a given student borrowed
        + sets borrow_date in each object.
        """
        book_list = []
        try:
            with open(self.borrows_file_path, mode='r', encoding='utf-8') as borrow_file:
                borrow_file_reader = csv.reader(borrow_file)
                for line in borrow_file_reader:
                    if len(line) < 4:
                        continue
                    if line[1] == stud_obj.student_id:
                        borrowed_book_id = line[2]
                        borrowed_date = line[3]
                        with open(self.books_file_path, mode='r', encoding='utf-8') as book_file:
                            book_reader = csv.reader(book_file)
                            for row in book_reader:
                                if len(row) < 7:
                                    continue
                                if row[0] == borrowed_book_id:
                                    book_obj = Book(*row)
                                    book_obj.borrow_date = borrowed_date
                                    book_list.append(book_obj)
        except FileNotFoundError:
            pass
        return book_list

    def update_all_borrows_file(self, stud_obj, book_obj):
        status = False
        with open(self.borrows_file_path, mode='r', encoding='utf-8') as borrow_file,\
             open('temp_borrows.csv', mode='w', newline='', encoding='utf-8') as temp_file:

            borrow_reader = csv.reader(borrow_file)
            temp_writer = csv.writer(temp_file)
            for row in borrow_reader:
                if len(row) < 4:
                    temp_writer.writerow(row)
                    continue
                if row[1] == stud_obj.student_id and row[2] == book_obj.book_id and not status:
                    status = True
                    continue
                temp_writer.writerow(row)

        os.remove(self.borrows_file_path)
        os.rename('temp_borrows.csv', self.borrows_file_path)

    def write_to_transaction_and_borrow_file(self, stud_obj, book_obj, trans_type):
        transaction_id = self.create_transaction_id()
        today_date = self.get_current_date()

        # all_transactions
        with open(self.transactions_file_path, mode='a', newline='', encoding='utf-8') as file:
            row = [transaction_id, stud_obj.student_id, book_obj.book_id, today_date, trans_type]
            csv.writer(file).writerow(row)

        if trans_type == 'b':
            with open(self.borrows_file_path, mode='a', newline='', encoding='utf-8') as borrow_file:
                b_row = [transaction_id, stud_obj.student_id, book_obj.book_id, today_date]
                csv.writer(borrow_file).writerow(b_row)

        if trans_type == 'r':
            return transaction_id
        else:
            return (transaction_id, today_date)

    def get_all_transactions(self):
        """
        Return a list of [trans_id, student_id, book_id, date, trans_type]
        from 'all_transactions.csv'
        """
        transactions = []
        try:
            with open(self.transactions_file_path, mode='r', encoding='utf-8') as file:
                csv_file = csv.reader(file)
                for row in csv_file:
                    if len(row) >= 5:
                        transactions.append(row)
        except FileNotFoundError:
            pass
        return transactions

    def get_all_borrowed_records(self):
        """
        Return a list of [transaction_id, student_id, book_id, borrow_date]
        from 'all_borrows.csv'
        """
        borrowed_list = []
        try:
            with open(self.borrows_file_path, mode='r', encoding='utf-8') as f:
                csv_file = csv.reader(f)
                for row in csv_file:
                    if len(row) >= 4:
                        borrowed_list.append(row)
        except FileNotFoundError:
            pass
        return borrowed_list

    def fetch_last_transaction_id(self):
        last = []
        try:
            with open(self.transactions_file_path, mode='r', encoding='utf-8') as file:
                csv_file = csv.reader(file)
                for row in csv_file:
                    if len(row) > 0:
                        last = row
            return last[0] if last else 'tr0000'
        except FileNotFoundError:
            return 'tr0000'

    def get_current_date(self):
        return datetime.datetime.now().strftime("%d-%m-%Y")

    def create_transaction_id(self):
        try:
            returned_id = self.fetch_last_transaction_id()
            num_part = int(returned_id[2:]) + 1
            return f"tr{num_part:04d}"
        except:
            return 'tr0001'

    # ~~~ Manual Fines ~~~
    def add_manual_fine(self, student_id, fine_amount, reason):
        today_str = self.get_current_date()
        with open(self.manual_fines_file_path, mode='a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([student_id, fine_amount, reason, today_str])

    def get_manual_fines_for_student(self, student_id):
        total_fine = 0
        try:
            with open(self.manual_fines_file_path, mode='r', encoding='utf-8') as f:
                csv_file = csv.reader(f)
                for row in csv_file:
                    if len(row) < 2:
                        continue
                    if row[0] == student_id:
                        try:
                            fine_val = float(row[1])
                            total_fine += fine_val
                        except:
                            pass
        except FileNotFoundError:
            pass
        return total_fine
