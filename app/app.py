#!/usr/bin/env python3

import hashlib
from flask import Flask, render_template, request, flash, session
from flask_session import Session
from utils.db_client import dbClient
from utils.redis import redisClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'big secret'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redisClient.client

Session(app)

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
            return 'A user has already registered this number', 401
        userId = dbClient.db.users.insert_one(user).inserted_id

        return render_template('signup.html', user=user)
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
        if user['password'] == password:
            session['user'] = user
            flash('Login Success!')
            return 'Hallo'
        else:
            return 'No BUENO'
    return render_template('login.html')

@app.route('/logout', strict_slashes=False)
def logout():
    flag = session.pop('user', None)
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
