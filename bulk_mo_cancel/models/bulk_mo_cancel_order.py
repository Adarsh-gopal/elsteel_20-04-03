# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_bulk_mo_cancel(self):
        for mo in self:
            if mo.state != 'cancel':
                mo.write({'state':'cancel'})