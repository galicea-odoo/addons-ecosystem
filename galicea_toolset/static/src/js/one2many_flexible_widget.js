odoo.define('galicea_toolset.one2many_flexible_widget', function(require) {
  var core = require('web.core');
/*  
  var view_dialogs = require('web.view_dialogs'),
     relational_fields = require('web.relational_fields'),
     rpc = require('web.rpc'),
     field_registry = require('web.field_registry');*/
     
     var form_relational = require('web.form_relational');

/*     var X2ManyList = form_relational.X2ManyList;
     var ListView = require('web.ListView');
     var FieldOne2Many = field_registry.get('one2many');
     var FieldOne2Many = relational_fields.FieldOne2Many; 
  

     var FormController = require('web.FormController');
     */
   /*
     ListView.include({
       do_activate_record: function (index, id, dataset, view) {
           var action = this.ViewManager.action;
           if (!action || !action.context || !action.context.open_formview)
             return this._super(index, id, dataset, view);
           do_action(this, id, action.context);
       }
     });
   
   
var One2ManyListView = core.one2many_view_registry.get('list');
  */

  var One2ManyFlexibleListView = form_relational.One2ManyListView.extend({
    do_activate_record: function(index, id) {
      var self = this;
      if (!this.x2m.get("effective_readonly")) {
        this._super.apply(this, arguments);
        return;
      }

      this.do_action({
          'type': 'ir.actions.act_window',
          'views': [[false, 'form']],
          'res_model': self.x2m.field.relation,
          'res_id': id,
          'target': self.x2m.node.attrs.click_target || 'current',
      });
    }
  });

  var FieldOne2Many = core.form_widget_registry.get('one2many');

  var FieldOne2ManyFlexible = FieldOne2Many.extend({
    init: function() {
      this._super.apply(this, arguments);
      this.x2many_views = {
        kanban: core.view_registry.get('one2many_kanban'),
        list: One2ManyFlexibleListView,
      };
    },
  });

  core.form_widget_registry.add('one2many_flexible', FieldOne2ManyFlexible);

  return {
    FieldOne2ManyFlexible: FieldOne2ManyFlexible,
  };
});
