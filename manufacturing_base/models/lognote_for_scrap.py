import json
import datetime
import math
import re
import warnings

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import OrderedSet, format_date

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES



class LogForScrap(models.Model):
    """ Manufacturing Orders """
    _name = 'stock.scrap'
   
    _inherit = ['stock.scrap','mail.thread', 'mail.activity.mixin']

    def _get_default_scrap_location_id(self):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        return self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [company_id, False])], limit=1).id

    def _get_default_location_id(self):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None
   
    

   
    origin = fields.Char(string='Source Document',tracking=True)
    product_id = fields.Many2one(
        'product.product', 'Product', domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        required=True, states={'done': [('readonly', True)]},tracking=True, check_company=True)
    
    scrap_qty = fields.Float('Quantity', default=1.0, required=True,tracking=True, states={'done': [('readonly', True)]}, digits='Product Unit of Measure')
    location_id = fields.Many2one(
        'stock.location', 'Source Location',tracking=True, domain="[('usage', '=', 'internal'), ('company_id', 'in', [company_id, False])]",
        required=True, states={'done': [('readonly', True)]}, default=_get_default_location_id, check_company=True)
    
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', tracking=True,default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True), ('company_id', 'in', [company_id, False])]", required=True, states={'done': [('readonly', True)]}, check_company=True)
    