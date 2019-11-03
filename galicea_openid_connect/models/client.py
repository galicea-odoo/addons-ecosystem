# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .. import random_tokens

class Client(models.Model):
    _name = 'galicea_openid_connect.client'
    _description = 'OpenID Connect client'

    name = fields.Char(required=True)
    auth_redirect_uri = fields.Char('Redirect URI for user login')
    client_id = fields.Char(
        string='Client ID',
        required=True,
        readonly=True,
        index=True,
        default=lambda _: random_tokens.lower_case(16),
    )
    secret = fields.Char(
        string='Client secret',
        required=True,
        readonly=True,
        default=lambda _: random_tokens.alpha_numeric(32),
        groups='galicea_openid_connect.group_admin'
    )
    system_user_id = fields.Many2one(
        'res.users',
        'Artificial user representing the client in client credentials requests',
        readonly=True,
        required=True,
        ondelete='restrict'
    )
    allow_password_grant = fields.Boolean(
        string='Allow OAuth2 password grant',
        default=False,
    )

    @api.model
    def __system_user_name(self, client_name):
        return '{} - API system user'.format(client_name)

    @api.model
    def create(self, values):
        if 'name' in values:
            system_user = self.env['res.users'].create({
                'name': self.__system_user_name(values['name']),
                'login': random_tokens.lower_case(8),
                'groups_id': [(4, self.env.ref('galicea_openid_connect.group_system_user').id)]
            })
            # Do not include in the "Pending invitations" list
            system_user.sudo(system_user.id)._update_last_login()
            values['system_user_id'] = system_user.id
        return super(Client, self).create(values)

    @api.multi
    def write(selfs, values):
        super(Client, selfs).write(values)
        if 'name' in values:
            selfs.mapped(lambda client: client.system_user_id).write({
                'name': selfs.__system_user_name(values['name'])
            })
        return True

    @api.multi
    def unlink(selfs):
        users_to_unlink = selfs.mapped(lambda client: client.system_user_id)
        ret = super(Client, selfs).unlink()
        users_to_unlink.unlink()
        return ret
