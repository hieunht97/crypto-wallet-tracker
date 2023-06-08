from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    wallets = db.relationship("Metamask")


class Metamask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100))
    network = db.Column(db.String(150))
    balance = db.Column(db.Numeric(precision=8, scale=4))
    token = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
