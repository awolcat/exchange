#!/usr/bin/env python3

import hashlib
from datetime import timedelta, datetime, timezone
from bson.objectid import ObjectId
from flask import Flask, render_template, request, flash, session, redirect, url_for, abort
from flask_session import Session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from uuid import uuid4
from utils.db_client import dbClient
from utils.redis import redisClient
from models.user import User
from globalpayments.gp import GP
from mpesa.b2c import b2c
from utils.currency_rate import rates


login_manager = LoginManager()
login_manager.login_view = 'login'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'big secret'

# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_REDIS'] = redisClient.client

# Session(app)
login_manager.init_app(app)

@app.errorhandler(404)
def handle(error):
    return {'error': 'Not Found'}

@app.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    if request.method == 'POST':
        encoded_pwd = request.form['password'].encode('utf-8')
        password = hashlib.sha1(encoded_pwd).hexdigest()
        user = {
                'firstname': request.form['firstname'],
                'lastname': request.form['lastname'],
                'number': request.form['mpesa_number'],
                'password': password
               }
        db_user = dbClient.db.users.find_one({'number': user['number']})
        if db_user:
            flash('This number is already registered')
        userId = dbClient.db.users.insert_one(user).inserted_id

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    if request.method == 'POST':
        number = request.form['mpesa_number']
        pwd = request.form['password'].encode('utf-8')
        password = hashlib.sha1(pwd).hexdigest()
        user = dbClient.db.users.find_one({'number': number})
        if not user:
            flash('No User Found')
            return render_template(login.html)
        user['_id'] = str(user['_id'])
        user_obj = User(**user)
        if user_obj.password == password:
            login_user(user_obj, duration=timedelta(minutes=30))
            flash('Login Success!')
            user_cards = dbClient.db.cards.find({'user_id': user_obj.id})
            length = 0
            for c in user_cards:
                length += 1
            user_cards.close()
            if length > 0:
                return redirect(url_for('change'))
            return redirect(url_for('card'))
        else:
            flash('Wrong username or password')
    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/logout', strict_slashes=False)
@login_required
def logout():
    logout_user()
    return render_template('login.html')

@app.route('/me')
@login_required
def me():
    user = dbClient.db.users.find_one({'_id': ObjectId(current_user.id)})
    user['_id'] = str(user['_id'])
    user = User(**user)
    cards_curs = dbClient.db.cards.find({'user_id': user.id})
    cards = [c for c in cards_curs]
    cards_curs.close()
    transactions_c = dbClient.db.transactions.find({'user_id': user.id})
    transactions = [t for t in transactions_c]
    return render_template('profile.html', cards=cards, user=user, transactions=transactions)

@app.route('/card', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def card():
    if request.method == 'POST':
        form = request.form
        card = {
                'card_number': form['card_number'],
                'expiry': form['expiry'],
                'cvv': form['cvv'],
               }
        gp_client = GP(**card)
        
        try:
            verification = gp_client.verify()
            dcc_check = gp_client.dcc(200)
            if verification.get('status') == 'VERIFIED':
                card_data = gp_client.store()
                card.update([('user_id', current_user.id),
                         ('payment_token', card_data['id']),
                         ('brand', card_data['card']['brand']),
                         ('masked_card_number', card_data['card']['masked_number_last4']),
                         ('card_currency', dcc_check.get('payer_currency')),
                         ('usd_rate', dcc_check.get('exchange_rate'))
                        ])
                dbClient.db.cards.insert_one(card)
                flash('Card was added successfully. Try making a withdrawal.')
                return redirect(url_for('me'))
        except Exception as err:
            flash('There was a problem adding this card. Try again in a few minutes or try another card.')
    return render_template('card_form.html')

@app.route('/payments', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def change():

    cards_cursor = dbClient.db.cards.find({'user_id': current_user.id})
    cards = [card for card in cards_cursor]
    cards_cursor.close()
    cards = rates(cards)
    if request.method == 'POST':
        amount = request.form['amount']
        masked_card = request.form['selection']
        card = None
        for c in cards:
            if c['masked_card_number'] == masked_card:
                card = c
        if not card:
            abort(404)
        gp_client = GP(**card)
        response = gp_client.transact(amount)
        
        try:
            success = response.get('action').get('result_code')
        except Exception:
            success = None
        
        if success == 'SUCCESS':
            dbClient.db.transactions.insert_one({
                                                 'user_id': current_user.id,
                                                 'gp_reference': response['reference'],
                                                 'amount': amount,
                                                 'datetime': datetime.now(timezone.utc).strftime('%a %d %b %Y, %I:%M%p'),
                                                 'payer_amount': response['currency_conversion']['payer_amount'],
                                                 'card_currency': card['card_currency']
                                                 })
            """for cc in cards:
                if cc['masked_card_number'] == card['masked_card_number']:
            """
            selected_cc = card
            
            kes_amt = float(selected_cc['blended_rate']) * float(amount)
            try:
                b2c_response = b2c(round(kes_amt))
                dbClient.db.transactions.update_one({'gp_reference': response['reference']},
                                                    { '$set': {
                                                               'masked_card': selected_cc['masked_card_number'],
                                                               'mpesa_reference': b2c_response['ConversationID'],
                                                               'kes_amount': round(kes_amt),
                                                              }
                                                    })
                flash('Transaction Success!')
                return render_template('payments.html', cards=cards)
            except Exception as err:
                # retry mpesa b2c
                flash('Your card was debited, but the Mpesa transaction failed. Send us the transaction reference to request a refund')
        else:
            flash(f"Transaction Failed!\nReason: {response['error_code']}")
    return render_template('payments.html', cards=cards)

@app.route('/b2c', methods=['GET', 'POST'])
def send_moni():
    response = b2c()
    return response

@app.route('/b2cresult', methods=['POST'], strict_slashes=False)
@login_required
def b2cresult():
    return '<p>Result received?</p>'

@app.route('/b2ctimeout', methods=['POST'], strict_slashes=False)
@login_required
def b2ctimeout():
    return '<p>Timeout received?</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
