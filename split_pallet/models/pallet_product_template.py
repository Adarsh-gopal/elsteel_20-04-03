# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command
from odoo.tools import float_round, float_compare



class ProductTemplate(models.Model):
    _inherit = 'product.template'


    pallet_capacity = fields.Float(tracking=True,store=True)


class MrpProductionSplit(models.TransientModel):
    _inherit = 'mrp.production.split'


    is_pallet_capacity = fields.Boolean(default=False)


    @api.onchange('is_pallet_capacity')
    def _onchange_is_pallet(self):
        for rec in self:
            if rec.is_pallet_capacity == True:
                rec.counter = rec.product_id.product_tmpl_id.pallet_capacity
            else:
                rec.counter = False
                rec.production_detailed_vals_ids = False
        

    @api.model
    def _compute_details(self):
        for rec in self:
            res = super(MrpProductionSplit, self)._compute_details()
            if rec.is_pallet_capacity == True:
                for pallet in rec:
                    commands = [Command.clear()]
                    if pallet.product_id.product_tmpl_id.pallet_capacity < 1 or not pallet.production_id:
                        pallet.production_detailed_vals_ids = commands
                        continue
                    # quantity = float_round(pallet.product_qty / pallet.product_id.product_tmpl_id.pallet_capacity, precision_rounding=pallet.product_uom_id.rounding)
                    quantity = float_round(pallet.product_id.product_tmpl_id.pallet_capacity,precision_rounding=pallet.product_uom_id.rounding)
                    remaining_quantity = pallet.product_qty 

                    pallet_size = round(pallet.product_qty / pallet.product_id.product_tmpl_id.pallet_capacity)
            
                    for _ in range(pallet_size - 1):
                        commands.append(Command.create({
                            'quantity': quantity,
                            'user_id': pallet.production_id.user_id,
                            'date': pallet.production_id.date_planned_start,
                        }))
                        remaining_quantity = float_round(remaining_quantity - quantity, precision_rounding=pallet.product_uom_id.rounding)
                    commands.append(Command.create({
                        'quantity': remaining_quantity,
                        'user_id': pallet.production_id.user_id,
                        'date': pallet.production_id.date_planned_start,
                    }))
                    pallet.production_detailed_vals_ids = commands
            else:
                rec.production_detailed_vals_ids = rec.production_detailed_vals_ids

