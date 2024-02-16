from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

pokemon_user = db.Table(
    'pokemon_user',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('pokemon_id_num', db.Integer, db.ForeignKey('pokemon.id_num'))
)

class BattleRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aggressor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    defender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    victor_id = db.Column(db.Integer)

    def __init__(self, aggressor_id, defender_id, victor_id):
        self.aggressor_id = aggressor_id
        self.defender_id = defender_id
        self.victor_id = victor_id
    
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
    ability = db.Column(db.String, nullable=False)
    battle_url = db.Column(db.String, nullable=False)

    def __init__(self, id_num, name, base_hp, base_atk, base_def, base_s_atk, base_s_def, base_spd, base_exp, sprite_url, ability, battle_url):
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
        self.ability = ability
        self.battle_url = battle_url

    def save(self):
        db.session.add(self)
        db.session.commit()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True)
    prof_img = db.Column(db.String)
    caught = db.relationship('Pokemon',
                             secondary = pokemon_user,
                             backref = 'caught_by',
                             lazy = 'dynamic'
                             )

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def save(self):
        db.session.add(self)
        db.session.commit()