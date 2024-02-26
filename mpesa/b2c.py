#!/usr/bin/env python3

import os
import requests
from uuid import uuid4
from mpesa.token_manager import MPESAToken
from OpenSSL import crypto, SSL
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import b64encode

security_credential = "d8kSHir0tMGn0cNo50b6ApgWU9Q9sMxTg5Volu6rqk6sWgznutz2tNbuo8xfHdoBRyl0R//FouFK5flDEjnMuUjuKaGD5N/UbaTUsDQPXHPngbYYdcyMZksIvffwXsCj/yqLGdxKdZFAcxH76LgVxFGBYmFa4zrnPNfEyTaUvtXqp4cb2C/2et2rVgRokrVfleuOJIvZ5npHLQmnBqHWGwmZw/W4Mv0VoXc7BwLNmm2a7qlpg9DgLKZ3uqgnjjEZLB+IPTRLbrsJ5+oQ0m/26DzyO4dok1b5YJlV6uWLk4IxE+T0dWbzXtOOis7pHRr+xh1t2w6ILvs3BB8mGO3qqA=="

def b2c():

    token = MPESAToken().get_token()
    headers = {
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
              }
    initiator_pwd = "Safaricom999!*!"
    folder = os.getcwd()
    cert_path = f"{folder}/mpesa/SandboxCertificate.cer"
    with open(cert_path, encoding='utf-8') as f:
        cert = f.read()
        cert_x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        pkey = cert_x509.get_pubkey()
        cryptography_key = pkey.to_cryptography_key()
        credential = cryptography_key.encrypt(initiator_pwd.encode('utf-8'), padding.PKCS1v15())
        security_cred = b64encode(credential).decode()
    payload = {
               "OriginatorConversationID": str(uuid4()),
               "InitiatorName": "testapi",
               "SecurityCredential": security_cred,
               "CommandID": "BusinessPayment",
               "Amount": 10,
               "PartyA": 600999,
               "PartyB": 254708374149,
               "Remarks": "Test remarks",
               "QueueTimeOutURL": "https://clear-hopefully-ladybird.ngrok-free.app/b2ctimeout",
               "ResultURL": "https://clear-hopefully-ladybird.ngrok-free.app/b2cresult",
               "Occasion": "occasion",
               }
    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/b2c/v3/paymentrequest', headers = headers, json = payload)
    return response.text.encode('utf8')
