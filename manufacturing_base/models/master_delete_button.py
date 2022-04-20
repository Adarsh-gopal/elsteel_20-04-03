# -*- coding: utf-8 -*-

from odoo import models, api, fields,_

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    active = fields.Boolean(default=True)

