from odoo import fields,models,api, _
from datetime import datetime

class ProductMaster(models.Model):
    _inherit="res.company"

    planning_worksheet = fields.Boolean(string="Plannig Worksheet")