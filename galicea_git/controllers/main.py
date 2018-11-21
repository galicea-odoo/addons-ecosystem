# -*- coding: utf-8 -*-

import subprocess, os, io

from odoo import http
from odoo.tools import config
import werkzeug

from ..http_chunked_fix import http_input_stream

class Main(http.Controller):
    @http.route(
        [
            '/git/<repo>',
            '/git/<repo>/<path:path>',
        ],
        auth='public',
        csrf=False
    )
    def git(self, request, repo, **kw):
        auth = request.httprequest.authorization
        if auth:
            request.session.authenticate(request.session.db, auth.username, auth.password)
        if not request.env.uid or request.env.user.login == 'public':
            return werkzeug.Response(
                headers=[('WWW-Authenticate', 'Basic')],
                status=401
            )

        try:
            repository = request.env['galicea_git.repository'].search(
                [('system_name', '=', repo)]
            )
        except AccessError:
            return werkzeug.Response(
                status=403
            )
        if not repository.exists():
            return werkzeug.Response(
                status=404
            )

        http_environment = request.httprequest.environ
        git_env = {
            'REQUEST_METHOD': http_environment['REQUEST_METHOD'],
            'QUERY_STRING': http_environment['QUERY_STRING'],
            'CONTENT_TYPE': request.httprequest.headers.get('Content-Type'),
            'REMOTE_ADDR': http_environment['REMOTE_ADDR'],
            'GIT_PROJECT_ROOT': os.path.join(config['data_dir'], 'git'),
            'GIT_HTTP_EXPORT_ALL': '1',
            'PATH_INFO': http_environment['PATH_INFO'][4:],
            'REMOTE_USER': request.env.user.login
        }

        command_env = os.environ.copy()
        for var in git_env:
            command_env[var] = git_env[var]

        git = subprocess.Popen(
            ['/usr/lib/git-core/git-http-backend'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=command_env,
            shell=True
        )
        stdout, stderr = git.communicate(http_input_stream(request).read())
        headers_str, body = stdout.split("\r\n\r\n", 2)

        http_status_code = 200
        headers = []
        for header in headers_str.split("\r\n"):
            name, value = header.split(': ', 2)
            if name == 'Status':
                http_code = int(value.split(' ')[0])
            else:
                headers.append((name, value))

        return werkzeug.Response(
            body,
            status = http_status_code,
            headers = headers
        )
