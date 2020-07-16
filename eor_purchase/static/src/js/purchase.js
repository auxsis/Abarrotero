odoo.define('eor_purchase.taxes', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var QWeb = core.qweb;
var field_utils = require('web.field_utils');

var TaxesWidget = AbstractField.extend({
    isSet: function(){
        return true;
    },
    _render: function(){
        var self = this;
        var inf = JSON.parse(this.value);
        if (!inf){
            this.$el.html('');
            return;
        }
        _.each(inf.content, function(k, v){

            k.index = v;
            k.amount_tax = field_utils.format.float(k.amount_tax, {digits: k.digits});
            //<k.amount_tax = k.amount_tax.replace('.', ',');
        });

        this.$el.html(QWeb.render('TaxesWidget', {
            line: inf.content,
            title: inf.title
        }))
    }
})

field_registry.add('taxes', TaxesWidget);

return {
    TaxesWidget: TaxesWidget
}
});
