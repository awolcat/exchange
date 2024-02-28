#!/usr/bin/env python3

import os.path as op
import currencyapicom
import urllib.request
from datetime import date
from utils.redis import redisClient


def rates(user_cards):
    dollar_to_kes = 140
    try:
        client = currencyapicom.Client('cur_live_pOq9MrqxZeXITzs9estGrFkFUNZx1PcjF2qkuJb1')
        # Add blended rates to card data for template
        result = client.latest(currencies=['KES'])
        dollar_to_kes = result['data']['KES']['value']
        redisClient.set('dollar_to_kes', dollar_to_kes, 3600 * 72)
    except Exception as err:
        dollar_to_kes = redisClient.get('dollar_to_kes')
    cards = []
    for card in user_cards:
        usd_rate = float(card['usd_rate'])
        dollar_to_kes = dollar_to_kes
        blended_rate = usd_rate * dollar_to_kes
        card['blended_rate'] = str(blended_rate)
        cards.append(card)
    return cards
        
