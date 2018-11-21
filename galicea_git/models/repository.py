# -*- coding: utf-8 -*-

import os
import random
import shutil
import string
import subprocess

from odoo import models, fields, api, http
from odoo.exceptions import ValidationError
from odoo.tools import config, which

class Repository(models.Model):
    _name = 'galicea_git.repository'

    state = fields.Selection(
        [('draft', 'Draft'), ('created', 'Created')],
        default='draft'
    )

    name = fields.Char('User-friendly name', required=True)
    system_name = fields.Char(
        'Directory name',
        required=True,
        readonly=True,
        index=True,
        states={'draft': [('readonly', False)]}
    )
    collaborator_ids = fields.Many2many(
        'res.users',
        string='Collaborators'
    )

    local_directory = fields.Char(
        'Local directory on server',
        compute='_compute_local_directory',
        groups='galicea_git.group_admin'
    )
    url = fields.Char(
        'Clone',
        compute='_compute_url'
    )

    @api.one
    @api.depends('system_name')
    def _compute_url(self):
        base_url = http.request.httprequest.host_url if http.request \
                else env['ir.config_parameter'].get_param('web.base.url') + '/'
        self.url = u'{}git/{}'.format(base_url, self.system_name)

    @api.one
    @api.depends('system_name')
    def _compute_local_directory(self):
        if self.system_name:
            self.local_directory = os.path.join(config['data_dir'], 'git', self.system_name)

    @api.constrains('system_name')
    def _validate_system_name(self):
        allowed_characters = string.ascii_lowercase + string.digits + '-'
        if not all(c in allowed_characters for c in self.system_name):
            raise ValidationError(
                'Only lowercase, digits and hyphens (-) are allowed in directory name'
            )

    @api.constrains('collaborator_ids')
    def _validate_collaborator_ids(self):
        invalid_collaborators = self.collaborator_ids.filtered(lambda c: not c.has_group('galicea_git.group_collaborator'))
        if invalid_collaborators:
            raise ValidationError(
                'User {} does not have the {} role. Contact your Administrator'.format(
                    invalid_collaborators[0].name,
                    self.env.ref('galicea_git.group_collaborator').full_name
                )
            )

    @api.model
    def create(self, values):
        values['state'] = 'created'
        ret = super(Repository, self).create(values)
        ret.__initialize_repo()
        return ret

    @api.multi
    def unlink(selfs):
        directories_to_move = selfs.mapped(lambda r: r.local_directory)
        ret = super(Repository, selfs).unlink()
        for directory in directories_to_move:
            if os.path.exists(directory):
                suffix = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
                new_directory = directory + '-deleted-' + suffix
                shutil.move(directory, new_directory)

    @api.multi
    def __initialize_repo(self):
        self.ensure_one()
        if os.path.exists(self.local_directory):
            raise ValidationError(
                'Repository {} already exists, choose a different name!'.format(self.system_name)
            )
        subprocess.check_call([which('git'), 'init', '--bare', self.local_directory])
