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
    _name = 'mrp.production'
    _description = 'Production Order'
   
    _inherit = ['mrp.production','mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_date_planned_start(self):
        if self.env.context.get('default_date_deadline'):
            return fields.Datetime.to_datetime(self.env.context.get('default_date_deadline'))
        return datetime.datetime.now()

    

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account', copy=True,
        help="Analytic account in which cost and revenue entries will take\
        place for financial management of the manufacturing order.",
        compute='_compute_analytic_account_id', store=True, readonly=False,tracking=True)

   
    product_id = fields.Many2one(
            'product.product', 'Product',
            domain="""[
                ('type', 'in', ['product', 'consu']),
                '|',
                    ('company_id', '=', False),
                    ('company_id', '=', company_id)
            ]
            """,
            readonly=True, required=True, check_company=True,tracking=True,
            states={'draft': [('readonly', False)]})

    product_qty = fields.Float(
        'Quantity To Produce',
        default=1.0, digits='Product Unit of Measure',tracking=True,
        readonly=True, required=True, 
        states={'draft': [('readonly', False)]})
    qty_producing = fields.Float(string="Quantity Producing", digits='Product Unit of Measure', copy=False,tracking=True)

    date_planned_start = fields.Datetime(
            'Scheduled Date', copy=False, default=_get_default_date_planned_start,
            help="Date at which you plan to start the production.",
            index=True, required=True,tracking=True)
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        readonly=True, states={'draft': [('readonly', False)]},
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
        check_company=True,tracking=True,
        help="Bill of Materials allow you to define the list of required components to make a finished product.")
   

    # @api.onchange('move_raw_ids')
    # def log_for_line(self):
    #     print(1222222222222222222222222222222222222222222222222)
    #     for line in self.move_raw_ids:
    #         print(line.quantity_done,1111111111111111111111111111111111)
    #         if line:
    #             message = "Quantity Changes"
    #             line.message_post(body=message)

    
