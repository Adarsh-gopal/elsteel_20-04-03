# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError



class MRPBOM(models.Model):
    _inherit = 'mrp.bom'

    xg_activate_sequential_planning = fields.Boolean(string="Activate Sequential Planning")
    


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # new_date = fields.Datetime()

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
            child_lst.sort(reverse=True)

            mo_list = []
            for line in child_lst:
                mo_id = self.env['mrp.production'].search([('id','=',line)])
                if mo_id.bom_id.xg_activate_sequential_planning == True:
                    mo_list.append(mo_id)
            # print(mo_list,"MO List",order)

            for mos in mo_list:
                if mos.workorder_ids:
                    mos.button_plan()
                    if mos != mo_list[-1]:
                        print('\n\n\n\n')
                        if mo_list[mo_list.index(mos)+1].state == 'confirmed':
                            mo_list[mo_list.index(mos)+1].write({'date_planned_start' :max(mos.workorder_ids.mapped('date_planned_finished'))})
                    




        # def button_plan(self):
        # """ Create work orders. And probably do stuff, like things. """
        # orders_to_plan = self.filtered(lambda order: not order.is_planned)
        # orders_to_confirm = orders_to_plan.filtered(lambda mo: mo.state == 'draft')
        # orders_to_confirm.action_confirm()
        # for order in orders_to_plan:
        #     order._plan_workorders()
        # return True
