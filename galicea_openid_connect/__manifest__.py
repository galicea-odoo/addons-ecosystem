# -*- coding: utf-8 -*-
{
    'name': "Galicea OpenID Connect Provider",

    'summary': """OpenID Connect Provider and OAuth2 resource server""",

    'author': "Maciej Wawro",
    'maintainer': "Galicea",
    'website': "http://galicea.pl",

    'category': 'Technical Settings',
    'version': '12.0.0.0',

    'depends': ['web', 'galicea_environment_checkup', 'galicea_base' ],

    'external_dependencies': {
        'python': ['jwcrypto', 'cryptography']
    },

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
#        'security/init.yml',
        'security/init.xml',
        'views/views.xml',
        'views/templates.xml'
    ],

    'environment_checkup': {
        'dependencies': {
            'python': [
                {
                    'name': 'jwcrypto',
                    'install': "pip install 'jwcrypto==0.5.0'"
                },
                {
                    'name': 'cryptography',
                    'version': '>=2.3',
                    'install': "pip install 'cryptography>=2.3'"
                }
            ]
        }
    },

    'images': [
        'static/description/images/master_screenshot.png',
        'static/description/images/client_screenshot.png',
        'static/description/images/login_screenshot.png',
        'static/description/images/error_screenshot.png'
    ]
}
