#!/usr/bin/env python3
"""Global Payments API methods
"""
import requests
from uuid import uuid4
from globalpayments.token_manager import tokenManager
from utils.db_client import dbClient


class GP():

    api = 'https://apis.sandbox.globalpay.com/ucp/'

    headers = {
               'authorization': f'Bearer {tokenManager.get_token()}',
               'content-type': 'application/json',
               'x-gp-version': '2021-03-22'
              }

    channel = "CNP"

    def __init__(self, **kwargs):
        self.country = kwargs.get('country')
        self.currency = kwargs.get('currency')
        self.card_number = kwargs.get('card_number')
        self.cvv = kwargs.get('cvv')
        self.exp_month = kwargs.get('expiry').split('/')[0]
        self.exp_year = kwargs.get('expiry').split('/')[1]

    def verify(self):
        url = f'{GP.api}verifications'
        body = {
                'account_name': 'transaction_processing',
                'channel': GP.channel,
                'currency': self.currency,
                'reference': str(uuid4()),
                'country': self.country,
                'payment_method': {
                                   'entry_mode': 'ECOM',
                                   'card': {
                                            'number': self.card_number,
                                            'expiry_month': self.exp_month,
                                            'expiry_year': self.exp_year
                                           }
                                  }
               }
        response = requests.post(url, headers=GP.headers, json=body)
        return response.json()

    def store(self):
        url = f'{GP.api}payment-methods'
        body = {'reference': str(uuid4()),
                'usage_mode': 'MULTIPLE',
                'card': {
                         'number': self.card_number,
                         'expiry_month': self.exp_month,
                         'expiry_year': self.exp_year,
                         'cvv': self.cvv
                        }
                }
        response = requests.post(url, headers=GP.headers, json=body)
        return response.json()

    def dcc():
        """Handle DCC checks
        """
        URL = f'{GP.api}currency-conversions'
        
        body = {
                "account_name": "DCC",
                "channel": "CNP",
                "amount": "10000",
                "currency": "USD",
                "country": "US",
                "reference": "becf9f3e-4d33-459c-8ed2-0c4affc9555e",
                "payment_method": {
                                   "name": "James Mason",
                                   "entry_mode": "ECOM",
                                   "card": {
                                            "number": "4006097467207025",
                                            "expiry_month": "05",
                                            "expiry_year": "25"
                                            }
                                  }
              }
