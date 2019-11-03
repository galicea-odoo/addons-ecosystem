# -*- coding: utf-8 -*-
{
    'name': "Galicea Environment Check-up",

    'summary': """
        Programmatically validate environment, including internal and external
        dependencies""",

    'author': "Maciej Wawro",
    'maintainer': "Galicea",
    'website': "http://galicea.pl",

    'category': 'Technical Settings',
    'version': '12.0.1.0',

    'depends': ['web','galicea_base',],

    'data': [
        'views/data.xml',
        'views/views.xml',
        'views/environment_checks.xml'
    ],

    'qweb': ['static/src/xml/templates.xml'],

    'images': [
        'static/description/images/custom_screenshot.png',
        'static/description/images/dependencies_screenshot.png'
    ],

    'installable': True
}
