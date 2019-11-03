from odoo.addons.galicea_git.controllers.main import Main

class ExtMain(Main):
    def authorize(self, req):
        auth = req.httprequest.authorization
        if auth and auth.password == 'bearer':
            access_token = req.httprequest.authorization.username
            token = req.env['galicea_openid_connect.access_token'].sudo().search(
                [('token', '=', access_token)]
            )
            if token:
                req.uid = token.user_id.id
                return
        super(ExtMain, self).authorize(req)
