# -*- coding: utf-8 -*-

from odoo import models, api, fields,_

class CRMTAGACTIVE(models.Model):
    _inherit = 'crm.tag'

    active = fields.Boolean(default=True)

