#!/usr/bin/python3
from datetime import datetime
import requests
import hashlib
from utils.redis import redisClient


class TokenManager():
    URL = 'https://apis.sandbox.globalpay.com/ucp/accesstoken'

    headers = {
               'content-type': 'application/json',
               'x-gp-version': '2021-03-22'
              }

    nonce = str(datetime.now())
    app_id = 'n1ieSIBgznD9J6NK7lJ6Y3WivSCsG50s'
    app_key = 'HY0XBroPop0x2efG'
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
        return self.token

    def refresh_token(self):
        response = requests.post(
                                 TokenManager.URL,
                                 headers=TokenManager.headers,
                                 json=TokenManager.body
                                )
        token = response.json().get('token')
        redisClient.set('gp_token', token, 3600 * 23)
        self.token = token

tokenManager = TokenManager()
