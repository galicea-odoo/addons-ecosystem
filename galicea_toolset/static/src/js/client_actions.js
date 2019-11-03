odoo.define('galicea_toolset.client_actions', function(require) {
  var Widget = require('web.Widget');
  var core = require('web.core');
  var common = require('web.form_common');
  var ActionManager = require('web.ActionManager');

  var OpenEditDialogAction = Widget.extend({
    init: function(parent, context) {
      this._super.apply(this, arguments);
      this.context = context;
      if (parent instanceof ActionManager) {
        this.am = parent;
      }
    },

    start: function () {
      var params = this.context.params;

      var popup = new common.FormViewDialog(self, {
        title: params.title,
        res_model: params.res_model,
        res_id: params.res_id,
      }).open();
      popup.on('closed', this, function() {
        this.am && this.am.history_back();
      });
    },
  });

  core.action_registry.add(
    'galicea_toolset.open_edit_dialog',
    OpenEditDialogAction
  );

  return {
    open_edit_dialog_action: OpenEditDialogAction,
  };
});
