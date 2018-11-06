# -*- coding: utf-8 -*-
{
    'name': "Galicea Enviromnent Check-up",

    'summary': """
        Programmatically validate environment, including internal and external
        dependencies""",

    'author': "Maciej Wawro",
    'maintainer': "Galicea",
    'website': "http://galicea.pl",

    'category': 'Technical Settings',
    'version': '10.0.1.0',

    'depends': ['web'],

    'data': [
        'views/data.xml',
        'views/views.xml',
        'views/environment_checks.xml'
    ],

    'qweb': ['static/src/xml/templates.xml'],

    'installable': True
}
