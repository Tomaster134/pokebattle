from flask import request, render_template, redirect, url_for, flash, session
from . import main
from .forms import PokeLookUp
from flask_login import login_required, current_user
import requests
from random import randint
from app.models import Pokemon, db

@main.route('/')
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
            'ability': data['abilities'][0]['ability']['name'].replace('-', ' ').title(),
            'sprite_url': data['sprites']['other']['official-artwork']['front_default'],
            'id_num': data['id'],
            'battle_url': data['sprites']['front_shiny']
        }
        for key, value in pokedict.items():
            if value == None: pokedict[key] = 0
        return pokedict
    elif response.status_code == 404: return '404 error code. Pokémon name or ID either doesn\'t exist or was mispelled. Please try again.'
    else: return f'{response.status_code} error code.'

@main.route('/pokedex', methods=['GET','POST'])
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


@main.route('/squad')
@login_required
def squad():
    squad = current_user.caught.all()
    return render_template('squad.html', squad=squad)

@main.route('/catch/<id_num>')
@login_required
def catch(id_num):
    if len(current_user.caught.all()) >= 6:
        flash('Too many Pokémon >:( You can only hold 6!', 'warning')
        return redirect(url_for('main.pokedex'))
    else:
        if Pokemon.query.get(id_num):
            pokemon = Pokemon.query.get(id_num)
            if pokemon in current_user.caught:
                flash(f'You\'ve already caught a {pokemon.name}! Don\'t be greedy now, go catch something else.', 'warning')
                return redirect(url_for('main.pokedex'))
            else:
                current_user.caught.append(pokemon)
                db.session.commit()
                flash('Pokémon successfully added to squad!', 'success')
                return redirect(url_for('main.pokedex'))
        else:
            temp = pokegrabber(id_num)
            new_pokemon = Pokemon(id_num=temp['id_num'], name=temp['name'], base_hp=temp['base_hp'], base_atk=temp['base_atk'], base_def=temp['base_def'], base_s_atk=temp['base_s_atk'], base_s_def=temp['base_s_def'], base_spd=temp['base_spd'], base_exp=temp['base_exp'], sprite_url=temp['sprite_url'], ability=temp['ability'], battle_url=temp['battle_url'])
            new_pokemon.save()
            pokemon = Pokemon.query.get(id_num)
            current_user.caught.append(pokemon)
            db.session.commit()
            flash('Pokémon successfully added to squad!', 'success')
            return redirect(url_for('main.pokedex'))
        
@main.route('/release/<id_num>')
@login_required
def release(id_num):
    pokemon = Pokemon.query.get(id_num)
    current_user.caught.remove(pokemon)
    db.session.commit()
    flash(f'{pokemon.name} has been released into the wild. On the one hand, good thing you\'re no longer forcing it into ritual combat. On the other hand, sure hope it knows how to feed itself after a life of captvity. Sheesh.', 'info')
    return redirect(url_for('main.squad'))