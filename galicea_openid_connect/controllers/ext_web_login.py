# -*- coding: utf-8 -*-

import time

from odoo import http
from odoo.addons import web

class Home(web.controllers.main.Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        result = super(Home, self).web_login(redirect, **kw)
        if result.is_qweb and 'force_auth_and_redirect' in kw:
            result.qcontext['redirect'] = kw['force_auth_and_redirect']
        if http.request.params.get('login_success'):
            http.request.session['auth_time'] = int(time.time())
        return result
