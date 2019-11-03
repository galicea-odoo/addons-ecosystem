# -*- coding: utf-8 -*-
{
    'name': "openapi",

    'summary': """
        Odoo Opnapi
        UWAGA! Obecnie dekorator apiroute ma ograniczoną funkcjonalność.
        M.in. tylko jeden URL
        controllers/api.py zawiera przykład wykorzystania -
        pod adresem /oapi/api zwraca dokumentację w JSON 
        """,

    'description': """
        
        """,

    'author': 'Jerzy Wawro',
    'maintainer': "Galicea",
    'website': "http://www.galicea.pl",
    'category': 'Tools',
    'version': '12.0.0.1',

    'depends': [
    ],
    'external_dependencies': {
      'python': [ 'fastapi', 'pydantic', 'starlette' ]
    },
    'data': [
    ],
    'application': True,
    'installable': True,
    
}
