from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid
import os
db = SQLAlchemy()

class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    balance = db.Column(db.Integer, nullable=False)

class Ad(db.Model):
    __tablename__ = 'ads'
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    speed = db.Column(db.Integer)
    responses = db.relationship('Response', backref='ad', lazy=True)

    def get_images(self):
        image_folder = os.path.join('static/images', self.id)
        if os.path.exists(image_folder):
            images = [f"images/{self.id}/{f}" for f in os.listdir(image_folder)]
            return sorted(images)
        return []

class Response(db.Model):
    __tablename__ = 'responses'

    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.String(36), db.ForeignKey('ads.id'), nullable=False)  # Изменено на String
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Material(db.Model):
    __tablename__ = 'materials'
    name = db.Column(db.String(36), primary_key=True)
    density = db.Column(db.Integer, nullable=False)

class ShipMaterial(db.Model):
    __tablename__ = 'ship_materials'
    ad_id = db.Column(db.String(36), db.ForeignKey('ads.id'), primary_key=True)
    material_id = db.Column(db.String(36), db.ForeignKey('materials.name'), primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    ad = db.relationship('Ad', backref=db.backref('materials', lazy=True))
    material = db.relationship('Material', backref=db.backref('ads', lazy=True))