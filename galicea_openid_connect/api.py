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

    def to_json(self):
        return {
            'error': self.code,
            'error_message': self.message
        }

def resource(path, method, auth='user', clients=None):
    assert auth in ['user', 'client']

    def endpoint_decorator(func):
        @http.route(path, auth='public', type='http', methods=[method, 'OPTIONS'], csrf=False)
        @wraps(func)
        def func_wrapper(self, req, **query):
            cors_headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, X-Debug-Mode, Authorization',
                'Access-Control-Max-Age': 60 * 60 * 24,
                'Access-Control-Allow-Methods': 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
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

                if clients:
                    if token.client_id.id not in map(lambda c: req.env.ref(c).id, clients):
                        raise ApiException('Access denied', 'restricted_app')

                ctx = req.context.copy()
                ctx.update({'client_id': token.client_id.id})
                req.context = ctx

                response = func(self, req, **query)
                return werkzeug.Response(
                    response=json.dumps(response),
                    headers=cors_headers,
                    status=200
                )
            except Exception as e:
                status = 400
                if not isinstance(e, ApiException):
                    _logger.exception('Unexpected exception while processing API request')
                    e = ApiException('Unexpected server error', 'server_error')
                    status = 500
                return werkzeug.Response(
                    response=json.dumps(e.to_json()),
                    status=status,
                    headers=cors_headers
                )

        return func_wrapper
    return endpoint_decorator
