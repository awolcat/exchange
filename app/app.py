#!/usr/bin/env python3

import hashlib
from datetime import timedelta
from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_session import Session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from uuid import uuid4
from utils.db_client import dbClient
from utils.redis import redisClient
from models.user import User
from globalpayments.gp import GP


login_manager = LoginManager()
login_manager.login_view = 'login'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'big secret'

# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_REDIS'] = redisClient.client

# Session(app)
login_manager.init_app(app)

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

@app.route('/card', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def card():
    if request.method == 'POST':
        form = request.form
        card = {
                'card_number': form['card_number'],
                'expiry': form['expiry'],
                'cvv': form['cvv'],
                'country': form['country'],
                'currency': form['currency'],
               }
        gp_client = GP(**card)
        verification = gp_client.verify()
        if verification.get('status') == 'VERIFIED':
            card_data = gp_client.store()
            card.update([('user_id', current_user.id),
                         ('payment_token', card_data['id']),
                         ('brand', card_data['card']['brand']),
                         ('masked_card_number', card_data['card']['masked_number_last4'])
                        ])
            dbClient.db.cards.insert_one(card)
            print(card)
        else:
            flash('There was a problem adding this card. Try again in a few minutes or try another card.')
    return render_template('card_form.html')


if __name__ == '__main__':
    app.run(debug=True)
