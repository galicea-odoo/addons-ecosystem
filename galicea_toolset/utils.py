# -*- coding: utf-8 -*-

from odoo import http

def get_base_url(env):
    """
    Better host name detection
    @param env odoo.api.Environment"""

    if http.request:
        # Preferuj nazwę hosta, która została użyta do tego zapytania
        return http.request.httprequest.host_url
    else:
        # Jeśli nie jesteśmy wewnątrz zapytania HTTP, zwróć domenę ostatnio użytą
        # przez admina do zalogowania
        return env['ir.config_parameter'].get_param('web.base.url') + '/'
