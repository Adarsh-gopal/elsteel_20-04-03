# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import date
import datetime
from lxml import etree
import math, datetime

class CurrencyCustomMaster(models.Model):
    _name = 'custom.currency.master.line'
    _rec_name = 'currency_id'
    _description = "Master Currency Line"

    currency_id = fields.Many2one('res.currency',string="Currency")
    # company_rate = fields.Float(string="Unit per Currency")
    inverse_company_rate = fields.Float(string="Unit per Currency")
    currency_line_id = fields.Many2one('custom.currency.master')
    
    @api.constrains('currency_id')
    def _check_parent_currency_id(self):
        for rec in self:
            if rec.currency_id == rec.currency_line_id.currency_id:
                raise UserError("{} is your Report Currency.".format(rec.currency_id.name))
            for line in rec.currency_line_id.currency_line_ids:
                if rec.currency_id == line.currency_id and rec.id != line.id:
                    raise ValidationError(_("""Currency already exists!"""))


class CurrencyCustomMaster(models.Model):
    _name = 'custom.currency.master'
    _rec_name = 'currency_id'
    _description = "Master Currency"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    currency_id = fields.Many2one('res.currency',string="Currency",tracking=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    currency_line_ids = fields.One2many('custom.currency.master.line','currency_line_id')
    active = fields.Boolean(default=True)
    
    @api.onchange('currency_id')
    def _onchange_is_current_company_currency(self):
        if self.currency_id and self.currency_id == self.company_id.currency_id:
            raise UserError("This is your Report Currency.")
        for line in self.currency_line_ids:
            if self.currency_id == line.currency_id:
                raise ValidationError(_("""Currency already exists in Currency Line!"""))



    @api.constrains('currency_id','company_id')
    def check_order_delay_reason(self):
        for rec in self:
            docs=rec.env['custom.currency.master'].search([('currency_id','=',rec.currency_id.id),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""Currency already exists!"""))

    # @api.model
    # def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     result = super(CurrencyCustomMaster, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type in ('tree'):
    #         names = {
    #             'company_currency_name': (self.env['res.company'].browse(self._context.get('company_id')) or self.env.company).currency_id.name,
    #             'rate_currency_name': self.env['res.currency'].browse(self._context.get('active_id')).name or 'Unit',
    #         }
    #         doc = etree.XML(result['arch'])
    #         for field in [['company_rate', _('%(rate_currency_name)s per %(company_currency_name)s', **names)],
    #                       ['inverse_company_rate', _('%(company_currency_name)s per %(rate_currency_name)s', **names)]]:
    #             node = doc.xpath("//tree//field[@name='%s']" % field[0])
    #             if node:
    #                 node[0].set('string', field[1])
    #         result['arch'] = etree.tostring(doc, encoding='unicode')
    #     if view_type in ('form'):
    #         names = {
    #             'company_currency_name': (self.env['res.company'].browse(self._context.get('company_id')) or self.env.company).currency_id.name,
    #             'rate_currency_name': self.env['res.currency'].browse(self._context.get('active_id')).name or 'Unit',
    #         }
    #         doc = etree.XML(result['arch'])
    #         for field in [['company_rate', _('%(rate_currency_name)s per %(company_currency_name)s', **names)],
    #                       ['inverse_company_rate', _('%(company_currency_name)s per %(rate_currency_name)s', **names)]]:
    #             node = doc.xpath("//form//field[@name='%s']" % field[0])
    #             if node:
    #                 node[0].set('string', field[1])
    #         result['arch'] = etree.tostring(doc, encoding='unicode')
    #     return result


class OrderDelayReason(models.Model):
    _name = 'order.delay.reason'

    name = fields.Char(size=50)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)

    @api.constrains('name','company_id')
    def check_order_delay_reason(self):
        for rec in self:
            docs=rec.env['order.delay.reason'].search([('name','=',rec.name),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""Name already exists!"""))




class SaleOrderInhandReport(models.Model):
    _inherit = 'sale.order'

    delay_num_weeks = fields.Integer(compute='_compute_delay_num_weeks_days')
    order_value_currency = fields.Float(compute='_compute_amount_convert_currency')
    total_order_quantity = fields.Float(compute="_compute_product_uom_qty_onhand_report")
    order_box_qty = fields.Float()
    order_invoiced_qty = fields.Float(compute="_compute_order_invoiced_qty_onhand")
    order_notes = fields.Char(compute='_compute_order_notes')
    order_delay_reason = fields.Many2one('order.delay.reason',string="Order Delay Reason") 
    is_delivery_done = fields.Boolean(compute='_compute_is_delivery_done_onhand',store=True)
    requested_dispatch_date = fields.Date()
    expected_dispatch_date = fields.Date(string="Expected Dispatch Date")
    order_date = fields.Date()

    def update_order_inhand_report_values(self):
        self._compute_order_invoiced_qty_onhand()
        self._compute_product_uom_qty_onhand_report()
        self._compute_amount_convert_currency()


    @api.depends('total_order_quantity','order_line.qty_delivered')
    def _compute_is_delivery_done_onhand(self):
        for rec in self:
            if rec.order_line:
                total_delivered_quantity = sum(rec.order_line.mapped('qty_delivered'))
                if total_delivered_quantity == rec.total_order_quantity:
                    rec.is_delivery_done = True
                else:
                    rec.is_delivery_done = False
            else:
                rec.is_delivery_done = False



    @api.depends('order_line.qty_invoiced')
    def _compute_order_invoiced_qty_onhand(self):
        for rec in self:
            if rec.order_line:
                rec.order_invoiced_qty = sum(rec.order_line.mapped('qty_invoiced'))
            else:
                rec.order_invoiced_qty = 0



    @api.depends('order_line.product_uom_qty')
    def _compute_product_uom_qty_onhand_report(self):
        for rec in self:
            if rec.order_line:
                rec.total_order_quantity = sum(rec.order_line.mapped('product_uom_qty'))
            else:
                rec.total_order_quantity = 0

    @api.depends('amount_total','currency_id')
    def _compute_amount_convert_currency(self):
        for rec in self:
            currency = self.env['res.currency'].browse(int(self.env['ir.config_parameter'].sudo().get_param('orderihreport.inhand_currency')))
            if currency:
                if rec.currency_id != currency:
                    master_id = self.env['custom.currency.master'].search([('currency_id','=',currency.id)])
                    amount_convert = 0
                    for line in master_id.currency_line_ids:
                        if line.currency_id == rec.currency_id:
                            amount_convert = line.inverse_company_rate * rec.amount_total
                    if amount_convert > 0:
                        rec.order_value_currency = amount_convert
                    else:
                        rec.order_value_currency = rec.amount_total                            
                else:
                    rec.order_value_currency = rec.amount_total
            else:
                rec.order_value_currency = rec.amount_total


    # @api.depends('amount_total','currency_id')
    # def _compute_amount_convert_currency(self):
    #     for rec in self:
    #         currency = self.env['res.currency'].browse(int(self.env['ir.config_parameter'].sudo().get_param('orderihreport.inhand_currency')))
    #         if currency.rate_ids:
    #             if rec.currency_id != currency:
    #                 amount_convert = rec.currency_id.with_context(date=fields.Date.today()).compute(rec.amount_total, currency)
    #                 rec.order_value_currency = amount_convert
    #             else:
    #                 rec.order_value_currency = rec.amount_total
    #         else:
    #             rec.order_value_currency = rec.amount_total


    @api.depends('order_line.product_id')
    def _compute_order_notes(self):
        for rec in self:
            if rec.order_line:
                order_note = " ".join(set([production.product_id.product_tmpl_id.product_group_1.name+',' if production.product_id.product_tmpl_id.product_group_1 else ''  for production in rec.order_line]))
                rec.order_notes = order_note[:-1]
            else:
                rec.order_notes = False

        
    

   
    @api.depends('requested_dispatch_date','expected_dispatch_date')
    def _compute_delay_num_weeks_days(self):
        for rec in self:
            if rec.requested_dispatch_date and rec.expected_dispatch_date:
                rec.delay_num_weeks = ((rec.expected_dispatch_date - rec.requested_dispatch_date).days / 7)
            else:
                rec.delay_num_weeks = 0



    @api.onchange('expected_dispatch_date')
    def _onchange_expected_dispatch_date(self):
        for rec in self:
            if rec.order_date and rec.expected_dispatch_date:
                if rec.expected_dispatch_date < rec.order_date:
                    raise UserError('Requested Dispatch Date Should be grater than Order Date')
            if rec.requested_dispatch_date and rec.expected_dispatch_date: 
                if rec.requested_dispatch_date > rec.expected_dispatch_date:
                    raise UserError('Expected Dispatch Date Should be grater than Requested Dispatch Date')
            
    @api.onchange('commitment_date')
    def _onchange_commitment_date_inhand(self):
        for rec in self:
            if rec.commitment_date:
                rec.expected_dispatch_date = rec.commitment_date
                rec.requested_dispatch_date = rec.commitment_date
                if rec.date_order:
                    rec.order_date = rec.date_order
            if rec.requested_dispatch_date and rec.expected_dispatch_date: 
                if rec.requested_dispatch_date > rec.expected_dispatch_date:
                    raise UserError('Expected Dispatch Date Should be grater than Requested Dispatch Date')

    
    @api.onchange('date_order')
    def _onchange_date_order_inhand(self):
        for rec in self:
            if rec.date_order:
                rec.order_date = rec.date_order
            if rec.date_order and rec.expected_dispatch_date:
                if rec.expected_dispatch_date < rec.order_date:
                    raise UserError('Requested Dispatch Date Should be grater than Order Date')
        

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    inhand_currency_id = fields.Many2one('res.currency',string='Inhand Currency')

    def set_values(self):
        super(ResConfigSettings,self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('orderihreport.inhand_currency',self.inhand_currency_id.id)
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            inhand_currency_id = int(params.get_param('orderihreport.inhand_currency'))
        )
        return res
     