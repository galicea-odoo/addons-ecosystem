# -*- coding: utf-8 -*-
{
    'name': "Galicea Git hosting",

    'summary': """Git repository hosting and per-user access checking""",

    'author': "Maciej Wawro",
    'maintainer': "Galicea",
    'website': "http://galicea.pl",

    'category': 'Technical Settings',
    'version': '12.0.0.1',

    'depends': ['web', 'galicea_environment_checkup'],

    'external_dependencies': {
        'bin': ['git']
    },

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/config.xml',
        'views/views.xml',
    ],

    'images': [
        'static/description/images/create_screenshot.png',
        'static/description/images/config_screenshot.png',
        'static/description/images/console_screenshot.png',
    ],

    'application': True,
    'installable': True,

    'environment_checkup': {
        'dependencies': {
            'external': [
                {
                    'name': 'git',
                    'version': '>=2.1.4',
                    'install': "apt install git"
                }
            ]
        }
    }
}
