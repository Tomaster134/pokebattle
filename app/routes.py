from flask import request, render_template
from app import app
from .forms import PokeLookUp


@app.route('/')
def index():
    return render_template('index.html')

def pokegrabber(pokemon=''):
    import requests
    if pokemon == 'random' or pokemon == '':
        from random import randint
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
        