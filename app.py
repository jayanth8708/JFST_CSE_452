from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE CONNECTION
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="library_db"
)

cursor = db.cursor(dictionary=True, buffered=True)


# ---------------- ADMIN LOGIN ---------------- #

@app.route('/')
def home():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def admin_login():

    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "admin":
        session['admin'] = True
        return redirect("/dashboard")
    else:
        return render_template("login.html", error="Invalid Admin Login")


# ---------------- ADMIN DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():

    if 'admin' not in session:
        return redirect('/')

    cursor.execute("SELECT COUNT(*) AS total FROM books")
    total_books = cursor.fetchone()['total']

    cursor.execute("SELECT SUM(quantity) AS available FROM books")
    available_books = cursor.fetchone()['available']

    cursor.execute("SELECT COUNT(*) AS issued FROM issued_books")
    issued_books = cursor.fetchone()['issued']

    cursor.execute("SELECT COUNT(*) AS reservations FROM reservations")
    reservations = cursor.fetchone()['reservations']

    return render_template(
        "dashboard.html",
        total_books=total_books,
        available_books=available_books,
        issued_books=issued_books,
        reservations=reservations
    )


# ---------------- USER AUTH ---------------- #

@app.route('/user_login')
def user_login():
    return render_template("user_login.html")


@app.route('/user_register')
def user_register():
    return render_template("user_register.html")


@app.route('/register_user', methods=['POST'])
def register_user():

    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    confirm = request.form['confirm']

    if password != confirm:
        return render_template("user_register.html", error="Passwords do not match")

    cursor.execute(
        "INSERT INTO users(email, phone, password) VALUES(%s,%s,%s)",
        (email, phone, password)
    )
    db.commit()

    return redirect('/user_login')


@app.route('/login_user', methods=['POST'])
def login_user():   # ✅ FIXED NAME

    email = request.form['email']
    password = request.form['password']

    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, password)
    )

    user = cursor.fetchone()

    if user:
        session['user'] = True
        session['user_email'] = email   # ✅ ADD THIS LINE
        return redirect('/user_dashboard')
    else:
        return render_template("user_login.html", error="Invalid User Login")


# ---------------- USER DASHBOARD ---------------- #

@app.route('/user_dashboard')
def user_dashboard():
    if 'user' not in session:
        return redirect('/user_login')

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    return render_template("user_dashboard.html", books=books)


# ---------------- ADD BOOK ---------------- #

@app.route('/add_book')
def add_book():
    return render_template("add_book.html")


@app.route('/save_book', methods=['POST'])
def save_book():

    title = request.form['title']
    author = request.form['author']
    category = request.form['category']
    quantity = request.form['quantity']
    barcode = request.form['barcode']

    cursor.execute("""
        INSERT INTO books(title, author, category, quantity, barcode)
        VALUES(%s,%s,%s,%s,%s)
    """, (title, author, category, quantity, barcode))

    db.commit()

    return redirect("/dashboard")


# ---------------- SCAN BOOK ---------------- #

@app.route('/scan_book')
def scan_book():
    return render_template("scan_book.html")


@app.route('/scan_book', methods=['POST'])
def scan_book_result():

    barcode = request.form['barcode']

    cursor.execute("SELECT * FROM books WHERE barcode=%s", (barcode,))
    book = cursor.fetchone()

    if book:
        return render_template("book_result.html", book=book)
    else:
        return "Book Not Found"


# ---------------- VIEW BOOKS ---------------- #

@app.route('/view_books')
def view_books():
    if 'user' not in session:
        return redirect('/user_login')

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    return render_template("view_books.html", books=books)


# ================= ADD FROM HERE ================= #

# ---------------- USER VIEW BOOKS ---------------- #

@app.route('/view_books_user')
def view_books_user():

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    return render_template("view_books_user.html", books=books)


# ---------------- RESERVE BOOK PAGE ---------------- #

@app.route('/reserve_books')
def reserve_books():
    if 'user' not in session:
        return redirect('/user_login')

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    return render_template("reserve_books.html", books=books)


# ---------------- RESERVE ACTION ---------------- #

@app.route('/reserve/<int:book_id>', methods=['POST'])
def reserve(book_id):

    # 🔐 Check login
    if 'user' not in session:
        return redirect('/user_login')

    username = session.get('user_email')

    # 📚 Get full book details
    cursor.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
    book = cursor.fetchone()

    # ❌ If book not found
    if not book:
        return "Book not found"

    # ❌ If no stock
    if book['quantity'] <= 0:
        return "Book Not Available"

    # 🔄 Reduce quantity
    cursor.execute(
        "UPDATE books SET quantity = quantity - 1 WHERE book_id=%s",
        (book_id,)
    )

    # 💾 Save reservation
    cursor.execute(
        "INSERT INTO reservations (book_id, username, book_name, status) VALUES (%s, %s, %s, %s)",
        (book_id, username, book['title'], 'Reserved')
    )

    db.commit()

    return redirect('/reserve_books')

# ================= END HERE ================= #

# ---------------- ADMIN RESERVATIONS ---------------- #

@app.route('/admin_reservations')
def admin_reservations():

    if 'admin' not in session:
        return redirect('/')

    cursor.execute("SELECT * FROM reservations")
    data = cursor.fetchall()

    return render_template("admin_reservations.html", reservations=data)

# ---------------- update RESERVATIONS ---------------- #
@app.route('/update_reservation/<int:res_id>', methods=['POST'])
def update_reservation(res_id):

    if 'admin' not in session:
        return redirect('/')

    action = request.form.get('action')

    # get reservation details
    cursor.execute("SELECT * FROM reservations WHERE id=%s", (res_id,))
    reservation = cursor.fetchone()

    if not reservation:
        return "Reservation not found"

    if action == 'approve':
        status = 'Approved'

    else:
        status = 'Rejected'

        # 🔥 IMPORTANT: restore quantity
        cursor.execute(
            "UPDATE books SET quantity = quantity + 1 WHERE book_id=%s",
            (reservation['book_id'],)
        )

    # update status
    cursor.execute(
        "UPDATE reservations SET status=%s WHERE id=%s",
        (status, res_id)
    )

    db.commit()

    return redirect('/admin_reservations')

# ---------------- ISSUE BOOK ---------------- #

@app.route('/issue_book', methods=['GET','POST'])
def issue_book():

    if request.method == 'POST':

        student = request.form['student']
        barcode = request.form['barcode']

        cursor.execute("SELECT quantity FROM books WHERE barcode=%s", (barcode,))
        book = cursor.fetchone()

        if book and book['quantity'] > 0:

            cursor.execute(
                "UPDATE books SET quantity = quantity - 1 WHERE barcode=%s",
                (barcode,)
            )

            cursor.execute(
                "INSERT INTO issued_books(student_name, barcode, issue_date) VALUES(%s,%s,CURDATE())",
                (student, barcode)
            )

            db.commit()

            return "Book Issued Successfully"

        else:
            return "Book Not Available"

    return render_template("issue_book.html")


# ---------------- RETURN BOOK ---------------- #

@app.route('/return_book', methods=['GET','POST'])
def return_book():

    if request.method == 'POST':

        student = request.form['student']
        barcode = request.form['barcode']

        cursor.execute(
            "SELECT * FROM issued_books WHERE student_name=%s AND barcode=%s",
            (student, barcode)
        )

        issued = cursor.fetchone()

        if not issued:
            return render_template("return_book.html", message="Book not issued")

        cursor.execute(
            "UPDATE books SET quantity = quantity + 1 WHERE barcode=%s",
            (barcode,)
        )

        cursor.execute(
            "DELETE FROM issued_books WHERE student_name=%s AND barcode=%s LIMIT 1",
            (student, barcode)
        )

        db.commit()

        return render_template("return_book.html", message="Book Returned Successfully")

    return render_template("return_book.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RUN APP ---------------- #

if __name__ == '__main__':
    app.run(debug=True)
