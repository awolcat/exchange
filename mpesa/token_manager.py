#!/usr/bin/env python3

import requests
import base64
from utils.redis import redisClient

class MPESAToken():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate"
    username = "XNnNSz3TmyFsSJ1C7bwktTQht8TwxrRtrA0GusxrdYLGfcOq"
    password = "Ukln6WdcnXsXS4PTKgHWOk9nuSAWJ2ApeFx8lDBgAuhSXUUmSGfNi5G0dvhjDKBe"
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    params = {"grant_type": "client_credentials"}

    def __init__(self):
        pass

    def get_token(self):
        if not redisClient.get("mpesa_token"):
            self.refresh_token()
        return redisClient.get("mpesa_token")

    def refresh_token(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        #if response.status_code == 200:
        try:
            token = response.json()
            redisClient.set("mpesa_token", token["access_token"], int(token["expires_in"]))
        except Exception:
            raise Exception("Could not refresh Daraja Consumer Token")

    def print_basic(self):
        print(self.token)