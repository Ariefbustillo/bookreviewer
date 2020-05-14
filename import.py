import csv
import os
from mod import *
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQLAlchemy()


engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(engine)
session = Session()

def main():
    csvfile = open("books.csv")
    reader = csv.reader(csvfile)
    for row in reader:
        book = Books(isbn=row[0], title=row[1], author=row[2], pub_year=row[3])
        session.add(book)
    session.commit()
    csvfile.close()
    return


if __name__ == "__main__":
    with app.app_context():
        main()