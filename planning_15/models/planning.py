# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError



class PixgenPurchase(models.Model):
	_inherit = 'purchase.order'


	@api.model
	def create(self, vals):
		res = super(PixgenPurchase, self).create(vals)
		if res.group_id.sale_id:
			route_ids = res.group_id.sale_id.order_line.mapped('route_id')
			buy_route_id = route_ids.rule_ids.filtered(lambda line: line.action == 'buy')
			if buy_route_id and buy_route_id.vendor_id:
				res.partner_id = buy_route_id.vendor_id.id
			
		return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    vendor_id = fields.Many2one('res.partner',string="Vendors")
