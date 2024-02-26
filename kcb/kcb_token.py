#!/usr/bin/env python3

import base64
from utils.redis import redisClient
import requests

class KCBToken():
    URL = 'https://wso2-api-gateway-direct-kcb-wso2-gateway.apps.test.aro.kcbgroup.com/token'

    API_KEY = 'miVoS3Q7GlDbDhUP_JhHJRIt6d8a'
    SECRET = 'eJvEuh_WdHnSgg2xajzVLVcNUDQa'

    def __init__(self):
        self.token = None

    def get_token(self):
        if not redisClient.get('kcb_token'):
            self.refresh_token()
        return redisClient.get('kcb_token')

    def refresh_token(self):
        base = f'{self.API_KEY}:{self.SECRET}'
        token = base64.b64encode(base.encode()).decode()
        headers = {'Authorization': f'Basic {token}'}
        body = {'grant_type': 'client_credentials'}
        response = requests.post(self.URL, headers=headers, data=body, verify=False)
        try:
            kcb_token = response.json().get('access_token')
            redisClient.set('kcb_token', kcb_token, 3300)
        except Exception as err:
            raise err
