# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .. import random_tokens

class AccessTokenBase(models.AbstractModel):
    _name = 'galicea_openid_connect.access_token_base'

    token = fields.Char(
        readonly=True,
        required=True,
        default=lambda _: random_tokens.alpha_numeric(64),
        index=True,
    )
    client_id = fields.Many2one(
        'galicea_openid_connect.client',
        readonly=True,
        index=True,
        required=True,
        ondelete='cascade'
    )

class AccessToken(models.Model):
    _inherit = 'galicea_openid_connect.access_token_base'
    _name = 'galicea_openid_connect.access_token'
    _description = 'Acccess token representing user-client pair'

    user_id = fields.Many2one(
        'res.users',
        required=True,
        readonly=True,
        index=True,
        ondelete='cascade'
    )

    @api.model
    def retrieve_or_create(self, user_id, client_id):
        existing_tokens = self.search(
            [
                ('user_id', '=', user_id),
                ('client_id', '=', client_id),
            ]
        )
        if existing_tokens:
            return existing_tokens[0]
        else:
            return self.create({'user_id': user_id, 'client_id': client_id})

class ClientAccessToken(models.Model):
    _inherit = 'galicea_openid_connect.access_token_base'
    _name = 'galicea_openid_connect.client_access_token'
    _description = 'Access token representing client credentials'

    @api.model
    def retrieve_or_create(self, client_id):
        existing_tokens = self.search(
            [
                ('client_id', '=', client_id),
            ]
        )
        if existing_tokens:
            return existing_tokens[0]
        else:
            return self.create({'client_id': client_id})
