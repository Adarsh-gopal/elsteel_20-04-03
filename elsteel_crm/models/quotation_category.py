# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class LeadProjectTypeQuatationWizard(models.TransientModel):
    _name = 'lead.project.type.quotation.wizard'
    _description = 'Project Type Wizard'

    crm_project_type = fields.Selection([('standard','Standard'),('enclosure','Special Enclosure')],string="Project Type",default='standard')

    def button_action_project_type(self):
        pass
        
class QuotationCategory(models.Model):
    _name = 'quotation.category'
    _description = 'Quotation Category'

    name = fields.Char()

    
class QuotationProductType(models.Model):
    _name = 'quotation.product.type'
    _description = 'Product Type'

    product_type_id = fields.Many2one('quotation.product.type.values')
    quantity = fields.Float()
    product_types_id = fields.Many2one('crm.quotation.request')

    @api.onchange('product_type_id')
    def _onchange_Product_type_id(self):
        for rec in self:
            if rec.product_type_id:
                rec.quantity = rec.product_type_id.quantity


class QuotationProductTypeValues(models.Model):
    _name = 'quotation.product.type.values'
    _description = 'Product Type Values'

    name = fields.Char()
    quantity = fields.Float()