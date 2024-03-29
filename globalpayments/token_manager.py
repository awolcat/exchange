#!/usr/bin/python3
from datetime import datetime
import requests
import hashlib
import os
from utils.redis import redisClient


class TokenManager():
    URL = 'https://apis.sandbox.globalpay.com/ucp/accesstoken'

    headers = {
               'content-type': 'application/json',
               'x-gp-version': '2021-03-22'
              }

    nonce = str(datetime.now())
    app_id = os.getenv('APP_ID')
    app_key = os.getenv('APP_KEY')
    hash512 = hashlib.sha512()
    hash512.update(f'{nonce}{app_key}'.encode())
    secret = hash512.hexdigest()


    body = {
            'app_id': app_id,
            'nonce': nonce,
            'secret': secret,
            'grant_type': 'client_credentials',
           }

    def __init__(self):
        self.token = None

    def get_token(self):
        if not redisClient.get('gp_token'):
            self.refresh_token()
        return redisClient.get('gp_token')

    def refresh_token(self):
        response = requests.post(
                                 TokenManager.URL,
                                 headers=TokenManager.headers,
                                 json=TokenManager.body
                                )
        token = response.json().get('token')
        redisClient.set('gp_token', token, 3600 * 23)

tokenManager = TokenManager()
