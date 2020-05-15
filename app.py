import os
import requests
from mod import db, Base, Reviews, Users, Books

from flask import Flask, session, render_template, request,redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
goodread_key = "ShHaN0gMAt2QQUQJsLzTRA"

# Check for environment variablec
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app.secret_key = '7djf6s9dj03'

# Create Tables
# Base.metadata.create_all(engine)


#Home page, to login if not logged in
@app.route("/")
def index():  
    if session['logged_in'] is False:
        session['user_id'] = None
        return render_template("login.html")
    return render_template("index.html")

#Logs out
@app.route("/logout")
def logout():
    session['user_id'] = None
    session['logged_in'] = False
    return render_template("login.html")

#Links to account creation
@app.route("/to_create_account")
def to_create_account():
    return render_template("create_account.html")

#Login, set session values
@app.route("/login", methods=["post"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    users = db.query(Users).all()
    for user in users:
        if user.username == username:
            if password == user.password:
                session['user_id'] = user.id
                session['logged_in'] = True
                print(user.id)
                return render_template("index.html")
    return("Username and Password Do Not Match")

#Create account
@app.route("/create_account",methods=['post'])
def create_account():
    username = request.form.get("username")
    password = request.form.get("password")
    last_user = db.query(Users).order_by(Users.id.desc()).first()
    user_id = last_user.id + 1
    user = Users(id =user_id, username = username, password = password)
    db.add(user)
    db.commit()
    return render_template("login.html")

#Search page
@app.route("/search", methods=["post"])
def search():
    #get search results
    q = request.form.get("q")
    results = db.query(Books).filter(or_(Books.title.like(f"%{q}%"),Books.author.like(f"%{q}%"), Books.isbn == q)).all()

    # print(results)
    if len(results) >= 1:
        return render_template("results.html", results=results)
    else:
        return "No results found."


#Show book info page
@app.route("/books/<isbn>", methods=["get", "post"])
def books(isbn):
    #get book info from database
    book_info = db.query(Books).filter(Books.isbn == isbn).one()

    #get Goodreads book info
    goodreads_info = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ShHaN0gMAt2QQUQJsLzTRA", "isbns": f"{isbn}"}).json()
    avg_rating = (goodreads_info.get('books')[0].get('average_rating'))
    ratings_count = (goodreads_info.get('books')[0].get('ratings_count'))

    #get reviews from database
    reviews = db.query(Reviews, Users).filter(and_(Reviews.isbn == isbn, Reviews.user_id == Users.id)).all()

    return render_template("book_info.html", book_info=book_info, reviews=reviews, avg_rating=avg_rating, ratings_count=ratings_count)


#Adds review to databse
@app.route("/review", methods=["post"])
def review():
    content = request.form.get("content")
    isbn = request.form.get("isbn")
    rating = request.form.get("rating")
    last_review = db.query(Reviews).order_by(Reviews.id.desc()).first()

    #Checks if user has review already
    if len(db.query(Reviews).filter(and_(Reviews.user_id == session['user_id'], Reviews.isbn == isbn)).all()) > 0:
        print(db.query(Reviews).filter(and_(Reviews.user_id == session['user_id'], Reviews.isbn == isbn)).all())
        return "You may not submit two reviews for the same book"

    #Checks if this is the first review in system, autoincrements review id
    if last_review is None:
        review = Reviews(id = 1, isbn=isbn,review=content, rating=rating, user_id=session['user_id'])
    else:
        review = Reviews(id=last_review.id + 1, isbn=isbn, review=content, rating=rating, user_id=session['user_id'])

    #Add review to database   
    db.add(review)
    db.commit()
    return redirect(url_for('books', isbn=isbn))

@app.route("/api/<isbn>",methods=['get'])
def api(isbn):
    #Get book and review information
    book_info = db.query(Books).filter(Books.isbn==isbn).one()
    last_review = db.query(Reviews).filter(Reviews.isbn == isbn).order_by(Reviews.id.desc()).first()
    reviews_info = db.query(Reviews).filter(Reviews.isbn == isbn).all()

    #if no reviews have been made
    if len(reviews_info) < 1:
        review_count="No Reviews"
        average_score="N/A"
        return jsonify(title=book_info.title, author=book_info.author, year=book_info.pub_year, isbn=book_info.isbn, review_count=review_count, average_score=average_score)

    #Use id of last review to count reviews
    review_count = last_review.id

    #Find average book rating
    average_score = 0
    for review_info in reviews_info:
        average_score += review_info.rating
    average_score /= review_count

    #Return JSON
    return jsonify(title=book_info.title, author=book_info.author, year=book_info.pub_year, isbn=book_info.isbn, review_count=review_count, average_score=average_score)


