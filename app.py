import os
from mod import db, Base, Reviews, Users, Books

from flask import Flask, session, render_template, request,redirect, url_for
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
@app.route("/")
def index():
    if session['logged_in'] is False:
        print("Not there")
        session['user_id'] = None
        return render_template("login.html")
    print(session['user_id'])
    return render_template("index.html")

@app.route("/logout")
def logout():
    session['user_id'] = None
    session['logged_in'] = False
    return render_template("login.html")

@app.route("/to_create_account")
def to_create_account():
    return render_template("create_account.html")

@app.route("/login", methods=["post"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    users = db.query(Users).all()
    for user in users:
        print(user.password)
        print(password)
        print(user.username)
        print(username)
        print(user.id)
        if user.username == username:
            if password == user.password:
                session['user_id'] = user.id
                session['logged_in'] = True
                print(user.id)
                return render_template("index.html")
    return ("Nope")

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


@app.route("/search", methods=["post"])
def search():
    q = request.form.get("q")
    print(q)
    results = db.query(Books).filter(or_(Books.title.like(f"%{q}%"),Books.author.like(f"%{q}%"), Books.isbn == q)).all()
    # print(results)
    if len(results) >= 1:
        return render_template("results.html", results=results)
    else:
        return "No results found."


@app.route("/books/<ibsn>", methods=["get", "post"])
def books(ibsn):
    # ibsn = request.args.get("ibsn")
    book_info = db.query(Books).filter(Books.isbn == ibsn).one()
    reviews = db.query(Reviews, Users).filter(and_(Reviews.isbn == ibsn, Reviews.user_id == Users.id)).all()

    return render_template("book_info.html", book_info=book_info, reviews=reviews)

@app.route("/review", methods=["post"])
def review():
    content = request.form.get("content")
    ibsn = request.form.get("ibsn")
    rating = request.form.get("rating")
    last_review = db.query(Reviews).order_by(Reviews.id.desc()).first()
    #Checks if user has review already

    if len(db.query(Reviews).filter(and_(Reviews.user_id == session['user_id'], Reviews.isbn == ibsn)).all()) > 0:
        print(db.query(Reviews).filter(and_(Reviews.user_id == session['user_id'], Reviews.isbn == ibsn)).all())
        return "You may not submit two reviews for the same book"

    #Checks if this is the first review in system, autoincrements review id
    if last_review is None:
        review = Reviews(id = 1, isbn=ibsn,review=content, rating=rating, user_id=session['user_id'])
    else:
        review = Reviews(id=last_review.id + 1, isbn=ibsn, review=content, rating=rating, user_id=session['user_id'])
    #add review to database   
    db.add(review)
    db.commit()
    return redirect(url_for('books', ibsn=ibsn))
