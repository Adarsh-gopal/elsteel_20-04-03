# -*- coding: utf-8 -*-

from odoo import models, api, fields,_
from odoo.exceptions import UserError, ValidationError


class CustomFields(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def _onchange_product_sourcing(self):
        for rec in self:
            if rec.product_id.product_sourcing == True:
                vendor_price_list = self.env['product.supplierinfo'].search([('product_tmpl_id','=',rec.product_id.product_tmpl_id.id)])
                if len(vendor_price_list):
                    vendor_list = vendor_price_list.filtered(lambda line: line.name == rec.partner_id)
                    if vendor_list.name != rec.partner_id:
                        raise UserError(_('Mismatch between selected Vendor and Sourcing for [{}]{}'.format(rec.product_id.default_code,rec.product_id.name)))
                else:
                    raise UserError(_('Missing Vendor Sourcing for [{}]{}'.format(rec.product_id.default_code,rec.product_id.name)))



class Purchasetoleranceinventry(models.Model):
    _inherit='product.template'

    product_sourcing = fields.Boolean(string='Sourcing')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.onchange('partner_id')
    def _onchange_partner_sourcing(self):
        for rec in self.order_line:
            if rec.product_id.product_sourcing == True:
                vendor_price_list = self.env['product.supplierinfo'].search([('product_tmpl_id','=',rec.product_id.product_tmpl_id.id)])
                if len(vendor_price_list):
                    vendor_list = vendor_price_list.filtered(lambda line: line.name == rec.partner_id)
                    if vendor_list.name != rec.partner_id:
                        raise UserError(_('Mismatch between selected Vendor and Sourcing for [{}]{}'.format(rec.product_id.default_code,rec.product_id.name)))
                else:
                    raise UserError(_('Missing Vendor Sourcing for [{}]{}'.format(rec.product_id.default_code,rec.product_id.name)))




# Product Sorcing for Purchase Requisition

class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition'

    @api.onchange('vendor_id')
    def _onchange_partner_sourcing(self):
        for rec in self.line_ids:
            if rec.product_id.product_sourcing == True:
                vendor_price_list = self.env['product.supplierinfo'].search([('product_tmpl_id','=',rec.product_id.product_tmpl_id.id)])
                if len(vendor_price_list):
                    vendor_list = vendor_price_list.filtered(lambda line: line.name == rec.requisition_id.vendor_id)
                    if vendor_list.name != rec.requisition_id.vendor_id:
                        raise UserError(_('Mismatch between selected Vendor and Sourcing for [{}]{}'.format(rec.product_id.default_code,rec.product_id.name)))
                else:
                    raise UserError(_('Missing Vendor Sourcing for [{}]{}'.format(rec.product_id.default_code,rec.product_id.name)))


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    @api.onchange('product_id')
    def _onchange_product_sourcing(self):
        for rec in self:
            if rec.product_id.product_sourcing == True:
                vendor_price_list = self.env['product.supplierinfo'].search([('product_tmpl_id','=',rec.product_id.product_tmpl_id.id)])
                if len(vendor_price_list):
                    vendor_list = vendor_price_list.filtered(lambda line: line.name == rec.requisition_id.vendor_id)
                    if vendor_list.name != rec.requisition_id.vendor_id:
                        raise UserError(_('Mismatch between selected Vendor and Sourcing for [{}]{}'.format(rec.product_id.default_code,rec.product_id.name)))
                else:
                    raise UserError(_('Missing Vendor Sourcing for [{}]{}'.format(rec.product_id.default_code,rec.product_id.name)))

