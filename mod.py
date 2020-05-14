from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()
Base = declarative_base()


class Books(Base):
    __tablename__ = 'books'
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    pub_year = db.Column(db.Integer, nullable=False)
    gr_rating = db.Column(db.Float, nullable=True)
    gr_num_of_ratings = db.Column(db.Integer, nullable=True)


class Reviews(Base):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, db.ForeignKey("books.isbn"), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.String, nullable=False)


class Users(Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
