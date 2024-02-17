from flask import request, render_template, redirect, url_for, flash, session
from . import battle
from flask_login import login_required, current_user
from app.models import User, db, BattleRecord


@battle.route('/battle')
@login_required
def battle_page():
    opponents = User.query.filter(User.id != current_user.id).all()
    op_info = []
    class OpInfo:
        def __init__(self, opponent, rec, vic):
            self.trainer = opponent
            self.rec = rec
            self.vic = vic
    for opponent in opponents:
        record = str(len(db.session.query(BattleRecord).filter(opponent.id == BattleRecord.defender_id).filter(current_user.id == BattleRecord.aggressor_id).all()) + len(db.session.query(BattleRecord).filter(opponent.id == BattleRecord.aggressor_id).filter(current_user.id == BattleRecord.defender_id).all()))
        victories = str(len(db.session.query(BattleRecord).filter(opponent.id == BattleRecord.defender_id).filter(current_user.id == BattleRecord.aggressor_id).filter(current_user.id == BattleRecord.victor_id).all()) + len(db.session.query(BattleRecord).filter(opponent.id == BattleRecord.aggressor_id).filter(current_user.id == BattleRecord.defender_id).filter(current_user.id == BattleRecord.victor_id).all()))
        trainer = OpInfo(opponent, record, victories)
        op_info.append(trainer)
    return render_template('battle.html', op_info=op_info)

@battle.route('/battle_preview/<opp_id>')
@login_required
def battle_preview(opp_id):
    opponent = User.query.get(opp_id)
    opp_squad = opponent.caught.all()
    return render_template('battle_preview.html', opp_squad=opp_squad, opponent=opponent)

def battler(your_squad, opp_squad, opponent):
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
            battle_log.append(f'You send out {your_poke.name}!')
        if their_new == True:
            their_hp = their_poke.base_hp
            their_new = False
            battle_log.append(f'{opponent.username} sends out {their_poke.name}!')
        if (your_poke.base_spd * (randint(80,120)/100)) > (their_poke.base_spd * (randint(80,120)/100)): turn = True
        else: turn = False
        while your_hp > 0 and their_hp > 0:
            if turn == True:
                your_attack = floor(((your_poke.base_atk + (your_poke.base_s_atk * .2)) + randint(-floor(((your_poke.base_atk + (your_poke.base_s_atk * .2)) * .1)), floor(((your_poke.base_atk + (your_poke.base_s_atk * .2)) * .1)))) - ((their_poke.base_def * .5) + (their_poke.base_s_def * .2)) + randint(-floor((((their_poke.base_def * .5) + (their_poke.base_s_def * .2)) * .1)), floor((((their_poke.base_def * .5) + (their_poke.base_s_def * .2)) * .1))))
                if your_attack < 0: your_attack = 0
                their_hp -= your_attack
                if their_hp < 0: their_hp = 0
                turn = False
                if your_attack == 0: 
                    battle_log.append(f'Your {your_poke.name} attacks their {their_poke.name} but does no damage! {their_hp} HP remaining!')
                else:
                    battle_log.append(f'Your {your_poke.name} attacks their {their_poke.name} and deals {your_attack} damage! {their_hp} HP remaining!')
            else:
                their_attack = floor(((their_poke.base_atk + (their_poke.base_s_atk * .2)) + randint(-floor(((their_poke.base_atk + (their_poke.base_s_atk * .2)) * .1)), floor(((their_poke.base_atk + (their_poke.base_s_atk * .2)) * .1)))) - ((your_poke.base_def * .5) + (your_poke.base_s_def * .2)) + randint(-floor((((your_poke.base_def * .5) + (your_poke.base_s_def * .2)) * .1)), floor((((your_poke.base_def * .5) + (your_poke.base_s_def * .2)) * .1))))
                if their_attack < 0: their_attack = 0
                your_hp -= their_attack
                if your_hp < 0: your_hp = 0
                turn = True
                if their_attack == 0: 
                    battle_log.append(f'Their {their_poke.name} attacks your {your_poke.name} but does no damage! {your_hp} HP remaining!')
                else:
                    battle_log.append(f'Their {their_poke.name} attacks your {your_poke.name} and deals {their_attack} damage! {your_hp} HP remaining!')
        if your_hp <= 0:
            your_counter += 1
            your_new = True
            battle_log.append(f'Your {your_poke.name} has fainted!')
        else:
            their_counter += 1
            their_new = True
            battle_log.append(f'Their {their_poke.name} has fainted!')
    if your_counter == len(your_squad):
        battle_log.append(f'{opponent.username} is the victor!')
        output = Output(opponent, battle_log)
        return output
    else: 
        battle_log.append(f'{current_user.username} is the victor!')
        output = Output(current_user, battle_log)
        return output

@battle.route('/battle_progress/<opp_id>')
@login_required
def battle_progress(opp_id):
    opponent = User.query.get(opp_id)
    opp_squad = opponent.caught.all()
    your_squad = current_user.caught.all()
    winner = battler(your_squad, opp_squad, opponent)
    session['winner'] = winner.victor.id
    session['log'] = winner.log
    return render_template('battle_progress.html', opp_squad=opp_squad, opponent=opponent, your_squad=your_squad)

# Something in this section causes a continual refresh of battle_progress I think? Render keeps saying GET battle_results and I now have 250 battles in my database. Not sure if it's because I'm using session to store a variable to move between battle_progress and battle_results?
@battle.route('/battle_results/<opp_id>')
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
        winner = Output(User.query.get(session.pop('winner')), session.pop('log'))
        victory = BattleRecord(current_user.id, opponent.id, winner.victor.id)
        victory.save()

        return render_template('battle_results.html', opp_squad=opp_squad, opponent=opponent, your_squad=your_squad, winner=winner)
    except KeyError: return render_template('battle_results.html', error=True)

# @battle.after_request
# def log_clear(response):
#     try:
#         if '/battle_results/' in request.path:
#             del session['winner']
#             del session['log']
#             return response
#     except KeyError:
#         return response
#     return response

@battle.route('/test')
@login_required
def test():
    attack = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.aggressor_id).all()))
    defend = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.defender_id).all()))
    victories = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.victor_id).all()))
    total = int(attack) + int(defend)
    return f'attack: {attack} defend: {defend} victories: {victories} total fights: {total}'

@battle.route('/record')
@login_required
def record():
    attack = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.aggressor_id).all()))
    defend = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.defender_id).all()))
    victories = str(len(db.session.query(BattleRecord).filter(current_user.id == BattleRecord.victor_id).all()))
    total = int(attack) + int(defend)
    if total:
        return render_template('battle_record.html', attack=attack, defend=defend, victories=victories, total=total)
    else: return render_template('battle_record.html', error=True)