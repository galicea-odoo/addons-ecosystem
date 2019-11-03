# -*- coding: utf-8 -*-

import json
import time
import os
import base64

from odoo import http
import werkzeug

from .. api import resource

try:
    from jwcrypto import jwk, jwt
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
except ImportError:
    pass

def jwk_from_json(json_key):
    key = jwk.JWK()
    key.import_key(**json.loads(json_key))
    return key

def jwt_encode(claims, key):
    token = jwt.JWT(
        header={'alg': key._params['alg'], 'kid': key._params['kid']},
        claims=claims
    )
    token.make_signed_token(key)
    return token.serialize()

def jwt_decode(serialized, key):
    token = jwt.JWT(jwt=serialized, key=key)
    return json.loads(token.claims)

RESPONSE_TYPES_SUPPORTED = [
    'code',
    'token',
    'id_token token',
    'id_token'
]

class OAuthException(Exception):
    INVALID_REQUEST = 'invalid_request'
    INVALID_CLIENT = 'invalid_client'
    UNSUPPORTED_RESPONSE_TYPE = 'unsupported_response_type'
    INVALID_GRANT = 'invalid_grant'
    UNSUPPORTED_GRANT_TYPE = 'unsupported_grant_type'

    def __init__(self, message, type):
        super(Exception, self).__init__(message)
        self.type = type

class Main(http.Controller):
    def __get_authorization_code_jwk(self, req):
        return jwk_from_json(req.env['ir.config_parameter'].sudo().get_param(
            'galicea_openid_connect.authorization_code_jwk'
        ))

    def __get_id_token_jwk(self, req):
        return jwk_from_json(req.env['ir.config_parameter'].sudo().get_param(
            'galicea_openid_connect.id_token_jwk'
        ))

    def __validate_client(self, req, **query):
        if 'client_id' not in query:
            raise OAuthException(
                'client_id param is missing',
                OAuthException.INVALID_CLIENT,
            )
        client_id = query['client_id']
        client = req.env['galicea_openid_connect.client'].sudo().search(
            [('client_id', '=', client_id)]
        )
        if not client:
            raise OAuthException(
                'client_id param is invalid',
                OAuthException.INVALID_CLIENT,
            )
        return client

    def __validate_redirect_uri(self, client, req, **query):
        if 'redirect_uri' not in query:
            raise OAuthException(
                'redirect_uri param is missing',
                OAuthException.INVALID_GRANT,
            )

        redirect_uri = query['redirect_uri']
        if client.auth_redirect_uri != redirect_uri:
            raise OAuthException(
                'redirect_uri param doesn\'t match the pre-configured redirect URI',
                OAuthException.INVALID_GRANT,
            )

        return redirect_uri

    def __validate_client_secret(self, client, req, **query):
        if 'client_secret' not in query or query['client_secret'] != client.secret:
            raise OAuthException(
                'client_secret param is not valid',
                OAuthException.INVALID_CLIENT,
            )

    @http.route('/.well-known/openid-configuration', auth='public', type='http')
    def metadata(self, req, **query):
        base_url = http.request.httprequest.host_url
        data = {
            'issuer': base_url,
            'authorization_endpoint': base_url + 'oauth/authorize',
            'token_endpoint': base_url + 'oauth/token',
            'userinfo_endpoint': base_url + 'oauth/userinfo',
            'jwks_uri': base_url + 'oauth/jwks',
            'scopes_supported': ['openid'],
            'response_types_supported': RESPONSE_TYPES_SUPPORTED,
            'grant_types_supported': ['authorization_code', 'implicit', 'password', 'client_credentials'],
            'subject_types_supported': ['public'],
            'id_token_signing_alg_values_supported': ['RS256'],
            'token_endpoint_auth_methods_supported': ['client_secret_post']
        }
        return json.dumps(data)

    @http.route('/oauth/jwks', auth='public', type='http')
    def jwks(self, req, **query):
        keyset = jwk.JWKSet()
        keyset.add(self.__get_id_token_jwk(req))
        return keyset.export(private_keys=False)

    @resource('/oauth/userinfo', method='GET')
    def userinfo(self, req, **query):
        user = req.env.user
        values = {
            'sub': str(user.id),
            # Needed in case the client is another Odoo instance
            'user_id': str(user.id),
            'name': user.name,
        }
        if user.email:
            values['email'] = user.email
        return values

    @resource('/oauth/clientinfo', method='GET', auth='client')
    def clientinfo(self, req, **query):
        client = req.env['galicea_openid_connect.client'].browse(req.context['client_id'])
        return {
            'name': client.name
        }

    @http.route('/oauth/authorize', auth='public', type='http', csrf=False)
    def authorize(self, req, **query):
        # First, validate client_id and redirect_uri params.
        try:
            client = self.__validate_client(req, **query)
            redirect_uri = self.__validate_redirect_uri(client, req, **query)
        except OAuthException as e:
            # If those are not valid, we must not redirect back to the client
            # - instead, we display a message to the user
            return req.render('galicea_openid_connect.error', {'exception': e})

        scopes = query['scope'].split(' ') if query.get('scope') else []
        is_openid_request = 'openid' in scopes

        # state, if present, is just mirrored back to the client
        response_params = {}
        if 'state' in query:
            response_params['state'] = query['state']

        response_mode = query.get('response_mode')
        try:
            if response_mode and response_mode not in ['query', 'fragment']:
                response_mode = None
                raise OAuthException(
                    'The only supported response_modes are \'query\' and \'fragment\'',
                    OAuthException.INVALID_REQUEST
                )

            if 'response_type' not in query:
                raise OAuthException(
                    'response_type param is missing',
                    OAuthException.INVALID_REQUEST,
                )
            response_type = query['response_type']
            if response_type not in RESPONSE_TYPES_SUPPORTED:
                raise OAuthException(
                    'The only supported response_types are: {}'.format(', '.join(RESPONSE_TYPES_SUPPORTED)),
                    OAuthException.UNSUPPORTED_RESPONSE_TYPE,
                )
        except OAuthException as e:
            response_params['error'] = e.type
            response_params['error_description'] = e.message
            return self.__redirect(redirect_uri, response_params, response_mode or 'query')

        if not response_mode:
            response_mode = 'query' if response_type == 'code' else 'fragment'

        user = req.env.user
        # In case user is not logged in, we redirect to the login page and come back
        needs_login = user.login == 'public'
        # Also if they didn't authenticate recently enough
        if 'max_age' in query and http.request.session.get('auth_time', 0) + int(query['max_age']) < time.time():
            needs_login = True
        if needs_login:
            params = {
              'force_auth_and_redirect': '/oauth/authorize?{}'.format(werkzeug.url_encode(query))
            }
            return self.__redirect('/web/login', params, 'query')

        response_types = response_type.split()

        extra_claims = {
            'sid': http.request.httprequest.session.sid,
        }
        if 'nonce' in query:
            extra_claims['nonce'] = query['nonce']

        if 'code' in response_types:
            # Generate code that can be used by the client server to retrieve
            # the token. It's set to be valid for 60 seconds only.
            # TODO: The spec says the code should be single-use. We're not enforcing
            # that here.
            payload = {
                'redirect_uri': redirect_uri,
                'client_id': client.client_id,
                'user_id': user.id,
                'scopes': scopes,
                'exp': int(time.time()) + 60
            }
            payload.update(extra_claims)
            key = self.__get_authorization_code_jwk(req)
            response_params['code'] = jwt_encode(payload, key)
        if 'token' in response_types:
            access_token = req.env['galicea_openid_connect.access_token'].sudo().retrieve_or_create(
                user.id,
                client.id
            ).token
            response_params['access_token'] = access_token
            response_params['token_type'] = 'bearer'

            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(access_token.encode('ascii'))
            at_hash = digest.finalize()
            extra_claims['at_hash'] = base64.urlsafe_b64encode(at_hash[:16]).strip('=')
        if 'id_token' in response_types:
            response_params['id_token'] = self.__create_id_token(req, user.id, client, extra_claims)

        return self.__redirect(redirect_uri, response_params, response_mode)

    @http.route('/oauth/token', auth='public', type='http', methods=['POST', 'OPTIONS'], csrf=False)
    def token(self, req, **query):
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
            if 'grant_type' not in query:
                raise OAuthException(
                    'grant_type param is missing',
                    OAuthException.INVALID_REQUEST,
                )
            if query['grant_type'] == 'authorization_code':
                return json.dumps(self.__handle_grant_type_authorization_code(req, **query))
            elif query['grant_type'] == 'client_credentials':
                return json.dumps(self.__handle_grant_type_client_credentials(req, **query))
            elif query['grant_type'] == 'password':
                return werkzeug.Response(
                    response=json.dumps(self.__handle_grant_type_password(req, **query)),
                    headers=cors_headers
                )
            else:
                raise OAuthException(
                    'Unsupported grant_type param: \'{}\''.format(query['grant_type']),
                    OAuthException.UNSUPPORTED_GRANT_TYPE,
                )
        except OAuthException as e:
            body = json.dumps({'error': e.type, 'error_description': e.message})
            return werkzeug.Response(response=body, status=400, headers=cors_headers)

    def __handle_grant_type_authorization_code(self, req, **query):
        client = self.__validate_client(req, **query)
        redirect_uri = self.__validate_redirect_uri(client, req, **query)
        self.__validate_client_secret(client, req, **query)

        if 'code' not in query:
            raise OAuthException(
                'code param is missing',
                OAuthException.INVALID_GRANT,
            )
        try:
            payload = jwt_decode(query['code'], self.__get_authorization_code_jwk(req))
        except jwt.JWTExpired:
            raise OAuthException(
                'Code expired',
                OAuthException.INVALID_GRANT,
            )
        except ValueError:
            raise OAuthException(
                'code malformed',
                OAuthException.INVALID_GRANT,
            )
        if payload['client_id'] != client.client_id:
            raise OAuthException(
                'client_id doesn\'t match the authorization request',
                OAuthException.INVALID_GRANT,
            )
        if payload['redirect_uri'] != redirect_uri:
            raise OAuthException(
                'redirect_uri doesn\'t match the authorization request',
                OAuthException.INVALID_GRANT,
            )

        # Retrieve/generate access token. We currently only store one per user/client
        token = req.env['galicea_openid_connect.access_token'].sudo().retrieve_or_create(
            payload['user_id'],
            client.id
        )
        response = {
            'access_token': token.token,
            'token_type': 'bearer'
        }
        if 'openid' in payload['scopes']:
            extra_claims = { name: payload[name] for name in payload if name in ['sid', 'nonce'] }
            response['id_token'] = self.__create_id_token(req, payload['user_id'], client, extra_claims)
        return response

    def __handle_grant_type_password(self, req, **query):
        client = self.__validate_client(req, **query)
        if not client.allow_password_grant:
            raise OAuthException(
                'This client is not allowed to perform password flow',
                OAuthException.UNSUPPORTED_GRANT_TYPE
            )

        for param in ['username', 'password']:
            if param not in query:
                raise OAuthException(
                    '{} is required'.format(param),
                    OAuthException.INVALID_REQUEST
                )
        user_id = req.env['res.users'].authenticate(
            req.env.cr.dbname,
            query['username'],
            query['password'],
            None
        )
        if not user_id:
            raise OAuthException(
                'Invalid username or password',
                OAuthException.INVALID_REQUEST
            )

        scopes = query['scope'].split(' ') if query.get('scope') else []
        # Retrieve/generate access token. We currently only store one per user/client
        token = req.env['galicea_openid_connect.access_token'].sudo().retrieve_or_create(
            user_id,
            client.id
        )
        response = {
            'access_token': token.token,
            'token_type': 'bearer'
        }
        if 'openid' in scopes:
            response['id_token'] = self.__create_id_token(req, user_id, client, {})
        return response

    def __handle_grant_type_client_credentials(self, req, **query):
        client = self.__validate_client(req, **query)
        self.__validate_client_secret(client, req, **query)
        token = req.env['galicea_openid_connect.client_access_token'].sudo().retrieve_or_create(client.id)
        return {
            'access_token': token.token,
            'token_type': 'bearer'
        }

    def __create_id_token(self, req, user_id, client, extra_claims):
        claims = {
            'iss': http.request.httprequest.host_url,
            'sub': str(user_id),
            'aud': client.client_id,
            'iat': int(time.time()),
            'exp': int(time.time()) + 15 * 60
        }
        auth_time = extra_claims.get('sid') and http.root.session_store.get(extra_claims['sid']).get('auth_time')
        if auth_time:
            claims['auth_time'] = auth_time
        if 'nonce' in extra_claims:
            claims['nonce'] = extra_claims['nonce']
        if 'at_hash' in extra_claims:
            claims['at_hash'] = extra_claims['at_hash']

        key = self.__get_id_token_jwk(req)
        return jwt_encode(claims, key)

    def __redirect(self, url, params, response_mode):
        location = '{}{}{}'.format(
            url,
            '?' if response_mode == 'query' else '#',
            werkzeug.url_encode(params)
        )
        return werkzeug.Response(
            headers={'Location': location},
            response=None,
            status=302,
        )
