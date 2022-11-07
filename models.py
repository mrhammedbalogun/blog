from email.policy import default
from enum import unique
from blog import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime
import re
from time import time

def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__= 'user'
    id = db.Column(db.Integer(), primary_key=True)
    fname = db.Column(db.String(length=30), nullable=False)
    lname = db.Column(db.String(length=30), nullable=False)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    post = db.relationship('Post', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Post(db.Model):
    __tablename__= 'post'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length=140), nullable=False)
    slug = db.Column(db.String(length=140), nullable=False, unique=True)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now())
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
        
        else:
            self.slug = str(int(time()))
    
    def __repr__(self) -> str:
        return f'<Post id: {self.id}, title: {self.title}>'
    