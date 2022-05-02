# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import datetime
import math
import re

from ast import literal_eval
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES





class BulkProduction(models.Model):
    _inherit = 'product.template'

    is_bulk_production = fields.Boolean(string="Is a Bulk Production",default=False)




class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    def action_merge(self):
        self._pre_action_split_merge_hook(merge=True)
        products = set([(production.product_id, production.bom_id) for production in self])
        product_id, bom_id = products.pop()
        users = set([production.user_id for production in self])
        if len(users) == 1:
            user_id = users.pop()
        else:
            user_id = self.env.user

        origs = self._prepare_merge_orig_links()
        dests = {}
        for move in self.move_finished_ids:
            dests.setdefault(move.byproduct_id.id, []).extend(move.move_dest_ids.ids)

        
        saleorder = set([production.so_origin for production in self])
        if len(saleorder) == 2:
            so_origin = list(saleorder)[1]
        else:
            so_origin = saleorder.pop()
        
        
        
        productcolour = set([production.product_colour for production in self])
        if len(productcolour) == 2:
            product_colour = list(productcolour)[1]
        else:
            product_colour = productcolour.pop()
        
 
        production = self.env['mrp.production'].create({
            'product_id': product_id.id,
            'bom_id': bom_id.id,
            'picking_type_id': bom_id.picking_type_id or self._get_default_picking_type(),
            'product_qty': sum(production.product_uom_qty for production in self),
            'product_uom_id': product_id.uom_id.id,
            'user_id': user_id.id,
            'origin': ",".join(sorted([production.name for production in self])),
            'so_origin' : so_origin,
            'product_colour' : product_colour,
        })
        production.so_origin = so_origin
        production.product_colour = product_colour
        self.env['stock.move'].create(production._get_moves_raw_values())
        self.env['stock.move'].create(production._get_moves_finished_values())
        production._create_workorder()

        for move in production.move_raw_ids:
            for field, vals in origs[move.bom_line_id.id].items():
                move[field] = vals
        for move in production.move_finished_ids:
            move.move_dest_ids = [Command.set(dests[move.byproduct_id.id])]

        self.move_dest_ids.created_production_id = production.id

        self.procurement_group_id.stock_move_ids.group_id = production.procurement_group_id

        if 'confirmed' in self.mapped('state'):
            production.move_raw_ids._adjust_procure_method()
            (production.move_raw_ids | production.move_finished_ids).write({'state': 'confirmed'})
            production.workorder_ids._action_confirm()
            production.state = 'confirmed'

        self.with_context(skip_activity=True)._action_cancel()
        for p in self:
            p._message_log(body=_('This production has been merge in %s', production.display_name))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'res_id': production.id,
            'target': 'main',
        }



    def _pre_action_split_merge_hook(self, merge=False, split=False):
        if not merge and not split:
            return True
        ope_str = merge and 'merge' or 'split'
        if any(production.state not in ('draft', 'confirmed') for production in self):
            raise UserError(_("Only manufacturing orders in either a draft or confirmed state can be %s.", ope_str))
        if any(not production.bom_id for production in self):
            raise UserError(_("Only manufacturing orders with a Bill of Materials can be %s.", ope_str))
        if split:
            return True

        if len(self) < 2:
            raise UserError(_("You need at least two production orders to merge them."))
        products = set([(production.product_id, production.bom_id) for production in self])
        if len(products) > 1:
            raise UserError(_('You can only merge manufacturing orders of identical products with same BoM.'))
        
        saleorder = set([(production.product_id, production.so_origin) for production in self])
        if len(saleorder) > 1:
            raise UserError(_('You can only merge manufacturing orders of identical products with same Sale Order.'))

        bulk_products = self.filtered(lambda pro : pro.product_id.product_tmpl_id.is_bulk_production == False)
        if bulk_products:
            raise UserError(_('You can only merge manufacturing orders of bulk products'))


        additional_raw_ids = self.mapped("move_raw_ids").filtered(lambda move: not move.bom_line_id)
        additional_byproduct_ids = self.mapped('move_byproduct_ids').filtered(lambda move: not move.byproduct_id)
        if additional_raw_ids or additional_byproduct_ids:
            raise UserError(_("You can only merge manufacturing orders with no additional components or by-products."))
        if len(set(self.mapped('state'))) > 1:
            raise UserError(_("You can only merge manufacturing with the same state."))
        if len(set(self.mapped('picking_type_id'))) > 1:
            raise UserError(_('You can only merge manufacturing with the same operation type'))
        # TODO explode and check no quantity has been edited
        return True

    def _prepare_merge_orig_links(self):
        origs = defaultdict(dict)
        for move in self.move_raw_ids:
            if not move.move_orig_ids:
                continue
            origs[move.bom_line_id.id].setdefault('move_orig_ids', set()).update(move.move_orig_ids.ids)
        for vals in origs.values():
            if not vals.get('move_orig_ids'):
                continue
            vals['move_orig_ids'] = [Command.set(vals['move_orig_ids'])]
        return origs
