#!/usr/bin/env/ python3

from uuid import uuid4
from kcb.kcb_token import KCBToken
import requests

def kcb_funds_transfer():
    
    url = "https://uat.buni.kcbgroup.com/fundstransfer/1.0.0/api/v1/transfer"
    token = KCBToken().get_token()
    headers = {'Authorization': f'Bearer {token}',
               'content-type': 'application/json'}
    body = {
            "beneficiaryDetails": "ALBERT IRURA MATHENGE",
            "companyCode": "KE0010001",
            "creditAccountNumber": "705112734",
            "currency": "KES",
            "debitAccountNumber": "1281902993",
            "debitAmount": 10,
            "paymentDetails": "fee payment",
            "transactionReference": str(uuid4()),
            "transactionType": "MO",
            "beneficiaryBankCode": "MPESA"
            }

    response = requests.post(url, headers=headers, json=body)
    print(response.json())
