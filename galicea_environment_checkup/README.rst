About
=====

This add-on allows you to:

- programmatically check software dependencies required by your add-on, as well as inform the Administrator as to how to meet them,
- add custom verification for Odoo instance set-up and inform the Administrator about any inconsistencies.

Dependency checks
=================
.. image:: /galicea_environment_checkup/static/description/dependencies.png

How-to
------
Just add ``environment_checkup`` entry to ``__manifest__.py``

.. code::

  {
      ...
      'environment_checkup': {
          'dependencies': {
              'python': [
                  {
                      'name': 'Crypto',
                      'version': '>=2.6.2',
                      'install': "pip install 'PyCrypto>=2.6.1'"
                  },
              ],
              'external': [
                  {
                      'name': 'wkhtmltopdf',
                      'install': "apt install wkhtmltopdf"
                  },
                  {
                      'name': 'git',
                      'version': '^3.0.0',
                      'install': "apt install git"
                  }
              ],
              'internal': [
                  {
                      'name': 'web',
                      'version': '~10.0.1.0'
                  }
              ]
          }
      }
  }

Custom in-code checks
=====================
.. image:: /galicea_environment_checkup/static/description/custom.png

How-to
------

1. Add the check

``system_checks.py``

.. code::

  # -*- coding: utf-8 -*-

  import cgi
  from odoo.addons.galicea_environment_checkup import custom_check, CheckSuccess, CheckWarning, CheckFail

  @custom_check
  def check_mail(env):
      users_without_emails = env['res.users'].sudo().search([('email', '=', False)])

      if users_without_emails:
          raise CheckWarning(
              'Some users don\'t have their e-mails set up.',
              details='See user <tt>{}</tt>.'.format(cgi.escape(users_without_emails[0].name))
          )

      return CheckSuccess('All users have their e-mails set.')

2. Make sure it's loaded

``__init__.py``

.. code::

  # -*- coding: utf-8 -*-
  from . import system_checks
