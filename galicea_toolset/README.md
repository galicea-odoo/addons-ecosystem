Widgets
=======

    <field name="url_field" widget="iframe" style="width: 100%" iframe_style="width: 100%" />

Creates an iframe with ``url_field`` value as a source.

    <field name="article_ids" widget="one2many_flexible" click_target="current" />

Allows changing the target for the item click action.

Functions
=========
    odoo.addons.galicea_toolset.utils.get_base_url(env)

Client actions
==============
    @api.multi

    def button_action(self):

    return {

    'type': 'ir.actions.client',

    'tag': 'galicea_toolset.open_edit_dialog',

    'params': { 'res_id': <id>, 'res_model': <model>, 'title': <title>}

    };
