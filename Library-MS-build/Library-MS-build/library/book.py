# library/book.py
class Book:
    def __init__(
        self,
        book_id,
        book_name,
        book_author,
        book_publisher,
        book_publish_date,
        book_availability_status='True',
        book_copies='1',
        borrow_date=None
    ):
        self.book_id = book_id
        self.book_name = book_name or 'Unknown'
        self.book_author = book_author or 'Unknown'
        self.book_publisher = book_publisher or 'Unknown'
        self.book_publish_date = book_publish_date or 'Unknown'
        self.book_copies = book_copies

        # Determine availability
        if int(self.book_copies) > 0:
            book_availability_status = 'True'
        else:
            book_availability_status = 'False'

        self.book_availability_status = book_availability_status
        self.borrow_date = borrow_date

    def __str__(self):
        return (
            f"Book ID           : {self.book_id}\n"
            f"Book Name         : {self.book_name}\n"
            f"Book Author       : {self.book_author}\n"
            f"Book Publisher    : {self.book_publisher}\n"
            f"Book Publish Date : {self.book_publish_date}\n"
            f"Book Avail status : {self.book_availability_status}\n"
            f"Book Copies       : {self.book_copies}\n"
        )
