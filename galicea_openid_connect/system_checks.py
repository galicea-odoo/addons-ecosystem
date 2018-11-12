# -*- coding: utf-8 -*-

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
        '<p>Odoo runs in a multi-DB mode, which will cause API request routing to fail.</p>'
        '<p>Run Odoo with <tt>--dbfilter</tt> or <tt>--database</tt> flag.</p>'
    )
    return CheckFail(
        'Odoo runs in a multi-DB mode.',
        details=details
    )
