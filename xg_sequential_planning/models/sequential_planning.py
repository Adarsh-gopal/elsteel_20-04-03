# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        if 'date_deadline' in vals:
            if self._context.get('change_dead_line'):
                if self._context.get('change_dead_line') == True:
                    vals.pop('date_deadline')
        res = super(StockMove, self).write(vals)
        return res


class MRPBOM(models.Model):
    _inherit = 'mrp.bom'

    xg_activate_sequential_planning = fields.Boolean(string="Activate Sequential Planning")
    


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    def action_sequential_planning(self):
        for order in self:
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
                if mo_id.bom_id.xg_activate_sequential_planning == True:
                    mo_list.append(mo_id)
            float_list = []
            for x in mo_list:
                if x.split_sequence not in float_list:
                    float_list.append(x.split_sequence) 
            float_list.sort(reverse=True)
            for float_value in float_list:
                for mos in mo_list:                
                    if mos.split_sequence == float_value:
                        if mos.workorder_ids:
                            mos._context.update({'change_dead_line':True})
                            mos.button_plan()
                            if float_value != float_list[-1]:
                                for search_mo in mo_list:
                                    if search_mo.split_sequence == float_list[float_list.index(float_value)+1]:
                                        if search_mo.state == 'confirmed':
                                            search_mo.write({'date_planned_start' :max(mos.workorder_ids.mapped('date_planned_finished'))})
                                




        # def button_plan(self):
        # """ Create work orders. And probably do stuff, like things. """
        # orders_to_plan = self.filtered(lambda order: not order.is_planned)
        # orders_to_confirm = orders_to_plan.filtered(lambda mo: mo.state == 'draft')
        # orders_to_confirm.action_confirm()
        # for order in orders_to_plan:
        #     order._plan_workorders()
        # return True
