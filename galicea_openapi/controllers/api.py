# -*- coding: utf-8 -*-

import json

from fastapi.openapi.docs import get_swagger_ui_html

from odoo import http, _
from ..openapi import apiroute
from ..openapi import oapi





class OpenApiTest(http.Controller):


    @http.route(['/oapi/tst1',], type='http', auth="user", website=True)
    def tst1(self, **kw):
        return "tst1"

    @oapi.get('/oapi/tst2')
    @http.route(['/oapi/tst2',], type='http', auth="user", website=True)
    def tst2(self):
        return 'ok test2'

    @oapi.api_route('/oapi/tst3')
    @http.route(['/oapi/tst3',], type='http', auth="user", website=True)
    def tst3(self, par1="abc"):
        return par1


    @oapi.api_route('/oapi/tst4')
    @http.route(['/oapi/tst4', ], type='http', auth="user", website=True)
    def tst4(self,par1="444"):
        return par1


    @apiroute('/oapi/tst5')
    def tst5(self, par1="555"):
       return par1

    @http.route(['/oapi/api',], type='http', auth="user", website=True)
    def api(self, **kw):
        return json.dumps(oapi.openapi())
#        wynik możesz skopiować do https://editor.swagger.io/

    @http.route(['/oapi/docs',], type='http', auth="user", website=True)
    def api_UI(self, **kw):
        response = get_swagger_ui_html(openapi_url = '/oapi/api', title = 'tytuł')
        return response.body





