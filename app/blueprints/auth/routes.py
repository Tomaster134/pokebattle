from flask import request, render_template, redirect, url_for, flash
from . import auth
from .forms import LoginForm, SignUpForm
from flask_login import login_user, logout_user, login_required
from app.models import User
from werkzeug.security import check_password_hash
from sqlalchemy import exc


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit:
        username = form.username.data
        password = form.password.data

        queried_user = User.query.filter(User.username == username).first()
        if queried_user and check_password_hash(queried_user.password, password):
            flash(f'Login successful! Welcome back {queried_user.username}', 'info')
            login_user(queried_user)
            return redirect(url_for('main.index'))
        else:
            flash('Username or password incorrect :(', 'warning')
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)
    
@auth.route('/signup', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.login'))
        except exc.IntegrityError:
            flash(f'Username or email already taken.', 'warning')
            return render_template('signup.html', form=form)
    else:
        return render_template('signup.html', form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))