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


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        procurement_groups = self.env['procurement.group'].search([('sale_id', 'in', self.ids)])
        mrp_production_ids = set(procurement_groups.stock_move_ids.created_production_id.ids) | set(procurement_groups.mrp_production_ids.ids)
        for parent in mrp_production_ids:
            parent = self.env['mrp.production'].search([('id','=',parent)])
            parent.split_sequence = 1
            for order in parent:
                child_lst = []
                new_child_lst = []
                for rec in order:
                    child_lst+= rec.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids
                    for ch in child_lst:
                        new_child_lst += self.env['mrp.production'].search([('id','=',ch)]).procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids
                        [child_lst.append(x) for x in new_child_lst if x not in child_lst]
                child_lst.append(order.id)            
                child_lst.sort(reverse=False)

                mo_list = []
                for line in child_lst:
                    mo_id = self.env['mrp.production'].search([('id','=',line)])
                    if mo_id:
                        mo_list.append(mo_id)
            value = 1
            for child_mo in mo_list:
                if child_mo != parent:
                    value += 1
                    child_mo.split_sequence = round(value,2)
        return res

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    split_sequence = fields.Float()
    


    # def action_view_mrp_production_childs(self):
    #     self.ensure_one()
    #     mrp_production_ids = self.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids
    #     action = {
    #         'res_model': 'mrp.production',
    #         'type': 'ir.actions.act_window',
    #     }
    #     if len(mrp_production_ids) == 1:
    #         action.update({
    #             'view_mode': 'form',
    #             'res_id': mrp_production_ids[0],
    #         })
    #     else:
    #         action.update({
    #             'name': _("%s Child MO's") % self.name,
    #             'domain': [('id', 'in', mrp_production_ids),('id','!=',self.id)],
    #             'view_mode': 'tree,form',
    #         })
    #     return action

    # def action_view_mrp_production_backorders(self):
    #     backorder_ids = self.procurement_group_id.mrp_production_ids.ids
    #     return {
    #         'res_model': 'mrp.production',
    #         'type': 'ir.actions.act_window',
    #         'name': _("Backorder MO's"),
    #         'domain': [('id', 'in', backorder_ids),('id','!=',self.id)],
    #         'view_mode': 'tree,form',
    #     }

    # @api.model
    # def create(self,vals):
    #     res = super(MrpProduction,self).create(vals)
    #     parent_sale = self.env['sale.order'].search([('name','=',res.origin)])
    #     if parent_sale:
    #         res.split_sequence = 1
    #     if res.split_sequence == 0:
    #         parent_mo = self.env['mrp.production'].search([('name','=',res.origin)])

    #     return res

    # def _split_productions(self, amounts=False, cancel_remaning_qty=False, set_consumed_qty=False):
    #     """ Splits productions into productions smaller quantities to produce, i.e. creates
    #     its backorders.
    #     :param dict amounts: a dict with a production as key and a list value containing
    #     the amounts each production split should produce including the original production,
    #     e.g. {mrp.production(1,): [3, 2]} will result in mrp.production(1,) having a product_qty=3
    #     and a new backorder with product_qty=2.
    #     :return: mrp.production records in order of [orig_prod_1, backorder_prod_1,
    #     backorder_prod_2, orig_prod_2, backorder_prod_2, etc.]
    #     """
    #     def _default_amounts(production):
    #         return [production.qty_producing, production._get_quantity_to_backorder()]

    #     if not amounts:
    #         amounts = {}
    #     for production in self:
    #         mo_amounts = amounts.get(production)
    #         if not mo_amounts:
    #             amounts[production] = _default_amounts(production)
    #             continue
    #         total_amount = sum(mo_amounts)
    #         if total_amount < production.product_qty and not cancel_remaning_qty:
    #             amounts[production].append(production.product_qty - total_amount)
    #         elif total_amount > production.product_qty or production.state in ['done', 'cancel']:
    #             raise UserError(_("Unable to split with more than the quantity to produce."))

    #     backorder_vals_list = []
    #     initial_qty_by_production = {}
    #     # Create the backorders.
    #     for production in self:
    #         initial_qty_by_production[production] = production.product_qty
    #         # if production.backorder_sequence == 0:  # Activate backorder naming
    #         #     production.backorder_sequence = 
    #         # production.name = self._get_name_backorder(production.name, production.backorder_sequence)
    #         # production.product_qty = amounts[production][0]
    #         backorder_vals = production.copy_data(default=production._get_backorder_mo_vals())[0]
    #         # backorder_qtys = amounts[production][1:]
    #         backorder_qtys = amounts[production]

    #         next_seq = max(production.procurement_group_id.mrp_production_ids.mapped("backorder_sequence"), default=1)

    #         for qty_to_backorder in backorder_qtys:
    #             next_seq += 1
    #             backorder_vals_list.append(dict(
    #                 backorder_vals,
    #                 product_qty=qty_to_backorder,
    #                 name=production._get_name_backorder(production.name, next_seq),
    #                 backorder_sequence=next_seq,
    #                 state='confirmed'
    #             ))


        
    #     backorders = self.env['mrp.production'].create(backorder_vals_list)
    #     print(len(backorders),backorders)
    #     index = 0
    #     production_to_backorders = {}
    #     production_ids = OrderedSet()
    #     for production in self:
    #         number_of_backorder_created = len(amounts.get(production, _default_amounts(production))) - 1
    #         production_backorders = backorders[index:(index + number_of_backorder_created)+1]
    #         production_to_backorders[production] = production_backorders
    #         production_ids.update(production.ids)
    #         production_ids.update(production_backorders.ids)
    #         index += number_of_backorder_created

       
    #     # Split the `stock.move` among new backorders.
    #     new_moves_vals = []
    #     moves = []
    #     for production in self:
    #         for move in production.move_raw_ids | production.move_finished_ids:
    #             if move.additional:
    #                 continue
    #             unit_factor = move.product_uom_qty / initial_qty_by_production[production]
    #             initial_move_vals = move.copy_data(move._get_backorder_move_vals())[0]
    #             move.with_context(do_not_unreserve=True).product_uom_qty = production.product_qty * unit_factor

    #             for backorder in production_to_backorders[production]:
    #                 move_vals = dict(
    #                     initial_move_vals,
    #                     product_uom_qty=backorder.product_qty * unit_factor
    #                 )
    #                 if move.raw_material_production_id:
    #                     move_vals['raw_material_production_id'] = backorder.id
    #                 else:
    #                     move_vals['production_id'] = backorder.id
    #                 new_moves_vals.append(move_vals)
    #                 moves.append(move)
       
    #     backorder_moves = self.env['stock.move'].create(new_moves_vals)
    #     # Split `stock.move.line`s. 2 options for this:
    #     # - do_unreserve -> action_assign
    #     # - Split the reserved amounts manually
    #     # The first option would be easier to maintain since it's less code
    #     # However it could be slower (due to `stock.quant` update) and could
    #     # create inconsistencies in mass production if a new lot higher in a
    #     # FIFO strategy arrives between the reservation and the backorder creation
    #     move_to_backorder_moves = defaultdict(lambda: self.env['stock.move'])
    #     for move, backorder_move in zip(moves, backorder_moves):
    #         move_to_backorder_moves[move] |= backorder_move

    #     move_lines_vals = []
    #     assigned_moves = set()
    #     partially_assigned_moves = set()
    #     move_lines_to_unlink = set()

    #     for initial_move, backorder_moves in move_to_backorder_moves.items():
    #         ml_by_move = []
    #         product_uom = initial_move.product_id.uom_id
    #         for move_line in initial_move.move_line_ids:
    #             available_qty = move_line.product_uom_id._compute_quantity(move_line.product_uom_qty, product_uom)
    #             if float_compare(available_qty, 0, precision_rounding=move_line.product_uom_id.rounding) <= 0:
    #                 continue
    #             ml_by_move.append((available_qty, move_line, move_line.copy_data()[0]))

    #         initial_move.move_line_ids.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
    #         moves = list(initial_move | backorder_moves)

    #         move = moves and moves.pop(0)
    #         move_qty_to_reserve = move.product_qty
    #         for quantity, move_line, ml_vals in ml_by_move:
    #             while float_compare(quantity, 0, precision_rounding=product_uom.rounding) > 0 and move:
    #                 # Do not create `stock.move.line` if there is no initial demand on `stock.move`
    #                 taken_qty = min(move_qty_to_reserve, quantity)
    #                 taken_qty_uom = product_uom._compute_quantity(taken_qty, move_line.product_uom_id)
    #                 if move == initial_move:
    #                     move_line.with_context(bypass_reservation_update=True).product_uom_qty = taken_qty_uom
    #                     if set_consumed_qty:
    #                         move_line.qty_done = taken_qty_uom
    #                 elif not float_is_zero(taken_qty_uom, precision_rounding=move_line.product_uom_id.rounding):
    #                     new_ml_vals = dict(
    #                         ml_vals,
    #                         product_uom_qty=taken_qty_uom,
    #                         move_id=move.id
    #                     )
    #                     if set_consumed_qty:
    #                         new_ml_vals['qty_done'] = taken_qty_uom
    #                     move_lines_vals.append(new_ml_vals)
    #                 quantity -= taken_qty
    #                 move_qty_to_reserve -= taken_qty

    #                 if float_compare(move_qty_to_reserve, 0, precision_rounding=move.product_uom.rounding) <= 0:
    #                     assigned_moves.add(move.id)
    #                     move = moves and moves.pop(0)
    #                     move_qty_to_reserve = move and move.product_qty or 0

    #             # Unreserve the quantity removed from initial `stock.move.line` and
    #             # not assigned to a move anymore. In case of a split smaller than initial
    #             # quantity and fully reserved
    #             if quantity:
    #                 self.env['stock.quant']._update_reserved_quantity(
    #                     move_line.product_id, move_line.location_id, -quantity,
    #                     lot_id=move_line.lot_id, package_id=move_line.package_id,
    #                     owner_id=move_line.owner_id, strict=True)

    #         if move and move_qty_to_reserve != move.product_qty:
    #             partially_assigned_moves.add(move.id)

    #         move_lines_to_unlink.update(initial_move.move_line_ids.filtered(
    #             lambda ml: not ml.product_uom_qty and not ml.qty_done).ids)

    #     self.env['stock.move'].browse(assigned_moves).write({'state': 'assigned'})
    #     self.env['stock.move'].browse(partially_assigned_moves).write({'state': 'partially_available'})
    #     # Avoid triggering a useless _recompute_state
    #     self.env['stock.move.line'].browse(move_lines_to_unlink).write({'move_id': False})
    #     self.env['stock.move.line'].browse(move_lines_to_unlink).unlink()
    #     self.env['stock.move.line'].create(move_lines_vals)

    #     # We need to adapt `duration_expected` on both the original workorders and their
    #     # backordered workorders. To do that, we use the original `duration_expected` and the
    #     # ratio of the quantity produced and the quantity to produce.
    #     for production in self:
    #         initial_qty = initial_qty_by_production[production]
    #         initial_workorder_remaining_qty = []
    #         bo = production_to_backorders[production]

    #         # Adapt duration
    #         for workorder in (production | bo).workorder_ids:
    #             workorder.duration_expected = workorder.duration_expected * workorder.production_id.product_qty / initial_qty

    #         # Adapt quantities produced
    #         for workorder in production.workorder_ids:
    #             initial_workorder_remaining_qty.append(max(workorder.qty_produced - workorder.qty_production, 0))
    #             workorder.qty_produced = min(workorder.qty_produced, workorder.qty_production)
    #         workorders_len = len(bo.workorder_ids)
    #         for index, workorder in enumerate(bo.workorder_ids):
    #             remaining_qty = initial_workorder_remaining_qty[index // workorders_len]
    #             if remaining_qty:
    #                 workorder.qty_produced = max(workorder.qty_production, remaining_qty)
    #                 initial_workorder_remaining_qty[index % workorders_len] = max(remaining_qty - workorder.qty_produced, 0)
    #     backorders.workorder_ids._action_confirm()

    #     return self.env['mrp.production'].browse(production_ids)

    def action_split(self):
        self._pre_action_split_merge_hook(split=True)
        if len(self) > 1:
            productions = [Command.create({'production_id': production.id}) for production in self]
            # Wizard need a real id to have buttons enable in the view
            wizard = self.env['mrp.production.split.multi'].create({'production_ids': productions})
            action = self.env['ir.actions.actions']._for_xml_id('split_manufacturing.action_mrp_production_split_multi')
            action['res_id'] = wizard.id
            return action
        else:
            action = self.env['ir.actions.actions']._for_xml_id('split_manufacturing.action_mrp_production_split')
            action['context'] = {
                'default_production_id': self.id,
            }
            return action

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