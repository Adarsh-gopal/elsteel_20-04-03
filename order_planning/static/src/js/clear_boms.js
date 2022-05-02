odoo.define('order_planning.clear_bom', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var ListController = require('web.ListController');

    ListController.include({

        renderButtons: function($node) {

        this._super.apply(this, arguments);

            if (this.$buttons) {

                let clear_bom_button = this.$buttons.find('.oe_clear_bom_button');
                clear_bom_button && clear_bom_button.click(this.proxy('clear_bom_button')) ;

            }

        },

        clear_bom_button: function () {
            console.log('yay filter',this)
            var source_id = this.model.loadParams.context.active_id;
            rpc.query({
                  	model: 'planning.worksheet',
                    method: 'unlink_records',
                    args: [source_id],
                    });

        }

    });

});