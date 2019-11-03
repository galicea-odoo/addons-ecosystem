# -*- coding: utf-8 -*-

import json
import logging
from functools import wraps

from odoo import http
import werkzeug

_logger = logging.getLogger(__name__)

class ApiException(Exception):
    INVALID_REQUEST = 'invalid_request'

    def __init__(self, message, code=None):
        super(Exception, self).__init__(message)
        self.code = code if code else self.INVALID_REQUEST

def resource(path, method, auth='user'):
    assert auth in ['user', 'client']

    def endpoint_decorator(func):
        @http.route(path, auth='public', type='http', methods=[method, 'OPTIONS'], csrf=False)
        @wraps(func)
        def func_wrapper(self, req, **query):
            cors_headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, X-Debug-Mode, Authorization',
                'Access-Control-Max-Age': 60 * 60 * 24,
            }
            if req.httprequest.method == 'OPTIONS':
                return http.Response(
                    status=200,
                    headers=cors_headers
                )

            try:
                access_token = None
                if 'Authorization' in req.httprequest.headers:
                    authorization_header = req.httprequest.headers['Authorization']
                    if authorization_header[:7] == 'Bearer ':
                        access_token = authorization_header.split(' ', 1)[1]
                if access_token is None:
                    access_token = query.get('access_token')
                if not access_token:
                    raise ApiException(
                        'access_token param is missing',
                        'invalid_request',
                    )
                if auth == 'user':
                    token = req.env['galicea_openid_connect.access_token'].sudo().search(
                        [('token', '=', access_token)]
                    )
                    if not token:
                        raise ApiException(
                            'access_token is invalid',
                            'invalid_request',
                        )
                    req.uid = token.user_id.id
                elif auth == 'client':
                    token = req.env['galicea_openid_connect.client_access_token'].sudo().search(
                        [('token', '=', access_token)]
                    )
                    if not token:
                        raise ApiException(
                            'access_token is invalid',
                            'invalid_request',
                        )
                    req.uid = token.client_id.system_user_id.id

                ctx = req.context.copy()
                ctx.update({'client_id': token.client_id.id})
                req.context = ctx

                response = func(self, req, **query)
                return werkzeug.Response(
                    response=json.dumps(response),
                    headers=cors_headers,
                    status=200
                )
            except ApiException as e:
                error_message = "error: {0}".format(e)
                return werkzeug.Response(
                    response=json.dumps({'error': e.code, 'error_message': error_message}),
                    status=400,
                    headers=cors_headers
                )
            except:
                _logger.exception('Unexpected exception while processing API request')
                return werkzeug.Response(
                    response=json.dumps({
                        'error': 'server_error',
                        'error_message': 'Unexpected server error',
                    }),
                    headers=cors_headers,
                    status=500
                )

        return func_wrapper
    return endpoint_decorator
