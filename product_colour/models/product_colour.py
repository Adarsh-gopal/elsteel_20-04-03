# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class ProductColourSale(models.Model):
    _inherit = 'sale.order.line'

    product_colour = fields.Char(string="Description 2",readonly=False)
    net_weight = fields.Float(string="Net Weight",related="product_id.product_tmpl_id.weight",readonly=True,store=True)
    gross_weight = fields.Float(string="Gross Weight",compute='_compute_gross_weight_sale_line',store=True)

    @api.depends('product_uom_qty','net_weight')
    def _compute_gross_weight_sale_line(self):
        for rec in self:
            if rec.net_weight and rec.product_uom_qty:
                rec.gross_weight = rec.net_weight * rec.product_uom_qty
            else:
                rec.gross_weight = 0.0

    @api.onchange('product_id')
    def _onchange_product_colour(self):
        for rec in self:
            rec.product_colour = rec.product_id.product_tmpl_id.item_group.name



class ProductColourPickingOperation(models.Model):
    _inherit = 'stock.move'

    product_colour = fields.Char(string="Description 2")
    net_weight = fields.Float(string="Net Weight",related="product_id.product_tmpl_id.weight",readonly=True,store=True)
    gross_weight = fields.Float(string="Gross Weight",compute='_compute_gross_weight_stock_move',store=True)

    @api.depends('product_uom_qty','net_weight')
    def _compute_gross_weight_stock_move(self):
        for rec in self:
            if rec.net_weight and rec.product_uom_qty:
                rec.gross_weight = rec.net_weight * rec.product_uom_qty
            else:
                rec.gross_weight = 0.0


    @api.model
    def create(self,vals):
        sale_order_line = self.env['sale.order.line'].browse(vals.get('sale_line_id'))
        vals.update({
            'product_colour' : sale_order_line.product_colour
            })
        res = super(ProductColourPickingOperation, self).create(vals)
        
        return res


class ProductColourDetailOperation(models.Model):
    _inherit = 'stock.move.line'

    product_colour = fields.Char(string="Description 2",related='move_id.product_colour')
    net_weight = fields.Float(string="Net Weight",related="product_id.product_tmpl_id.weight",readonly=True,store=True)
    gross_weight = fields.Float(string="Gross Weight",compute='_compute_gross_weight_stock_move_line',store=True)

    @api.depends('qty_done','net_weight')
    def _compute_gross_weight_stock_move_line(self):
        for rec in self:
            if rec.net_weight and rec.qty_done:
                rec.gross_weight = rec.net_weight * rec.qty_done
            else:
                rec.gross_weight = 0.0



class ProductColourProduction(models.Model):
    _inherit = 'mrp.production'

    product_colour = fields.Char(string="Description 2")
    net_weight = fields.Float(string="Net Weight",related="product_id.product_tmpl_id.weight",readonly=True,store=True)
    gross_weight = fields.Float(string="Gross Weight",compute='_compute_gross_weight_production',store=True)

    @api.depends('product_qty','net_weight')
    def _compute_gross_weight_production(self):
        for rec in self:
            if rec.net_weight and rec.product_qty:
                rec.gross_weight = rec.net_weight * rec.product_qty
            else:
                rec.gross_weight = 0.0

    # @api.depends('origin')
    # def _compute_product_colour(self):
    #     for rec in self:
    #         if rec.origin:
    #             mo = rec.env['mrp.production'].search([('name','=',rec.origin)])
    #             if mo:
    #                 rec.product_colour = mo.product_colour
    #             else:
    #                 rec.product_colour = rec.product_id.product_tmpl_id.item_group.name
    #         else:
    #             rec.product_colour = False

    @api.model
    def create(self,vals):
        res = super(ProductColourProduction,self).create(vals)
        if len(res.move_dest_ids) < 2:
            res.product_colour = res.move_dest_ids.product_colour
            if not res.product_colour:
                mo = self.env['mrp.production'].search([('name','=',res.origin)])
                if mo:
                    res.product_colour = mo.product_colour
                else:
                    res.product_colour = False
        return res


class ProductColourWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    product_colour = fields.Char(string="Description 2",related='production_id.product_colour')
    net_weight = fields.Float(string="Net Weight",related="product_id.product_tmpl_id.weight",readonly=True,store=True)
    gross_weight = fields.Float(string="Gross Weight",compute='_compute_gross_weight_production_workorder',store=True)

    @api.depends('total_workorder_demand','net_weight')
    def _compute_gross_weight_production_workorder(self):
        for rec in self:
            if rec.net_weight and rec.total_workorder_demand:
                rec.gross_weight = rec.net_weight * rec.total_workorder_demand
            else:
                rec.gross_weight = 0.0
