# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import date
import datetime


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
    order_value_currency = fields.Float(compute='_compute_amount_convert_currency',store=True)
    # estimated_time_dispatch  =  fields.Datetime(help='Estimated Time Dispatch')
    # estimated_time_arrive  =  fields.Datetime(help='Estimated Time Arrival')
    order_notes = fields.Char(compute='_compute_order_notes')
    requested_dispatch_date = fields.Datetime(string="Requested Dispatch Date")
    order_delay_reason = fields.Many2one('order.delay.reason',string="Order Delay Reason") 
    order_box_qty = fields.Float(compute="_compute_product_uom_qty_onhand_report",store=True)
    order_week_name = fields.Char(string="Week No")
    order_invoiced_qty = fields.Float(compute="_compute_order_invoiced_qty_onhand",store=True)

    
    
    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None,orderby=False, lazy=True):
    #     result = super(SaleOrderInhandReport, self).read_group(domain, fields,groupby, offset, limit, orderby, lazy)
    #     for res in result:
    #         # import pdb;
    #         # pdb.set_trace()
    #         if res.get('date_order:week'):
    #             # my_date = datetime.date.res.get('date_order')
    #             # year, week_num, day_of_week = my_date.isocalendar()
    #             if fields[4] == 'order_week_name':
    #                 fields[4] = res.get('date_order:week')

    #     return result

    def flow_values(self):
        self._compute_order_invoiced_qty_onhand()
        self._compute_product_uom_qty_onhand_report()
        self._compute_amount_convert_currency()

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
                rec.order_box_qty = sum(rec.order_line.mapped('product_uom_qty'))
            else:
                rec.order_box_qty = 0

    @api.depends('amount_total','currency_id')
    def _compute_amount_convert_currency(self):
        for rec in self:
            currency = self.env['res.currency'].browse(int(self.env['ir.config_parameter'].sudo().get_param('orderihreport.inhand_currency')))
            if currency.rate_ids:
                if rec.currency_id != currency:
                    amount_convert = rec.currency_id.with_context(date=fields.Date.today()).compute(rec.amount_total, currency)
                    rec.order_value_currency = amount_convert
                else:
                    rec.order_value_currency = rec.amount_total
            else:
                rec.order_value_currency = rec.amount_total


    @api.depends('order_line.product_id')
    def _compute_order_notes(self):
        for rec in self:
            if rec.order_line:
                order_note = " ".join(set([production.product_id.product_tmpl_id.product_group_1.name+',' if production.product_id.product_tmpl_id.product_group_1 else ''  for production in rec.order_line]))
                rec.order_notes = order_note[:-1]
            else:
                rec.order_notes = False

        
    

    @api.depends('commitment_date','requested_dispatch_date')
    def _compute_delay_num_weeks_days(self):
        for rec in self:
            if rec.commitment_date and rec.requested_dispatch_date:
                rec.delay_num_weeks = (abs(rec.commitment_date - rec.requested_dispatch_date).days//7)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
            else:
                rec.delay_num_weeks = 0




    @api.onchange('requested_dispatch_date')
    def _onchange_requested_dispatch_date(self):
        for rec in self:
            if rec.date_order and rec.requested_dispatch_date:
                if rec.requested_dispatch_date < rec.date_order:
                    raise UserError('Requested Dispatch Date Should be grater than Order Date')
            if rec.commitment_date and rec.requested_dispatch_date: 
                if rec.commitment_date < rec.requested_dispatch_date:
                    raise UserError('Requested Dispatch Date Should be less than Delivery Date')

    @api.onchange('commitment_date')
    def _onchange_commitment_date_inhand(self):
        for rec in self:
            if rec.commitment_date and rec.requested_dispatch_date: 
                if rec.commitment_date < rec.requested_dispatch_date:
                    raise UserError('Requested Dispatch Date Should be less than Delivery Date')

    @api.onchange('date_order')
    def _onchange_date_order_inhand(self):
        for rec in self:
            if rec.date_order and rec.requested_dispatch_date:
                if rec.requested_dispatch_date < rec.date_order:
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
     