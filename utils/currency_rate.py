#!/usr/bin/env python3

import os.path as op
import urllib.request
from datetime import date

from currency_converter import ECB_URL, CurrencyConverter

def rates(user_cards):
    # Get today's rates
    filename = f"ecb_{date.today():%Y%m%d}.zip"
    if not op.isfile(filename):
        urllib.request.urlretrieve(ECB_URL, filename)
    c = CurrencyConverter(filename)
    
    # Add blended rates to card data for template
    cards = []
    for card in user_cards:
        usd_rate = c.convert(1, card['card_currency'], 'USD')
        kes_rate = c.convert(1, 'USD', 'KES')
        blended_rate = usd_rate * kes_rate
        card['blended_rate'] = blended_rate
        cards.push(card)
    return cards
        
