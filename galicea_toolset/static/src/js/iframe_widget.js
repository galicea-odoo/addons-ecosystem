odoo.define('pwste_epub.iframe_widget', function(require) {

  var AbstractField = require('web.AbstractField');
  var fieldRegistry = require('web.field_registry');



  var core = require('web.core');
  var Widget= require('web.Widget');
  var widgetRegistry = require('web.widget_registry');
  var FieldManagerMixin = require('web.FieldManagerMixin');

  var IFrameWidget = AbstractField.extend({

     init: function () {
        this._super.apply(this, arguments);
//        this.set("value", "");
    },

    _renderReadonly: function() {
      window.widget=this;
      this.$el.html(
        $('<iframe>', {
          src:  this.value || 'about:blank',
          style: this.attrs.iframe_style
        })
      );
      if (this.attrs.new_window_label && this.value) {
        this.$el.prepend(
          $('<a>', {
            href: this.value,
            target: '_blank',
            style: 'float:right; margin-bottom: 10px',
            'class': 'btn btn-primary',
          }).html('<i class="fa fa-external-link-square" aria-hidden="true"></i> Otwórz w nowym oknie')
        )
      } 
    },
  });

  fieldRegistry.add(
    'iframe', IFrameWidget
  );

  return {
    IFrameWidget: IFrameWidget,
  };

});
