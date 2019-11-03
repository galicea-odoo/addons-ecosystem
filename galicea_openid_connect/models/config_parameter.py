# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .. import random_tokens
try:
    from jwcrypto import jwk
except ImportError:
    pass

class ConfigParameter(models.Model):
  _inherit = 'ir.config_parameter'

  @api.model
  def openid_init_keys(self):
    keys = {
        'galicea_openid_connect.authorization_code_jwk': lambda: \
            jwk.JWK.generate(kty='oct', size=256, kid=random_tokens.alpha_numeric(16), use='sig', alg='HS256').export(),
        'galicea_openid_connect.id_token_jwk': lambda: \
            jwk.JWK.generate(kty='RSA', size=2054, kid=random_tokens.alpha_numeric(16), use='sig', alg='RS256').export()
    }

    for key, gen in iter(keys.items()):
        if not self.search([('key', '=', key)]):
            self.create({
                'key': key,
                'value': gen(),
                'group_ids': [(4, self.env.ref('base.group_erp_manager').id)]
            })
