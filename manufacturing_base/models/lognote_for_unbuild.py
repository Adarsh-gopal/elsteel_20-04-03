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




class LogMrpProduction(models.Model):
    """ Manufacturing Orders """
    _name = 'mrp.unbuild'
   
    _inherit = ['mrp.unbuild','mail.thread', 'mail.activity.mixin']

   
    

    product_id = fields.Many2one(
        'product.product', 'Product', check_company=True,
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        required=True,tracking=True, states={'done': [('readonly', True)]})
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        domain="""[
        '|',
            ('product_id', '=', product_id),
            '&',
                ('product_tmpl_id.product_variant_ids', '=', product_id),
                ('product_id','=',False),
        ('type', '=', 'normal'),
        '|',
            ('company_id', '=', company_id),
            ('company_id', '=', False)
        ]
    """,
        states={'done': [('readonly', True)]},tracking=True, check_company=True)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        required=True,tracking=True, states={'done': [('readonly', True)]})

    analytic_account = fields.Many2one('account.analytic.account', string="Analytic Account" , tracking=True )
    analytic_tags = fields.Many2many('account.analytic.tag', string="Analytic Tags" ,tracking=True )

    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,tracking=True,
        required=True, states={'done': [('readonly', True)]}, help="Location where the product you want to unbuild is.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,tracking=True,
        required=True, states={'done': [('readonly', True)]}, help="Location where you want to send the components resulting from the unbuild order.")

    