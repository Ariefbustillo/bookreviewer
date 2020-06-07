import os
import requests
from flask import Flask
from mod import db


app = Flask(__name__)
import routes


# Check for environment variables
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("GOODREAD_KEY"):
    raise RuntimeError("GOODREAD_KEY is not set")
if not os.getenv("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY is not set")

# get environment variables
goodread_key = os.getenv("GOODREAD_KEY")
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
