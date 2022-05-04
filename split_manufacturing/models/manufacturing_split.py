# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command
from odoo.tools import float_round, float_compare



class MrpProductionSplitMulti(models.TransientModel):
    _name = 'mrp.production.split.multi'
    _description = "Wizard to Split Multiple Productions"

    production_ids = fields.One2many('mrp.production.split', 'production_split_multi_id', 'Productions To Split')


class MrpProductionSplit(models.TransientModel):
    _name = 'mrp.production.split'
    _description = "Wizard to Split a Production"

    production_split_multi_id = fields.Many2one('mrp.production.split.multi', 'Split Productions')
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order', readonly=True)
    product_id = fields.Many2one(related='production_id.product_id')
    product_qty = fields.Float(related='production_id.product_qty')
    product_uom_id = fields.Many2one(related='production_id.product_uom_id')
    counter = fields.Integer(
        "Split #", default=0, compute="_compute_counter",
        store=True, readonly=False)
    production_detailed_vals_ids = fields.One2many(
        'mrp.production.split.line', 'mrp_production_split_id',
        'Split Details', compute="_compute_details", store=True, readonly=False)
    valid_details = fields.Boolean("Valid", compute="_compute_valid_details")
    split_sequence = fields.Float(related='production_id.split_sequence')


    @api.depends('production_detailed_vals_ids')
    def _compute_counter(self):
        for wizard in self:
            wizard.counter = len(wizard.production_detailed_vals_ids)

    @api.depends('counter')
    def _compute_details(self):
        for wizard in self:
            commands = [Command.clear()]
            if wizard.counter < 1 or not wizard.production_id:
                wizard.production_detailed_vals_ids = commands
                continue
            quantity = float_round(wizard.product_qty / wizard.counter, precision_rounding=wizard.product_uom_id.rounding)
            
            remaining_quantity = wizard.product_qty
            for _ in range(wizard.counter - 1):
                commands.append(Command.create({
                    'quantity': quantity,
                    'user_id': wizard.production_id.user_id,
                    'date': wizard.production_id.date_planned_start,
                    'product_colour' : wizard.production_id.product_colour,
                    'so_origin': wizard.production_id.so_origin,

                }))
                remaining_quantity = float_round(remaining_quantity - quantity, precision_rounding=wizard.product_uom_id.rounding)
            commands.append(Command.create({
                'quantity': remaining_quantity,
                'user_id': wizard.production_id.user_id,
                'date': wizard.production_id.date_planned_start,
                'product_colour' : wizard.production_id.product_colour,
                'so_origin': wizard.production_id.so_origin,
            }))
            wizard.production_detailed_vals_ids = commands

        

    @api.depends('production_detailed_vals_ids')
    def _compute_valid_details(self):
        self.valid_details = False
        for wizard in self:
            if wizard.production_detailed_vals_ids:
                wizard.valid_details = float_compare(wizard.product_qty, sum(wizard.production_detailed_vals_ids.mapped('quantity')), precision_rounding=wizard.product_uom_id.rounding) == 0

    def action_split(self):
        productions = self.production_id._split_productions({self.production_id : [detail.quantity for detail in self.production_detailed_vals_ids]})
        if productions:
            # for origin in productions:
            #     # origin.origin = productions[0].origin + ',' + ",".join(sorted([production.name for production in productions[1:]]))
            #     origin.origin = ",".join(sorted([production.name for production in productions]))

            # saleorder = set([production.so_origin for production in productions])
            # if len(saleorder) == 2:
            #     so_origin = list(saleorder)[1]
            # else:
            #     so_origin = saleorder.pop()       
            
            # # import pdb;
            # # pdb.set_trace()


            # productcolour = set([production.product_colour for production in productions])
            # if len(productcolour) == 2:
            #     product_colour = list(productcolour)[1]
            # else:
            #     product_colour = productcolour.pop()

            
            # morign = productions[0].origin.split(',')
            # if morign:
            #     mo_orign = morign[0]
            # else:
            #     mo_orign = False

            # if so_origin == False:
            #     search_mo_id = self.env['mrp.production'].search([('origin','=',mo_orign)]).filtered(lambda x:x.so_origin != False and x.product_colour != False)
            #     if len(search_mo_id)>1:
            #         so_origin = search_mo_id.so_origin
            #     else:
            #         for search_mo in search_mo_id:
            #             if search_mo.so_origin:
            #                 so_origin = search_mo_id.so_origin

            
            # if product_colour == False:
            #     search_mo_id = self.env['mrp.production'].search([('origin','=',mo_orign)]).filtered(lambda x:x.so_origin != False and x.product_colour != False)
            #     if len(search_mo_id)>1:
            #         product_colour = search_mo_id.product_colour
            #     else:
            #         for search_mo in search_mo_id:
            #             if search_mo.product_colour:
            #                 product_colour = search_mo_id.product_colour


            # if product_colour == False:
            #     product_colour = self.production_detailed_vals_ids[0].product_colour

            # if so_origin == False:
            #     so_origin = self.production_detailed_vals_ids[0].so_origin
            product_colour = self.production_detailed_vals_ids[0].product_colour
            so_origin = self.production_detailed_vals_ids[0].so_origin
            
            value = 0
            for mos in productions:
                mos.split_sequence = round(self.production_detailed_vals_ids[value].serial_no,2)
                value += 1
                if so_origin:
                    mos.so_origin = so_origin
                if product_colour:
                    mos.product_colour = product_colour
            # productions[0].write({'is_splited' : True})
            for production, detail in zip(productions, self.production_detailed_vals_ids):
                production.user_id = detail.user_id
                production.date_planned_start = detail.date
            if self.production_split_multi_id:
                saved_production_split_multi_id = self.production_split_multi_id.id
                self.production_split_multi_id.production_ids = [Command.unlink(self.id)]
                action = self.env['ir.actions.actions']._for_xml_id('split_manufacturing.action_mrp_production_split_multi')
                action['res_id'] = saved_production_split_multi_id
                return action


    def action_prepare_split(self):
        action = self.env['ir.actions.actions']._for_xml_id('split_manufacturing.action_mrp_production_split')
        action['res_id'] = self.id
        return action

    def action_return_to_list(self):
        self.production_detailed_vals_ids = [Command.clear()]
        self.counter = 0
        action = self.env['ir.actions.actions']._for_xml_id('split_manufacturing.action_mrp_production_split_multi')
        action['res_id'] = self.production_split_multi_id.id
        return action


class MrpProductionSplitLine(models.TransientModel):
    _name = 'mrp.production.split.line'
    _description = "Split Production Detail"

    mrp_production_split_id = fields.Many2one(
        'mrp.production.split', 'Split Production', required=True, ondelete="cascade")
    quantity = fields.Float('Quantity To Produce', digits='Product Unit of Measure', required=True)
    user_id = fields.Many2one(
        'res.users', 'Responsible', required=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('mrp.group_mrp_user').id)])
    date = fields.Datetime('Schedule Date')
    product_colour = fields.Char()
    so_origin = fields.Char()
    
    serial_no = fields.Float(string='#',compute='_compute_sl')
    
    @api.depends('quantity','user_id')
    def _compute_sl(self):
        for order in self.mapped('mrp_production_split_id'):
            number = order.split_sequence
            for line in order.production_detailed_vals_ids:
                if line == order.production_detailed_vals_ids[0]:
                    line.serial_no = number
                else:
                    number += 0.01
                    line.serial_no = number
                    
                