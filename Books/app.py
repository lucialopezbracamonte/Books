from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import requests
import calendar
from collections import Counter
import math

# Initialize Flask app
app = Flask(__name__)

# Configure the app for SQLAlchemy and set the secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"  # Database configuration
app.config["SECRET_KEY"] = "ENTER YOUR SECRET KEY"  # Secret key for secure sessions
db = SQLAlchemy(app)  # Initialize SQLAlchemy

# Google Books API base URL
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# User model for database (inherits UserMixin for Flask-Login integration)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    favorite_book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)
    favorite_book = db.relationship("Book", backref="favorited_by", uselist=False)
    books = db.relationship("UserBook", backref="user")

# Book model to store book details
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    author = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    user_books = db.relationship("UserBook", backref="book")

# UserBook model to track books associated with a user
class UserBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    date_read = db.Column(db.Date, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now)  # Automatically sets date added
    star_rating = db.Column(db.Integer, nullable=True)
    list_type = db.Column(db.String(50), nullable=False)  # E.g., "Read", "To Be Read"

# Post model for user reviews or posts about books
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.now)  # Automatically sets posting date
    star_rating = db.Column(db.Integer, nullable=True)
    date_read = db.Column(db.Date, nullable=True)
    user = db.relationship("User", backref="posts")
    book = db.relationship("Book", backref="posts")

# Default reading lists for users
default_lists = ['Currently Reading', 'To Be Read', 'Read']

# User loader function for Flask-Login
@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)

# Home route - displays books categorized by reading lists for logged-in users
@app.route("/")
def home():
    if current_user.is_authenticated:
        books_by_list = {}
        for list_name in default_lists:
            # Query books by list type for the current user
            books_in_list = (
                db.session.query(Book, UserBook)
                .join(UserBook, Book.id == UserBook.book_id)
                .filter(UserBook.user_id == current_user.id, UserBook.list_type == list_name)
                .all()
            )
            books_by_list[list_name] = books_in_list
        return render_template('home.html', books_by_list=books_by_list)
    return render_template("home.html")  # For non-authenticated users

# Search route to search books within the user's lists
@app.route("/search")
def search():
    query = request.args.get("query")  # Get search query
    if query:
        # Search books by title or author
        results = Book.query.join(UserBook).filter(
            UserBook.user_id == current_user.id,
            (Book.title.ilike(f"%{query}%")) | (Book.author.ilike(f"%{query}%"))
        ).all()
    else:
        results = []
    return render_template("search_results.html", results=results)

# External book search route using Google Books API
@app.route("/search_books", methods=["GET", "POST"])
def search_books():
    if request.method == "POST":
        query = request.form.get("query")
        if not query:
            return render_template("search_books.html", message="Please enter a search query.")
        
        # Fetch book data from Google Books API
        response = requests.get(GOOGLE_BOOKS_API_URL, params={"q": query})
        data = response.json()
        books = [
            {
                "title": item.get("volumeInfo", {}).get("title", "Unknown"),
                "author": ", ".join(item.get("volumeInfo", {}).get("authors", ["Unknown"])),
                "description": item.get("volumeInfo", {}).get("description", "No description available."),
                "thumbnail": item.get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail", ""),
                "id": item.get("id")
            }
            for item in data.get("items", [])
        ]
        return render_template("search_books.html", books=books)
    return render_template("search_books.html")

# Registration route for new users
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(username=request.form.get("username"), password=request.form.get("password"))
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)  # Log in the user after registration
            return redirect(url_for("home"))
        except:
            return "There was a problem adding that user"
    return render_template("sign_up.html")

# Login route for existing users
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if not user:
            return render_template("login.html", message="User not found.")
        if user.password == request.form.get("password"):  # Basic password check
            login_user(user)  # Log the user in
            return redirect(url_for("home"))
    return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    logout_user()  # Log out the current user
    return redirect(url_for("home"))

# Profile route for the current user
@app.route("/profile")
def profile():
    return render_template("profile.html", current_user=current_user)

# More comments for the remaining routes will continue with a similar structure.

@app.route("/other_profile/<int:user_id>")
def other_profile(user_id):
    # Fetch a user's profile using their ID, or return a 404 error if not found.
    user = User.query.get_or_404(user_id)
    # Render the other_profile.html template with the fetched user.
    return render_template("other_profile.html", user=user)

@app.route("/posts")
def posts():
    # Query all posts, ordered by the most recent date_read.
    all_posts = Post.query.order_by(Post.date_read.desc()).all()
    # Render the posts.html template with the fetched posts.
    return render_template("posts.html", posts=all_posts)

@app.route("/edit_favorite/<int:book_id>", methods=["POST"])
def set_favorite(book_id):
    # Check the submitted form action: "set" or "edit".
    if request.form["submit"] == "set":
        # Fetch the book using its ID. If found, set it as the user's favorite.
        book = Book.query.get(book_id)
        if book:
            current_user.favorite_book = book
            db.session.commit()
            # Redirect to the user's profile after updating.
            return redirect(url_for("profile"))
    elif request.form["submit"] == "edit":
        # Clear the user's favorite book.
        current_user.favorite_book = None
        db.session.commit()
        return redirect(url_for("profile"))

@app.route("/add_book", methods=["POST"])
def add_book():
    # Retrieve book details from the submitted form.
    title = request.form.get("title")
    author = request.form.get("author")
    description = request.form.get("description")
    thumbnail = request.form.get("thumbnail")
    list_type = request.form.get("list_type")
    date_read = request.form.get("date_read")
    star_rating = request.form.get("star_rating")
    
    # Check if the book already exists in the database.
    book = Book.query.filter_by(title=title, author=author, description=description, thumbnail_url=thumbnail).first()
        
    if not book:
        # If the book does not exist, create and save a new book entry.
        book = Book(title=title, author=author, description=description, thumbnail_url=thumbnail)
        db.session.add(book)
        db.session.commit()
        
    # Create a UserBook association for the current user and the book.
    user_book = UserBook(user_id=current_user.id, book_id=book.id, list_type=list_type)
    if user_book.list_type == "Read":
        # Set additional details if the book is marked as "Read".
        date_read = datetime.strptime(date_read, "%Y-%m-%d").date()
        user_book.date_read = date_read
        user_book.star_rating = star_rating

        # Create a new post for the book if it is read.
        post = Post(user_id=current_user.id, book_id=book.id, star_rating=star_rating, date_read=date_read)
        db.session.add(post)

    db.session.add(user_book)
    db.session.commit()

    # Redirect to the homepage after adding the book.
    return redirect(url_for("home"))

@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book_detail(book_id):
    # Fetch the book by its ID or return a 404 error if not found.
    book = Book.query.get_or_404(book_id)
    # Fetch the UserBook association for the current user and the book.
    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()

    if request.method == "POST":
        # Handle form submission to update the book's list type and details.
        new_list = request.form.get("list_type")
        if new_list:
            user_book.list_type = new_list

            if new_list == "Read":
                # Update date_read and star_rating if the book is marked as "Read".
                new_date_read = request.form.get("date_read")
                new_star_rating = request.form.get("star_rating")
                if new_date_read:
                    new_date_read = datetime.strptime(new_date_read, "%Y-%m-%d").date()
                    user_book.date_read = new_date_read
                if new_star_rating:
                    user_book.star_rating = new_star_rating
                # Create a new post entry.
                post = Post(user_id=current_user.id, book_id=book.id, star_rating=new_star_rating, date_read=new_date_read)
                db.session.add(post)

        db.session.commit()
        # Redirect to the homepage after updating the book details.
        return redirect(url_for("home"))

    # Render the book_detail.html template with the book and user_book data.
    return render_template("book_detail.html", book=book, user_book=user_book)

@app.route("/reading_wrapped")
def reading_wrapped():
    # Fetch all books marked as "Read" by the current user.
    read_books = UserBook.query.filter_by(user_id=current_user.id, list_type='Read').all()

    # Calculate statistics: total books, average rating, most-read author.
    total_books = len(read_books)
    total_ratings = sum([book.star_rating for book in read_books if book.star_rating])
    average_rating = total_ratings / total_books if total_books else 0
    average_rating = math.floor(average_rating * 100) / 100

    author_count = {}
    for book in read_books:
        # Count the frequency of each author in the read books.
        author_count[book.book.author] = author_count.get(book.book.author, 0) + 1
    
    # Determine the most-read author.
    most_read_author = max(author_count, key=author_count.get, default="N/A")

    # Count books read in each month.
    month_count = Counter()
    for book in read_books:
        if book.date_read:
            month = book.date_read.strftime("%B")
            month_count[month] += 1

    # Determine the most-read month.
    most_read_month = month_count.most_common(1)[0][0] if month_count else "N/A"

    # Prepare data for a chart showing monthly reading trends.
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    monthly_read_count = [month_count.get(month, 0) for month in months]

    # Render the reading_wrapped.html template with the calculated data.
    return render_template("reading_wrapped.html", 
                           total_books=total_books,
                           average_rating=average_rating, 
                           most_read_author=most_read_author,
                           most_read_month=most_read_month,
                           monthly_read_count=monthly_read_count)

@app.route("/calendar", methods=["GET", "POST"])
def calendar_view():
    # Get the current date or use the year/month from the request arguments.
    today = date.today()
    year = int(request.args.get("year", today.year))  
    month = int(request.args.get("month", today.month))  

    # Generate calendar days for the specified month and year.
    cal = calendar.Calendar()
    month_days = cal.itermonthdays2(year, month)

    # Fetch all "Read" books for the current user.
    user_books = (
        db.session.query(UserBook, Book)
        .join(Book, UserBook.book_id == Book.id)
        .filter(UserBook.user_id == current_user.id, UserBook.list_type == "Read")
        .all()
    )

    # Create a mapping of read dates to book thumbnail URLs.
    books_by_date = {
        user_book.date_read.day: book.thumbnail_url
        for user_book, book in user_books
        if user_book.date_read and user_book.date_read.year == year and user_book.date_read.month == month
    }

    # Render the calendar.html template with the calendar and book data.
    return render_template(
        "calendar.html",
        year=year,
        month=month,
        month_days=list(month_days),
        books_by_date=books_by_date,
    )

if __name__ == "__main__":
    # Run the app in debug mode for easier troubleshooting.
    app.run(debug=True)
