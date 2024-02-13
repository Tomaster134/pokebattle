from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class PokeLookUp(FlaskForm):
    pokemon = StringField('Pokemon: ')
    lookup_btn = SubmitField('Lookup!')