from urllib import request
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import json


class WorkCentreCategory(models.Model):
    _name = 'workcenter.category'

    name = fields.Char(string='Name')
    categ_sequence_id = fields.Many2one('ir.sequence',string='Sequence')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    
    # @api.constrains('name','company_id')
    # def check_item_group_code(self):
    #     for rec in self:
    #         docs=rec.env['workcenter.category'].search([('name','=',rec.name),('company_id','=',rec.company_id.id)])
    #         if len(docs) > 1:
    #             raise ValidationError(_("""Name already exists!"""))


class WorkCenter(models.Model):
    _inherit ='mrp.workcenter'

    workcentre_category_id = fields.Many2one('workcenter.category',string='Work Center Category') 
    is_workcenter_category_id = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self,vals_list):
        for values in vals_list:
            sequence = self.env['workcenter.category'].browse(values.get('workcentre_category_id')).categ_sequence_id
            if values.get('workcentre_category_id') or (values.get('code') == False and sequence):
                values.update({'code':sequence.next_by_id()})
        res=super().create(vals_list)
        return res

    


    def write(self, values):
        res =super(WorkCenter, self).write(values)
        if values.get('workcentre_category_id') or (not self.code and self.workcentre_category_id.categ_sequence_id):
            self.code = self.workcentre_category_id.categ_sequence_id.next_by_id() 
        return res

    @api.onchange('workcentre_category_id')
    def _onchange_workcentre_category_id(self):
        for rec in self:
            if rec.code:
                rec.is_workcenter_category_id = True
            else:
                rec.is_workcenter_category_id = False


class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    output_quantity = fields.Float(string="Output Quantity", store=True)
    output_bool = fields.Boolean(string="Output Boolean")

    
class workOrderCategory(models.Model):
    _name = 'wizard.outquantity'

    output_quantity = fields.Float(string="Quantity Output", required=True)
    
    
    def added(self):
        timeline_obj = self.env['mrp.workcenter.productivity']
        domain = [('workorder_id', '=', self._context.get('active_id')), ('output_bool', '=', False)]
        
        

        wod=self.env['mrp.workorder'].search([('id','=',self._context.get('active_id'))])

        if (self.output_quantity + wod.total_output_quantity) > wod.production_id.qty_producing:
            raise UserError("Output quantity should not be greater than product quantity")


        total_output_quantity_list = wod.production_id.workorder_ids.filtered(lambda x: x.workcenter_routing_sequence < wod.workcenter_routing_sequence).mapped('total_output_quantity')
        if len(total_output_quantity_list):
            for line in total_output_quantity_list: 
                if (wod.total_output_quantity + self.output_quantity) > line:
                    raise UserError("Output quantity should not be greater than product quantity")
        
        productivity_workorder = self.env['mrp.workcenter.productivity'].search(domain)
        if productivity_workorder:
            productivity_workorder[0].output_quantity = self.output_quantity
            productivity_workorder[0].output_bool = True

        # for timeline in timeline_obj.search(domain):
        #   timeline.output_quantity = self.output_quantity
        #   timeline.output_bool = True 

            
        return True
    

class workOrderCategory(models.Model):
    _inherit = 'mrp.workorder'

    total_output_quantity = fields.Float(string = "Total output quantity",  compute ='compute_total_outquantity' )
    workcenter_routing_sequence = fields.Integer(string = "Workcenter Routing Sequence", related = "operation_id.sequence", store = True)
    total_workorder_demand=fields.Float(string="Demand", related="production_id.product_qty")
    total_workorder_remaining=fields.Float(string="Remaining",compute="compute_total_remaining_quantity")


    @api.depends('total_output_quantity','total_workorder_demand')
    def compute_total_remaining_quantity(self):
        for line_record in self:
            if line_record:
                line_record.total_workorder_remaining=line_record.total_workorder_demand-line_record.total_output_quantity

    @api.depends('time_ids.output_quantity')
    def compute_total_outquantity(self):
        for rec in self:
            rec.total_output_quantity = sum(rec.time_ids.mapped('output_quantity'))
            if rec.total_output_quantity > rec.production_id.qty_producing:
                raise UserError("Output quantity should not be greater than product quantity")
            

    def button_pending(self):
        res = super(workOrderCategory, self).button_pending()
        if self._context.get('active_model') == 'mrp.workorder':
            return {
                        'name':_("Workorder_wizard"),
                        'view_mode': 'form',
                        'view_id': self.env.ref('manufacturing_base.mrp_workorder_center_category_ZZZZ').id,
                        'view_type': 'form',
                        'res_model': 'wizard.outquantity',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'active_ids':self.ids
                    }
        else:
            return res


    def unlink(self):
        if self.date_planned_start or self.state == 'done':
            raise UserError("Operation cannot be Deleted")
        res = super(workOrderCategory,self).unlink()
        return res

class MrpProductionOutputQty(models.Model):
    _inherit = 'mrp.production'

    mrp_production_child_count = fields.Integer(copy=False)

    so_origin = fields.Char("Sale Order",compute='_compute_sale_origin',store=True)
    # so_origin = fields.Char("Parent Source")

    def button_mark_done(self):
        for rec in self.workorder_ids:
            if rec.date_planned_finished:
                if rec.total_output_quantity == 0:
                    raise UserError("{} Operation Output Quantity not Recored".format(rec.name))
            else:
                raise UserError("{} Operation Not Started".format(rec.name))


        res = super(MrpProductionOutputQty, self).button_mark_done()

        return res

    @api.depends('origin','name')
    def _compute_sale_origin(self):
        for rec in self:
            parent_sale = self.env['sale.order'].search([('name','=',rec.origin)])
            if not parent_sale:
                mrp_origin = self.env['mrp.production'].search([('name','=',rec.origin)])
                sale_origin = self.env['sale.order'].search([('name','=',mrp_origin.origin)])
                if sale_origin:
                    rec.so_origin = mrp_origin.origin
                else:
                    rec.so_origin = mrp_origin.so_origin
            else:
                rec.so_origin = rec.origin
            # if rec.so_origin:
            #     rec.so_origin = self[0].so_origin
            # else:
            #     rec.so_origin = self[0].origin
                
    
    def update_sale_order_number(self):
        for rec in self:
            parent_sale = self.env['sale.order'].search([('name','=',rec.origin)])
            if not parent_sale:
                mrp_origin = self.env['mrp.production'].search([('name','=',rec.origin)])
                sale_origin = self.env['sale.order'].search([('name','=',mrp_origin.origin)])
                if sale_origin:
                    rec.so_origin = mrp_origin.origin
                else:
                    rec.so_origin = mrp_origin.so_origin
            else:
                rec.so_origin = rec.origin



    # @api.model_create_multi
    # def create(self,vals):
    #     if not self._context.get('params'):
    #         for rec in vals:       
    #             sale_origin = self.env['mrp.production'].search([('name','=',rec.get('origin'))])
    #             if sale_origin.origin:
    #                 rec['origin'] = sale_origin.origin

    #     # else:
    #     #     if self._context.get('params').get('model') != 'mrp.production' :
    #     #         for rec in vals:       
    #     #             sale_origin = self.env['mrp.production'].search([('name','=',rec.get('origin'))])
    #     #             if sale_origin.origin:
    #     #                 rec['origin'] = sale_origin.origin

    #     res = super(MrpProductionOutputQty,self).create(vals)
    #     return res







    # @api.model_create_multi
    # def create(self,vals):
    #     if not self._context.get('params'):
    #         for rec in vals:       
    #             sale_origin = self.env['mrp.production'].search([('name','=',rec.get('origin'))])
    #             if sale_origin.origin:
    #                 rec['origin'] = sale_origin.origin

    #     # else:
    #     #     if self._context.get('params').get('model') != 'mrp.production' :
    #     #         for rec in vals:       
    #     #             sale_origin = self.env['mrp.production'].search([('name','=',rec.get('origin'))])
    #     #             if sale_origin.origin:
    #     #                 rec['origin'] = sale_origin.origin

    #     res = super(MrpProductionOutputQty,self).create(vals)
    #     return res