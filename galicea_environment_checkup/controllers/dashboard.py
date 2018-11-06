# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request

from ..environment_checkup.runtime import all_installed_checks, display_data
from ..environment_checkup.core import CheckResult

class Dashboard(http.Controller):
    @http.route('/galicea_environment_checkup/data', type='json', auth='user')
    def data(self, request, **kw):
        if not request.env.user.has_group('base.group_erp_manager'):
            raise AccessError("Access Denied")

        checks = all_installed_checks(request.env)
        response = display_data(request.env, checks)

        priority = {
            CheckResult.FAIL: 0,
            CheckResult.WARNING: 1,
            CheckResult.SUCCESS: 2
        }
        response.sort(key=lambda res: (priority[res['result']], res['module']))

        return response
