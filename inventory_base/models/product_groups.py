# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    code = fields.Char('Short Name', required=True, size=10, help="Short name used to identify your warehouse")

class ItemGroup(models.Model):
    _name = "item.group"
    _description = "Item Group"
    # _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    name = fields.Char()
    code = fields.Char()
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    active = fields.Boolean(default=True)

    @api.constrains('code','company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['item.group'].search([('code','=',rec.code),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""code already exists!"""))



class ProductGroup1(models.Model):
    _name = "product.group.1"
    _description = "Product Group 1"
    # _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    name = fields.Char()
    code = fields.Char()
    product_category_id = fields.Many2one('product.category')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    active = fields.Boolean(default=True)

    @api.constrains('code','company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['product.group.1'].search([('code','=',rec.code),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""code already exists!"""))


class ProductGroup2(models.Model):
    _name = "product.group.2"
    _description = "Product Group 2"
    # _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    name = fields.Char()
    code = fields.Char()
    product_group_1 = fields.Many2one('product.group.1')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    active = fields.Boolean(default=True)

    @api.constrains('code','company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['product.group.2'].search([('code','=',rec.code),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""code already exists!"""))


class ProductGroup3(models.Model):
    _name = "product.group.3"
    _description = "Product Group 3"
    # _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    name = fields.Char()
    code = fields.Char()
    product_group_2 = fields.Many2one('product.group.2')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    active = fields.Boolean(default=True)
    
    @api.constrains('code','company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['product.group.3'].search([('code','=',rec.code),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""code already exists!"""))



class ProductTemplate(models.Model):
    _inherit = "product.template"

    item_group = fields.Many2one('item.group', ondelete='restrict')
    product_group_1 = fields.Many2one('product.group.1', domain="[('product_category_id', '=', categ_id)]", ondelete='restrict')
    product_group_2 = fields.Many2one('product.group.2', domain="[('product_group_1', '=', product_group_1)]", ondelete='restrict')
    product_group_3 = fields.Many2one('product.group.3', domain="[('product_group_2', '=', product_group_2)]", ondelete='restrict')


class ProductProduct(models.Model):
    _inherit = "product.product"

    item_group = fields.Many2one(related='product_tmpl_id.item_group', store=True)
    product_group_1 = fields.Many2one(related='product_tmpl_id.product_group_1',store=True)
    product_group_2 = fields.Many2one(related='product_tmpl_id.product_group_2',store=True)
    product_group_3 = fields.Many2one(related='product_tmpl_id.product_group_3',store=True)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    product_category_id = fields.Many2one('product.category',related='product_id.product_tmpl_id.categ_id', store=True)
    item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.item_group', store=True)
    product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.product_group_1',store=True)
    product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.product_group_2',store=True)
    product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.product_group_3',store=True)


class StockMove(models.Model):
    _inherit = "stock.move"

    product_category_id = fields.Many2one('product.category',related='product_id.product_tmpl_id.categ_id', store=True)
    item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.item_group', store=True)
    product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.product_group_1',store=True)
    product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.product_group_2',store=True)
    product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.product_group_3',store=True)


class StockMove(models.Model):
    _inherit = "stock.move.line"

    product_category_id = fields.Many2one('product.category',related='product_id.product_tmpl_id.categ_id', store=True)
    item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.item_group', store=True)
    product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.product_group_1',store=True)
    product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.product_group_2',store=True)
    product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.product_group_3',store=True)