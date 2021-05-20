from sqlalchemy.orm import backref
from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 사용자의 추가 정보 컬럼 만들기
    about_me = db.Column(db.String(140))
    # 마지막으로 사이트에 access한 시간 추적 컬럼 만들기
    datetime_kor = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    last_seen = db.Column(db.DateTime, default=datetime_kor)
    # 클래스의 객체를 print하는 방법
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    datetime_kor = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    timestamp = db.Column(db.DateTime, index=True, default=datetime_kor)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 클래스의 객체를 print하는 방법
    def __repr__(self):
        return '<Post {}>'.format(self.body)

