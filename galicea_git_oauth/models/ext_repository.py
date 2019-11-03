# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from odoo import models

class Repository(models.Model):
    _inherit = 'galicea_git.repository'

    def authenticated_url(self, client):
        """
        @param application galicea_openid.application"""

        token = self.env['galicea_openid_connect.access_token'].sudo().retrieve_or_create(
            self.env.user.id,
            client.id
        )
        unauthenticated_url = self.url
        url_parts = urlparse(unauthenticated_url)
        return '{}://{}:bearer@{}{}'.format(
            url_parts.scheme,
            token.token,
            url_parts.netloc,
            url_parts.path,
        )
