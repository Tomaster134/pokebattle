from flask import request, render_template, redirect, url_for, flash, session
from . import main
from .forms import PokeLookUp
from flask_login import login_required, current_user
import requests
from random import randint
from app.models import User, Pokemon, db, BattleRecord

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

@main.route('/battle')
@login_required
def battle():
    opponents = User.query.filter(User.id != current_user.id).all()
    op_info = []
    class OpInfo:
        def __init__(self, opponent, rec):
            self.trainer = opponent
            self.rec = rec
    for opponent in opponents:
        record = str(len(db.session.query(BattleRecord).filter(opponent.id == BattleRecord.defender_id).filter(current_user.id == BattleRecord.aggressor_id).all()) + len(db.session.query(BattleRecord).filter(opponent.id == BattleRecord.aggressor_id).filter(current_user.id == BattleRecord.defender_id).all()))
        trainer = OpInfo(opponent, record)
        op_info.append(trainer)
    return render_template('battle.html', op_info=op_info)

@main.route('/battle_preview/<opp_id>')
@login_required
def battle_preview(opp_id):
    opponent = User.query.get(opp_id)
    opp_squad = opponent.caught.all()
    return render_template('battle_preview.html', opp_squad=opp_squad, opponent=opponent)

def battle(your_squad, opp_squad, opponent):
    from random import randint
    from math import floor
    class Output:
        def __init__(self, victor, log):
            self.victor = victor
            self.log = log
    your_counter = 0
    their_counter = 0
    your_new = True
    their_new = True
    turn = True
    battle_log = []
    while your_counter < len(your_squad) and their_counter < len(opp_squad):
        your_poke = your_squad[your_counter]
        their_poke = opp_squad[their_counter]
        if your_new == True:
            your_hp = your_poke.base_hp
            your_new = False
            battle_log.append(f'{current_user.username} sends out {your_poke.name}!')
        if their_new == True:
            their_hp = their_poke.base_hp
            their_new = False
            battle_log.append(f'{opponent.username} sends out {their_poke.name}!')
        if your_poke.base_spd > their_poke.base_spd: turn = True
        else: turn = False
        while your_hp > 0 and their_hp > 0:
            if turn == True:
                your_attack = floor(((your_poke.base_atk + (your_poke.base_s_atk * .2)) + randint(-floor(((your_poke.base_atk + (your_poke.base_s_atk * .2)) * .1)), floor(((your_poke.base_atk + (your_poke.base_s_atk * .2)) * .1)))) - ((their_poke.base_def * .5) + (their_poke.base_s_def * .2)) + randint(-floor((((their_poke.base_def * .5) + (their_poke.base_s_def * .2)) * .1)), floor((((their_poke.base_def * .5) + (their_poke.base_s_def * .2)) * .1))))
                if your_attack < 0: your_attack = 0
                their_hp -= your_attack
                turn = False
                if your_attack == 0: 
                    battle_log.append(f'{your_poke.name} attacks {their_poke.name} but does no damage!')
                else:
                    battle_log.append(f'{your_poke.name} attacks {their_poke.name} and deals {your_attack} damage!')
            else:
                their_attack = floor(((their_poke.base_atk + (their_poke.base_s_atk * .2)) + randint(-floor(((their_poke.base_atk + (their_poke.base_s_atk * .2)) * .1)), floor(((their_poke.base_atk + (their_poke.base_s_atk * .2)) * .1)))) - ((your_poke.base_def * .5) + (your_poke.base_s_def * .2)) + randint(-floor((((your_poke.base_def * .5) + (your_poke.base_s_def * .2)) * .1)), floor((((your_poke.base_def * .5) + (your_poke.base_s_def * .2)) * .1))))
                if their_attack < 0: their_attack = 0
                your_hp -= their_attack
                turn = True
                if their_attack == 0: 
                    battle_log.append(f'{their_poke.name} attacks {your_poke.name} but does no damage!')
                else:
                    battle_log.append(f'{their_poke.name} attacks {your_poke.name} and deals {their_attack} damage!')
        if your_hp <= 0:
            your_counter += 1
            your_new = True
            battle_log.append(f'{your_poke.name} has fainted!')
        else:
            their_counter += 1
            their_new = True
            battle_log.append(f'{their_poke.name} has fainted!')
    if your_counter == len(your_squad):
        battle_log.append(f'{opponent.username} is the victor!')
        output = Output(opponent, battle_log)
        return output
    else: 
        battle_log.append(f'{current_user.username} is the victor!')
        output = Output(current_user, battle_log)
        return output

@main.route('/battle_progress/<opp_id>')
@login_required
def battle_progress(opp_id):
    opponent = User.query.get(opp_id)
    opp_squad = opponent.caught.all()
    your_squad = current_user.caught.all()
    winner = battle(your_squad, opp_squad, opponent)
    session['winner'] = winner.victor.id
    session['log'] = winner.log
    return render_template('battle_progress.html', opp_squad=opp_squad, opponent=opponent, your_squad=your_squad)


@main.route('/battle_results/<opp_id>')
@login_required
def battle_results(opp_id):
    try:
        opponent = User.query.get(opp_id)
        opp_squad = opponent.caught.all()
        your_squad = current_user.caught.all()
        class Output:
            def __init__(self, victor, log):
                self.victor = victor
                self.log = log
        winner = Output(User.query.get(session['winner']), session['log'])
        victory = BattleRecord(current_user.id, opponent.id, winner.victor.id)
        victory.save()

        return render_template('battle_results.html', opp_squad=opp_squad, opponent=opponent, your_squad=your_squad, winner=winner)
    except KeyError: return render_template('battle_results.html', error=True)

@main.after_request
def log_clear(response):
    try:
        if '/battle_results/' in request.path:
            del session['winner']
            del session['log']
            return response
    except KeyError: return response
    return response

@main.route('/test')
@login_required
def test():
    attack = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.aggressor_id).all()))
    defend = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.defender_id).all()))
    victories = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.victor_id).all()))
    total = int(attack) + int(defend)
    return f'attack: {attack} defend: {defend} victories: {victories} total fights: {total}'

@main.route('/record')
@login_required
def record():
    attack = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.aggressor_id).all()))
    defend = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.defender_id).all()))
    victories = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.victor_id).all()))
    total = int(attack) + int(defend)
    if total:
        return render_template('battle_record.html', attack=attack, defend=defend, victories=victories, total=total)
    else: return render_template('battle_record.html', error=True)