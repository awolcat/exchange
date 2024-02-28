#!/usr/bin/env python3

import os.path as op
import urllib.request
from datetime import date

#from forex_python.converter import CurrencyRates

def rates(user_cards):
    # Get today's rates
    """
    filename = f"ecb_{date.today():%Y%m%d}.zip"
    if not op.isfile(filename):
        urllib.request.urlretrieve(ECB_URL, filename)
    c = CurrencyConverter(filename)
    """
    # Add blended rates to card data for template
    cards = []
    for card in user_cards:
        blended_rate = 130
        card['blended_rate'] = blended_rate
        cards.append(card)
    return cards
        
