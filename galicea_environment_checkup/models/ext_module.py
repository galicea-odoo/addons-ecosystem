# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models

from ..environment_checkup import dependencies
from ..environment_checkup.runtime import display_data

class Module(models.Model):
    _inherit = 'ir.module.module'

    dependency_checks = fields.Text(
        compute='_compute_dependency_checks'
    )

    @api.one
    def _compute_dependency_checks(self):
        checks = dependencies.get_checks_for_module_recursive(self)
        self.dependency_checks = json.dumps(display_data(self.env, checks))
