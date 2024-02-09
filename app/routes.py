from flask import request, render_template, redirect, url_for, flash
from app import app
from .forms import PokeLookUp, LoginForm, SignUpForm
from flask_login import login_user, logout_user, login_required, current_user
import requests
from random import randint
from app.models import User
from werkzeug.security import check_password_hash
from sqlalchemy import exc

@app.route('/')
def index():
    return render_template('index.html')

def pokegrabber(pokemon=''):
    if pokemon == 'random' or pokemon == '':
        pokemon = randint(1,1025)
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon}'
    response = requests.get(url)
    if response.ok:
        data = response.json()
        pokedict = {
            'name': data['forms'][0]['name'].replace('-', ' ').title(),
            'base_hp': data['stats'][0]['base_stat'],
            'base_atk': data['stats'][1]['base_stat'],
            'base_def': data['stats'][2]['base_stat'],
            'base_s_atk': data['stats'][3]['base_stat'],
            'base_s_def': data['stats'][4]['base_stat'],
            'base_spd': data['stats'][5]['base_stat'],
            'base_exp': data['base_experience'],
            'ability1': data['abilities'][0]['ability']['name'].replace('-', ' ').title(),
            'sprite_url': data['sprites']['other']['official-artwork']['front_default'],
            'id_num': pokemon
        }
        return pokedict
    elif response.status_code == 404: return '404 error code. Pokemon name or ID either doesn\'t exist or was mispelled. Please try again.'
    else: return f'{response.status_code} error code.'

@app.route('/pokedex', methods=['GET','POST'])
def pokedex():
    form = PokeLookUp()
    if request.method == 'POST' and form.validate_on_submit:
        lookup = form.pokemon.data
        if 'error code' in pokegrabber(lookup):
            error = pokegrabber(lookup)
            return render_template('error.html', error=error)
        else:
            pokemon = pokegrabber(lookup)
            return render_template('pokedex.html', pokemon=pokemon, form=form)
    else:
        return render_template('pokedex.html', form=form)
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit:
        username = form.username.data
        password = form.password.data

        queried_user = User.query.filter(User.username == username).first()
        if queried_user and check_password_hash(queried_user.password, password):
            flash(f'Login successful! Welcome back {queried_user.username}', 'info')
            login_user(queried_user)
            return redirect(url_for('index'))
        else:
            flash('Username or password incorrect :(', 'warning')
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST' and form.validate_on_submit:
        username = form.username.data
        email = form.email.data
        password = form.password.data
        try:
            new_user = User(username, email, password)
            new_user.save()
            flash(f'Sign up successful! Welcome to PokéBattle {username}! Please log in with your new account.', 'success')
            return redirect(url_for('login'))
        except exc.IntegrityError:
            flash(f'Username or email already taken.', 'warning')
            return render_template('signup.html', form=form)
    else:
        return render_template('signup.html', form=form)

@app.route('/account')
def account():
    if current_user.is_anonymous: return redirect(url_for('login'))
    else: return render_template('account.html')
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))