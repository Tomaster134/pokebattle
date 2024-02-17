from flask import request, render_template, redirect, url_for, flash, session
from . import battle
from flask_login import login_required, current_user
from app.models import User, db, BattleRecord

#Opponents is a list of all users, with a class that stores the ID of the opponent, as well as the number of times fought and number of times defeated. Used a class just so I can iterate through users without having to use some kind of index range to make sure all the variables are properly associated with each other. Jinja gets a little cranky with multiple variables in a for loop
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

#Pretty straightforward, just displays the opponent's squad, having gotten the opponent ID passed in from the previous "battle" page
@battle.route('/battle_preview/<opp_id>')
@login_required
def battle_preview(opp_id):
    opponent = User.query.get(opp_id)
    opp_squad = opponent.caught.all()
    return render_template('battle_preview.html', opp_squad=opp_squad, opponent=opponent)

#Function that actually performs the math to determine the winner of the battle. Pokemon turn order is determined by base_spd, and pokemon then take turns attacking each other, with base_def & base_s_def blocking some damage. HP persists between opponents, and fainted pokemon are eliminated. Random integers are used to introduce variability to the battles. Used a class to return both the winner of the battle and a record of each move that occurred during the battle.
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

#Route calls the battle function, and assigns the instatiated object to a "winner" variable. This variable is then used to assign the variables of "winner" and "log" in the "session" dictionary. The "session" is used to be able to pass the two variables from this page to the results page to prevent repeated refreshing of a page to rack up wins.
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

# It's hitting the battle_results page because the result of the victory is being logged in the database, so the variable is being passed between the two routes. Why does it want to circle back though? Is it the URL redirect?

#wasn't even really because of the route. JavaScript just kept resubmitting because it was taking too long to get the next page loaded and it was set to submit a url_for when the counter was less than or equal to 0, so it just kept resubmitting every 1000ms. Fixed by only having it call the next URL when counter hits zero.

#Battle results page pops off the two "session" values to display the winner and battle log. This clears those entries so if you refresh the page, you are told you need to fight another battle to see a new set of results.
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

#Didn't end up needing this because I used .pop to clean the session entries, but still want to keep it so I can remember about .after_request

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

# Fairly simple route that just displays some stats about how many battles you've fought, how many you started, etc etc
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