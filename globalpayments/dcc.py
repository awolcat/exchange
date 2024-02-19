#!/usr/bin/env python3
"""Check card for Dynamic Currency Conversion
    capability
"""
from uuid import uuid4
from globalpayments.token_manager import tokenManager
from utils.db_client import dbClient

class DynamicCurrencyConversion():
    """Handle DCC checks
    """
    URL = 'https://apis.sandbox.globalpay.com/ucp/currency-conversions'
    headers = {
               'authorization': f'Bearer {tokenManager.get_token()}',
               'content-type': 'application/json',
               'x-gp-version': '2021-03-22'
               }
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
