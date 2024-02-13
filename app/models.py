from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def save(self):
        db.session.add(self)
        db.session.commit()

class Pokemon(db.Model):
    id_num = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    base_hp = db.Column(db.Integer, nullable=False)
    base_atk = db.Column(db.Integer, nullable=False)
    base_def = db.Column(db.Integer, nullable=False)
    base_s_atk = db.Column(db.Integer, nullable=False)
    base_s_def = db.Column(db.Integer, nullable=False)
    base_spd = db.Column(db.Integer, nullable=False)
    base_exp = db.Column(db.Integer, nullable=False)
    sprite_url = db.Column(db.String, nullable=False)

    def __init__(self, id_num, name, base_hp, base_atk, base_def, base_s_atk, base_s_def, base_spd, base_exp, sprite_url):
        self.id_num = id_num
        self.name = name
        self.base_hp = base_hp
        self.base_atk = base_atk
        self.base_def = base_def
        self.base_s_atk = base_s_atk
        self.base_s_def = base_s_def
        self.base_spd = base_spd
        self.base_exp = base_exp
        self.sprite_url = sprite_url

    def save(self):
        db.session.add(self)
        db.session.commit()