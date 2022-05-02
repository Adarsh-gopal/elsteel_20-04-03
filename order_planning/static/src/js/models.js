odoo.define('order_planning.JsToCallWizard', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var ListController = require('web.ListController');

    ListController.include({

        renderButtons: function($node) {

        this._super.apply(this, arguments);

            if (this.$buttons) {

                let filter_button = this.$buttons.find('.oe_filter_button');
                filter_button && filter_button.click(this.proxy('filter_button')) ;

            }

        },

        filter_button: function () {
            console.log('yay filter',this)
            var source_id = this.model.loadParams.context.active_id;
            rpc.query({
                  	model: 'planning.worksheet',
                    method: 'generate_all_bom',
                    args: [source_id],
                    });

        }

    });

});