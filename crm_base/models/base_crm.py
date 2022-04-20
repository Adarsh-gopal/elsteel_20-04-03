# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class Lead(models.Model):
    _inherit =  "crm.lead"

    coordinator_id = fields.Many2one('res.users','Responsible By')
    expected_date = fields.Datetime(string='Expected Closing', copy=False, default=fields.Datetime.now)
  
    # lns_user_ids = fields.Many2many('res.users', 'lns_user_team_id',string='Users')
    cust_user_ids = fields.Many2many('res.users', 'cust_user_crm_ref','cust_lead_id','cust_user_id',string='Users')
    # lns_property_status = fields.Many2one('lns.property.status','Property Status')
    # lns_property_type = fields.Many2one('lns.property.type','Property Type')
    cust_type_of_sale = fields.Selection([('standard','Standard'),('project','Project')],string='Type of Sale')
    
    crm_product_line_ids = fields.One2many('cust.crm.lead.prduct.line','cust_crm_lead_id')
    
    # Related Sale Order Line

    # crm_product_line_ids = fields.One2many('sale.order.line','cust_crm_lead_id')

    # @api.onchange('expected_date')
    # def onchange_date(self):
    #     for rec in self:
    #         if rec.expected_date:
    #             rec.date_deadline=rec.expected_date

    # @api.onchange('crm_product_line_ids')
    # def calc_planned_revenue(self):
    #     total =  0
    #     for line in self.crm_product_line_ids:
    #         total += line.price_subtotal
    #     self.expected_revenue = total

    # @api.onchange('team_id')
    # def get_uer_ids(self):
    #     for each_lead in self:
    #         if each_lead.team_id:
    #             each_lead.cust_user_ids = [(6, 0, each_lead.team_id.member_ids.ids)]

    # def update_data(self):
    #     for record in self.crm_product_line_ids:
    #         a=0
    #         record.price_unit = record.product_id.lst_price
    #         tot=self.env['stock.quant'].search([('product_id','=',record.product_id.id),('product_id.default_code','=',record.product_id.default_code)])
    #         for i in tot:
    #             if i.location_id.usage=="internal" and i.location_id.location_id:
    #                 if i.available_quantity>0:
    #                     a=a+i.available_quantity                    
    #         record.available_quantity=a

    # END


    @api.onchange('expected_date')
    def onchange_date(self):
        for rec in self:
            if rec.expected_date:
                rec.date_deadline=rec.expected_date

    @api.onchange('crm_product_line_ids')
    def calc_planned_revenue(self):
        total =  0
        for line in self.crm_product_line_ids:
            total += line.cust_subtotal
        self.expected_revenue = total
    @api.onchange('team_id')
    def get_uer_ids(self):
        for each_lead in self:
            if each_lead.team_id:
                each_lead.cust_user_ids = [(6, 0, each_lead.team_id.member_ids.ids)]

    def update_data(self):
        for record in self.crm_product_line_ids:
            a=0
            record.cust_price = record.cust_product_id.lst_price
            tot=self.env['stock.quant'].search([('product_id','=',record.cust_product_id.id),('product_id.default_code','=',record.cust_product_id.default_code)])
            for i in tot:
                if i.location_id.usage=="internal" and i.location_id.location_id:
                    if i.available_quantity>0:
                        a=a+i.available_quantity                    
            record.available_quantity=a            


# Related Sale Order Line

# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     order_id = fields.Many2one('sale.order',required=False)
#     cust_crm_lead_id = fields.Many2one('crm.lead')
#     available_quantity=fields.Float(string="Available Quantity")
             

#     @api.onchange('product_id')
#     def _change_cust_price(self):       
#         for record in self:
#             a=0
#             self.price_unit = self.product_id.lst_price
#             tot=self.env['stock.quant'].search([('product_id','=',record.product_id.id),('product_id.default_code','=',record.product_id.default_code)])
#             for i in tot:
#                 if i.location_id.usage=="internal" and i.location_id.location_id:
#                     if i.available_quantity>0:
#                         a=a+i.available_quantity                    
#             record.available_quantity=a

                    
                 

#     def refreshtochange(self):
#         for record in self:
#             a=0
#             self.price_unit = self.product_id.lst_price
#             tot=self.env['stock.quant'].search([('product_id','=',record.product_id.id),('product_id.default_code','=',record.product_id.default_code)])
#             for i in tot:
#                 if i.location_id.usage=="internal" and i.location_id.location_id:
#                     if i.available_quantity>0:
#                         a=a+i.available_quantity                    
#             record.available_quantity=a

#     def update_data(self):
#         for record in self:
#             a=0
#             self.price_unit = self.product_id.lst_price
#             tot=self.env['stock.quant'].search([('product_id','=',record.product_id.id),('product_id.default_code','=',record.product_id.default_code)])
#             for i in tot:
#                 if i.location_id.usage=="internal" and i.location_id.location_id:
#                     if i.available_quantity>0:
#                         a=a+i.available_quantity                    
#             record.available_quantity=a

# END













class CRMLeadProductLine(models.Model):
    _name = "cust.crm.lead.prduct.line"
    
    _description = "CUST CRM LEAD PRODUCT LINE"

    cust_crm_lead_id = fields.Many2one('crm.lead')
    cust_product_id = fields.Many2one('product.product','Product')
    cust_qty = fields.Float('Quantity')
    cust_price = fields.Float('Price')
    cust_subtotal = fields.Float('Subtotal',compute='_calc_subtotal', store=True)
    company_currency = fields.Many2one("res.currency",string='Currency' )
    available_quantity=fields.Float(string="Available Quantity")

    @api.depends('cust_qty','cust_price','cust_subtotal')
    def _calc_subtotal(self):
        for rec in self:
            rec.cust_subtotal = rec.cust_qty * rec.cust_price

    @api.onchange('cust_product_id')
    def _change_cust_price(self):
       
        for record in self:
            a=0
            self.cust_price = self.cust_product_id.lst_price
            tot=self.env['stock.quant'].search([('product_id','=',record.cust_product_id.id),('product_id.default_code','=',record.cust_product_id.default_code)])
            for i in tot:
                if i.location_id.usage=="internal" and i.location_id.location_id:
                    if i.available_quantity>0:
                        a=a+i.available_quantity                    
            record.available_quantity=a


    def refreshtochange(self):
        for record in self:
            a=0
            self.cust_price = self.cust_product_id.lst_price
            tot=self.env['stock.quant'].search([('product_id','=',record.cust_product_id.id),('product_id.default_code','=',record.cust_product_id.default_code)])
            for i in tot:
                if i.location_id.usage=="internal" and i.location_id.location_id:
                    if i.available_quantity>0:
                        a=a+i.available_quantity                    
            record.available_quantity=a

    def update_data(self):
        for record in self:
            a=0
            self.cust_price = self.cust_product_id.lst_price
            tot=self.env['stock.quant'].search([('product_id','=',record.cust_product_id.id),('product_id.default_code','=',record.cust_product_id.default_code)])
            for i in tot:
                if i.location_id.usage=="internal" and i.location_id.location_id:
                    if i.available_quantity>0:
                        a=a+i.available_quantity                    
            record.available_quantity=a

 
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'

#     order_id = fields.Many2one('sale.order',required=False)

    

# class LnsPropertyStatus(models.Model):
#     _name = "lns.property.status"
#     name = fields.Char('Property Status')

# class LnsPropertyType(models.Model):
#     _name = "lns.property.type"
#     name = fields.Char('Property Type')