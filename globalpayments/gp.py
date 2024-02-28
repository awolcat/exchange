#!/usr/bin/env python3
"""Global Payments API methods
"""
import requests
from uuid import uuid4
from bson.objectid import ObjectId
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
    country = 'KE'
    currency = 'USD'

    def __init__(self, **kwargs):
        self.card_number = kwargs.get('card_number')
        self.cvv = kwargs.get('cvv')
        self.exp_month = kwargs.get('expiry').split('/')[0]
        self.exp_year = kwargs.get('expiry').split('/')[1]
        self.dcc_id = kwargs.get('dcc_id')

    def verify(self):
        url = f'{GP.api}verifications'
        body = {
                'account_name': 'transaction_processing',
                'channel': GP.channel,
                'currency': GP.currency,
                'reference': str(uuid4()),
                'country': GP.country,
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

    def dcc(self, amount):
        """Handle DCC checks
        """
        import pprint
        url = f'{GP.api}currency-conversions'
        #"name": f"{user['firstname']} {user['lastname']}",
        body = {
                "account_name": "dcc",
                "channel": GP.channel,
                "amount": amount,
                "currency": GP.currency,
                "country": GP.country,
                "reference": str(uuid4()),
                "payment_method": {
                                   "entry_mode": "ECOM",
                                   "card": {
                                            "number": self.card_number,
                                            "expiry_month": self.exp_month,
                                            "expiry_year": self.exp_year
                                            }
                                  }
              }
        response = requests.post(url, headers=GP.headers, json=body)
        return response.json()


    def transact(self, amount):
        #dcc_check = self.dcc(amount)
        #print(dcc_check)
        #dcc_id = dcc_check.get('status', None)
        url = f'{GP.api}transactions'

        body = {
                'account_name': 'transaction_processing',
                'type': 'SALE',
                'channel': GP.channel,
                'country': GP.country,
                'amount': amount,
                'currency': GP.currency,
                'reference': str(uuid4()),
                'payment_method': {
                                   'entry_mode': 'ECOM',
                                   'card': {
                                            'number': self.card_number,
                                            'expiry_month': self.exp_month,
                                            'expiry_year': self.exp_year
                                            }
                                   }
                }
        temp = {'currency_conversion': {'id': self.dcc_id}, }
        body.update(temp)
        response = requests.post(url, headers=GP.headers, json=body)
        return response.json()

    def bins(self):
        url = f'{GP.api}currency-conversions/dcc-bin-ranges'
        params = {'account_name': 'transaction_processing', 'country': 'US', 'merchant_currency': 'USD'}
        response = requests.get(url, headers=GP.headers, params=params)
        return response.json()

    def accounts(self):
        url =  f'{GP.api}accounts'
        #GP.headers.pop('x-gp-version')
        response = requests.get(url, headers=GP.headers)
        print("ACCOUNTS", response.json())
