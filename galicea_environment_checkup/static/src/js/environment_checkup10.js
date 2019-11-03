odoo.define('galicea_environment_checkup', function(require) {
  "use strict";

  var core = require('web.core');
  var form_common = require('web.form_common');
  var Widget = require('web.Widget');
  var session = require('web.session');
  var QWeb = core.qweb;
  var SystrayMenu = require('web.SystrayMenu');
  var Model = require('web.Model');

  var Users = new Model('res.users');

  var SystrayIcon =  Widget.extend({
    tagName: 'li',
    events: {
        "click": "on_click",
    },

    start: function(){
      this.load(this.all_dashboards);
      return this._super();
    },

    load: function(dashboards){
      var self = this;
      var loading_done = new $.Deferred();
      Users.call('has_group', ['base.group_erp_manager']).then(function(is_admin) {
        if (is_admin) {
          session.rpc('/galicea_environment_checkup/data', {})
            .then(function (data) {
              var counts = { 'success': 0, 'warning': 0, 'fail': 0 };
              data.forEach(function (check) { ++counts[check.result]; });

              var result;
              if (counts['fail']) {
                result = 'fail';
              } else if (counts['warning']) {
                result = 'warning';
              } else {
                result = 'success';
              }

              self.replaceElement(QWeb.render('GaliceaEnvironmentCheckupIcon', {
                'result': result,
                'count': counts['warning'] + counts['fail']
              }));
              loading_done.resolve();
            });
        } else {
          loading_done.resolve();
        }
      });

      return loading_done;
    },

    on_click: function (event) {
      event.preventDefault();
      this.do_action('galicea_environment_checkup.dashboard_action', {clear_breadcrumbs: true});
    },
  });

  SystrayMenu.Items.push(SystrayIcon);

  var Dashboard = Widget.extend({
    start: function(){
      return this.load(this.all_dashboards);
    },

    load: function(dashboards) {
      var self = this;
      var loading_done = new $.Deferred();
      session.rpc('/galicea_environment_checkup/data', {})
        .then(function (data) {
          self.replaceElement(QWeb.render('GaliceaEnvironmentCheckupDashboard', {'data': data}));
          loading_done.resolve();
        });
      return loading_done;
    },
  });

  core.action_registry.add('galicea_environment_checkup.dashboard', Dashboard);

  var FormWidget = form_common.AbstractField.extend({
    init: function() {
      this._super.apply(this, arguments);
      this.set("value", "[]");
    },

    render_value: function() {
      var data = JSON.parse(this.get('value'));
      if (data.length == 0) {
        this.replaceElement('<div />');
        return;
      }
      this.replaceElement(QWeb.render('GaliceaEnvironmentCheckupFormWidget', {'data': data}));
    },
  });

  core.form_widget_registry.add('environment_checks', FormWidget);

  return {
    SystrayIcon: SystrayIcon,
    Dashboard: Dashboard,
    FormWidget: FormWidget
  };
});
