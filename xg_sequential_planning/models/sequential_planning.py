# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from itertools import chain

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
            
            # split_sequence Code Start
            float_list = []
            for x in mo_list:
                if x.split_sequence not in float_list:
                    float_list.append(x.split_sequence) 
            float_list.sort()
            float_list.sort(reverse=True)

            
            value = int(float_list[0])
            values = []
            for l in range(value+1):
                if l != 0:
                    values.append(l)
            values.sort(reverse=True)
            created_list = []
            for new_val in values:
                new_list = self.split_at_values(new_val,float_list)
                if len(new_list):
                    created_list.append(new_list)

            value = 0
            new_sequence_list = []
            for list1 in range(0,len(created_list[0])):
                new_sequence_list = new_sequence_list + [item[value]  for item in created_list[:-1]]
                value+=1
            
            
            list_count = len(created_list)-2
            new_sequence_list.append(float_list[-1])
            # split_sequence Code End

            for float_value in new_sequence_list:
                for mos in mo_list:                
                    if mos.split_sequence == float_value:
                        if mos.workorder_ids:
                            mos._context.update({'change_dead_line':True})
                            mos.button_plan()
                            if float_value != new_sequence_list[-1]:
                                for search_mo in mo_list:
                                    if int(float_value) != int(new_sequence_list[-2]):
                                        if search_mo.split_sequence == new_sequence_list[new_sequence_list.index(float_value)+1]:
                                            if search_mo.state == 'confirmed':
                                                search_mo.write({'date_planned_start' :max(mos.workorder_ids.mapped('date_planned_finished'))})
                                    if float_value == new_sequence_list[-2]:
                                        if search_mo.split_sequence == new_sequence_list[-1]:
                                            if search_mo.state == 'confirmed':
                                                search_mo.write({'date_planned_start' :max(mos.workorder_ids.mapped('date_planned_finished'))})
                                                
        
    def split_at_values(self,number, values):
        first_val = int(values[0])
        new_list_list = []
        for value in values:
            if number == first_val:
                if value >= number:
                    new_list_list.append(value)
            else:
                if (number+1) > value >= number:
                    new_list_list.append(value)
        return new_list_list
