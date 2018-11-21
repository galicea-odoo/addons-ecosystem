# -*- coding: utf-8 -*-

import os

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ConfigSettings(models.TransientModel):
    _name = 'galicea_git.config.settings'
    _inherit = 'res.config.settings'

    git_http_backend = fields.Char(
        'Absolute path to Git HTTP backend',
        required=True
    )
    git_http_backend_valid = fields.Boolean(
        compute='_compute_git_http_backend_valid'
    )

    @api.one
    @api.depends('git_http_backend')
    def _compute_git_http_backend_valid(self):
        self.git_http_backend_valid = self.git_http_backend and os.access(self.git_http_backend, os.X_OK)

    @api.one
    def set_params(self):
        self.env['ir.config_parameter'].set_param('galicea_git.git_http_backend', self.git_http_backend)

    @api.model
    def get_default_values(self, fields):
        return {
            'git_http_backend': self.env['ir.config_parameter'].get_param('galicea_git.git_http_backend')
        }

    @api.multi
    def execute(self):
        self.ensure_one()
        if not self.env.user.has_group('galicea_git.group_admin'):
            raise AccessError("Only Git administrators can change those settings")
        super(ConfigSettings, self.sudo()).execute()
        act_window = self.env.ref('galicea_git.config_settings_action')
        return act_window.read()[0]
