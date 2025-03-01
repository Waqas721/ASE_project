# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import timedelta

from library.database import Database
from library.student import Student
from library.librarian import Librarian

app = Flask(__name__)
app.secret_key = 'some_secret_key_for_session'

# Make sessions permanent (won't expire until logout)
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(days=365)  # adjust as needed

# Ensure data folder and CSVs exist
if not os.path.exists('data'):
    os.makedirs('data')

for fname in [
    'all_borrows.csv',
    'all_transactions.csv',
    'books.csv',
    'librarian.csv',
    'students.csv',
    'manual_fines.csv'
]:
    fpath = os.path.join('data', fname)
    if not os.path.exists(fpath):
        open(fpath, 'w').close()

# ================================
#              HOME
# ================================
@app.route('/')
def home():
    return render_template('index.html')


# ================================
#         STUDENT ROUTES
# ================================

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password1 = request.form.get('password1', '').strip()
        password2 = request.form.get('password2', '').strip()
        batch = request.form.get('batch', '').strip()

        if not name or not password1 or not password2 or not batch:
            flash("All fields are required!", "error")
            return redirect(url_for('student_register'))

        if password1 != password2:
            flash("Passwords do not match!", "error")
            return redirect(url_for('student_register'))

        db = Database()
        last_id = db.fetch_last_student_id()
        try:
            new_id_num = int(last_id[2:]) + 1
        except:
            new_id_num = 1
        new_id_str = f"st{new_id_num:04d}"

        stud = Student(
            student_id=new_id_str,
            student_name=name,
            student_password=password1,
            student_batch=batch
        )
        db.save_student(stud)
        flash(f"Student registered successfully with ID {new_id_str}", "success")
        return redirect(url_for('student_login'))
    return render_template('student_register.html')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        password = request.form.get('password', '').strip()

        if not student_id or not password:
            flash("Please fill in all fields!", "error")
            return redirect(url_for('student_login'))

        db = Database()
        stud_obj = db.authenticate(student_id, password)
        if stud_obj:
            session.permanent = True
            session['student_id'] = stud_obj.student_id
            session['student_name'] = stud_obj.student_name
            # Clear any librarian session
            session.pop('lib_id', None)
            session.pop('lib_name', None)

            flash("Student login successful!", "success")
            return redirect(url_for('student_dashboard'))
        else:
            flash("Authentication failed. Check ID/Password!", "error")
            return redirect(url_for('student_login'))

    return render_template('student_login.html')


@app.route('/student/dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))
    return render_template('student_dashboard.html')


@app.route('/student/view_books')
def student_view_books():
    """
    Displays ALL books (no Borrow action).
    """
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    stud = Student(session['student_id'], session['student_name'], "", "")
    books = stud.view_books()
    return render_template('books_list.html', books=books, user_type='student')


@app.route('/student/borrow_books')
def student_borrow_books():
    """
    Displays all books that might be available to borrow.
    Borrow requests are posted to /student/borrow
    """
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    stud = Student(session['student_id'], session['student_name'], "", "")
    all_books = stud.view_books()
    return render_template('borrow_book.html', books=all_books)


@app.route('/student/borrow', methods=['POST'])
def student_borrow():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    book_id = request.form.get('book_id', '').strip()
    stud = Student(session['student_id'], session['student_name'], "", "")
    status = stud.borrow_book(book_id)

    if status:
        _, today_date, book_obj = status
        flash(f"You have borrowed '{book_obj.book_name}' on {today_date}.", "success")
    else:
        flash("Book unavailable or invalid Book ID.", "error")

    return redirect(url_for('student_borrow_books'))


@app.route('/student/borrowed_books')
def student_borrowed_books():
    """
    Displays books the student currently has borrowed.
    Return requests are posted to /student/return
    """
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    db = Database()
    stud = Student(session['student_id'], session['student_name'], "", "")
    borrowed = db.get_all_borrowed_books(stud)
    return render_template('borrowed_books.html', borrowed_books=borrowed)


@app.route('/student/return', methods=['POST'])
def student_return():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    book_id = request.form.get('book_id', '').strip()
    stud = Student(session['student_id'], session['student_name'], "", "")
    status = stud.return_book(book_id)

    if status:
        trans_id, book_obj = status
        flash(f"You have returned '{book_obj.book_name}' successfully!", "success")
    else:
        flash("Return unsuccessful. Check Book ID or you haven't borrowed it.", "error")

    return redirect(url_for('student_borrowed_books'))


@app.route('/student/check_fines')
def student_check_fines():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    stud = Student(session['student_id'], session['student_name'], "", "")
    fine = stud.check_fines()  # includes manual + automatic
    return render_template('student_fines.html', fine_amount=fine)


@app.route('/student/deregister', methods=['POST'])
def student_deregister():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    stud = Student(session['student_id'], session['student_name'], "", "")
    success = stud.deregister()
    if success:
        flash("You have been deregistered successfully!", "success")
        session.clear()
        return redirect(url_for('home'))
    else:
        flash("Cannot deregister. Please ensure you have returned all books and have no fines!", "error")
        return redirect(url_for('student_dashboard'))


# ================================
#        LIBRARIAN ROUTES
# ================================

@app.route('/librarian/register', methods=['GET', 'POST'])
def librarian_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password1 = request.form.get('password1', '').strip()
        password2 = request.form.get('password2', '').strip()

        if not name or not password1 or not password2:
            flash("All fields are required!", "error")
            return redirect(url_for('librarian_register'))

        if password1 != password2:
            flash("Passwords do not match!", "error")
            return redirect(url_for('librarian_register'))

        db = Database()
        last_id = db.fetch_last_librarian_id()
        try:
            new_id_num = int(last_id[2:]) + 1
        except:
            new_id_num = 1
        new_id_str = f"lb{new_id_num:04d}"

        lib = Librarian(new_id_str, name, password1)
        db.save_librarian(lib)
        flash(f"Librarian registered successfully with ID {new_id_str}", "success")
        return redirect(url_for('librarian_login'))

    return render_template('librarian_register.html')


@app.route('/librarian/login', methods=['GET', 'POST'])
def librarian_login():
    if request.method == 'POST':
        lib_id = request.form.get('lib_id', '').strip()
        password = request.form.get('password', '').strip()

        if not lib_id or not password:
            flash("All fields are required!", "error")
            return redirect(url_for('librarian_login'))

        db = Database()
        lib_obj = db.lib_authenticate(lib_id, password)
        if lib_obj:
            session.permanent = True
            session['lib_id'] = lib_obj.librarian_id
            session['lib_name'] = lib_obj.librarian_name
            # Clear any student session
            session.pop('student_id', None)
            session.pop('student_name', None)

            flash("Librarian login successful!", "success")
            return redirect(url_for('librarian_dashboard'))
        else:
            flash("Authentication failed. Check ID/Password!", "error")
            return redirect(url_for('librarian_login'))

    return render_template('librarian_login.html')


@app.route('/librarian/dashboard')
def librarian_dashboard():
    if 'lib_id' not in session:
        return redirect(url_for('librarian_login'))
    return render_template('librarian_dashboard.html')


@app.route('/librarian/view_books')
def librarian_view_books():
    if 'lib_id' not in session:
        return redirect(url_for('librarian_login'))

    lib = Librarian(session['lib_id'], session['lib_name'], "")
    books = lib.view_books()
    return render_template('books_list.html', books=books, user_type='librarian')


@app.route('/librarian/add_book', methods=['POST'])
def librarian_add_book():
    if 'lib_id' not in session:
        return redirect(url_for('librarian_login'))

    book_name = request.form.get('book_name', '')
    book_author = request.form.get('book_author', '')
    book_publisher = request.form.get('book_publisher', '')
    book_publish_date = request.form.get('book_publish_date', '')
    book_copies = request.form.get('book_copies', '')

    lib = Librarian(session['lib_id'], session['lib_name'], "")
    book_obj = lib.add_books(book_name, book_author, book_publisher, book_publish_date, book_copies)
    flash(f"Book '{book_obj.book_name}' added with ID {book_obj.book_id}!", "success")
    return redirect(url_for('librarian_view_books'))


@app.route('/librarian/update_book', methods=['POST'])
def librarian_update_book():
    if 'lib_id' not in session:
        return redirect(url_for('librarian_login'))

    book_id = request.form.get('book_id', '')
    book_name = request.form.get('book_name', '')
    book_author = request.form.get('book_author', '')
    book_publisher = request.form.get('book_publisher', '')
    book_publish_date = request.form.get('book_publish_date', '')
    book_copies = request.form.get('book_copies', '')

    lib = Librarian(session['lib_id'], session['lib_name'], "")
    status, book_obj = lib.update_book(
        book_id, book_name, book_author, 
        book_publisher, book_publish_date, book_copies
    )

    if status:
        flash(f"Book '{book_id}' updated successfully!", "success")
    else:
        flash("Book update failed. Check Book ID!", "error")
    return redirect(url_for('librarian_view_books'))


@app.route('/librarian/remove_book', methods=['POST'])
def librarian_remove_book():
    if 'lib_id' not in session:
        return redirect(url_for('librarian_login'))

    book_id = request.form.get('book_id', '')
    lib = Librarian(session['lib_id'], session['lib_name'], "")
    result = lib.remove_book(book_id)

    if result:
        flash(f"Book '{result.book_name}' (ID: {result.book_id}) removed successfully!", "success")
    else:
        flash("Error removing book. Check Book ID!", "error")
    return redirect(url_for('librarian_view_books'))


# NEW: Librarian Transactions route
@app.route('/librarian/transactions')
def librarian_transactions():
    """
    Displays all borrow/return transactions from 'all_transactions.csv'.
    Also has a button or link to add a fine for a student.
    """
    if 'lib_id' not in session:
        return redirect(url_for('librarian_login'))

    db = Database()
    all_trans = db.get_all_transactions()
    return render_template('librarian_transactions.html', transactions=all_trans)

# NEW: Librarian Borrowed Books
@app.route('/librarian/borrowed_books')
def librarian_borrowed_books():
    """
    Shows all records from 'all_borrows.csv': (trans_id, stud_id, book_id, borrow_date)
    Also can add fine from here.
    """
    if 'lib_id' not in session:
        return redirect(url_for('librarian_login'))

    db = Database()
    borrowed_list = db.get_all_borrowed_records()  # We'll add a method
    return render_template('librarian_borrowed_books.html', borrowed_list=borrowed_list)


@app.route('/librarian/add_fine', methods=['GET', 'POST'])
def librarian_add_fine():
    if 'lib_id' not in session:
        return redirect(url_for('librarian_login'))

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        fine_amount_str = request.form.get('fine_amount', '0').strip()
        reason = request.form.get('reason', '').strip()
        redirect_page = request.form.get('redirect_page', 'librarian_transactions')

        if not student_id or not fine_amount_str:
            flash("Student ID and Fine Amount are required!", "error")
            return redirect(url_for('librarian_add_fine'))

        try:
            fine_amount = float(fine_amount_str)
        except:
            fine_amount = 0

        db = Database()
        db.add_manual_fine(student_id, fine_amount, reason)
        flash(f"Fine of Rs. {fine_amount} added to student {student_id}.", "success")
        return redirect(url_for(redirect_page))

    # If GET, possibly we have a student_id from query param
    student_id = request.args.get('student_id', '')
    page = request.args.get('page', 'librarian_transactions')  
    # page can be 'librarian_transactions' or 'librarian_borrowed_books'
    return render_template('librarian_add_fine.html', default_stud_id=student_id, redirect_page=page)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
