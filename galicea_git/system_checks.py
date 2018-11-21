# -*- coding: utf-8 -*-

import os

from odoo.addons.galicea_environment_checkup import \
        custom_check, CheckWarning, CheckSuccess, CheckFail
from odoo import http

@custom_check
def check_single_db(env):
    if not http.request:
        raise CheckWarning('Could not detect DB settings.')

    dbs = http.db_list(True, http.request.httprequest)
    if len(dbs) == 1:
        return CheckSuccess('Odoo runs in a single-DB mode.')

    details = (
        '<p>Odoo runs in a multi-DB mode, which will cause Git HTTP requests to fail.</p>'
        '<p>Run Odoo with <tt>--dbfilter</tt> or <tt>--database</tt> flag.</p>'
    )
    return CheckFail(
        'Odoo runs in a multi-DB mode.',
        details=details
    )

@custom_check
def check_http_backend(env):
    backend_path = env['ir.config_parameter'].sudo().get_param(
        'galicea_git.git_http_backend'
    )
    if not os.access(backend_path, os.X_OK):
        raise CheckFail(
            'Git HTTP backend not found',
            details='<a href="http://galicea.mw-odoo:8080/web#action=galicea_git.config_settings_action">Check the configuration here</a>'
        )
    return CheckSuccess('Git HTTP backend was found')
