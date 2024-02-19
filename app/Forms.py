#!/usr/bin/env python3

from wtforms import Form, BooleanField, StringField, validators

class RegistrationForm(Form):
    firstname = StringField('First Name', [validators.Length(min=2, max=25),
                                           validators.InputRequired(message='Field cannot be blank')]
                           )
    lastname = StringField('Last Name', [validators.Length(min=2, max=25),
                                         validators.InputRequired(message='Field cannot be blank')]
                          )
    mpesa_number = StringField('MPesa Number', [validators.Length(min=10, max=10),
                                                validators.InputRequired(message='Field cannot be blank')]
                              )
    password = StringField('Password', [validators.Length(min=8, max=25),
                                        validators.InputRequired(message='Field cannot be blank')]
                          )
    accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
