# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    @api.constrains('inventory_quantity')
    def inventory_quantity_approval(self):
        if not self.env.user.has_group('inventory_base.group_inventory_adjustment_access'):
            raise UserError(_('You are Not Authorised Person to Update the Quantity'))

class prixgen_stock_picking(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _purchase_lot(self):
        name = self._name
        product_id = self.product_id.id

        if name == 'sale.order.line':
            purchase_lot = self.env['stock.production.lot'].search([('product_id','=',product_id)])
            for product_lot in purchase_lot:
                if product_lot.product_qty>0:
                    product_lot.show_lot=True
                else:
                    product_lot.show_lot=False
        else:
            purchase_lot = self.env['stock.production.lot'].search([('product_id','=',product_id)])
            for product_lot in purchase_lot:
                product_lot.show_lot=True

class prixgen_purchase_stock_picking(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def _purchase_lot(self):
        name = self._name
        product_id = self.product_id.id

        if name == 'purchase.order.line':
            purchase_lot = self.env['stock.production.lot'].search([('product_id','=',product_id)])
            for product_lot in purchase_lot:
                product_lot.show_lot=True



class prixgen_stock_picking_move(models.Model):
    _inherit = 'stock.move.line'

    @api.onchange('product_id')
    def _purchase_lot(self):
        name = self._name
        product_id = self.product_id.id
        
        if name == 'stock.move.line':
            purchase_lot = self.env['stock.production.lot'].search([('product_id','=',product_id)])
            for product_lot in purchase_lot:
                if product_lot.product_qty>0:
                    product_lot.show_lot=True
                else:
                    product_lot.show_lot=False
        else:
            purchase_lot = self.env['stock.production.lot'].search([('product_id','=',product_id)])
            for product_lot in purchase_lot:
                product_lot.show_lot=True

    serial_no = fields.Char(string='#',compute="_compute_sl")

    @api.depends('product_id')
    def _compute_sl(self):
        var = 1
        for rec in self:
            if rec.serial_no == False:
                rec.serial_no = ord(chr(var + int(rec.serial_no)))
                var += 1
            else:
                rec.serial_no = False

    # serial_no = fields.Char(string='#',compute="_compute_sl")

    # @api.depends('product_id')
    # def _compute_sl(self):
    #     var = 1
    #     for rec in self:
    #         if rec.serial_no == False:
    #             rec.serial_no = ord(chr(var + int(rec.serial_no)))
    #             var += 1
    #         else:
    #             rec.serial_no = int(False)


class StockProductionLot(models.Model):
    _inherit="stock.production.lot"

    show_lot=fields.Boolean('Show Lot',default=False)

class StockMove(models.Model):
    _inherit = 'stock.move'

    serial_no = fields.Char(string='#',compute="_compute_sl")

    @api.depends('product_id')
    def _compute_sl(self):
        var = 1
        for rec in self:
            if rec.serial_no == False:
                rec.serial_no = ord(chr(var + int(rec.serial_no)))
                var += 1
            else:
                rec.serial_no = False

