# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class LeadProjectTypeQuatationWizard(models.TransientModel):
    _name = 'lead.project.type.quotation.wizard'
    _description = 'Project Type Wizard'

    crm_project_type = fields.Selection([('standard','Standard'),('enclosure','Special Enclosure')],string="Project Type",default='standard')
    project_name = fields.Char(string="Project Name")
    lead_id = fields.Many2one('crm.lead')

    def button_action_project_type(self):
        for wizard in self:
            vals = {
                'project_name' : self.project_name,
                'request_project_type' : self.crm_project_type,
                'lead_id' : self.lead_id.id,
                'partner_id' : self.lead_id.partner_id.id,
                'user_id' : self.lead_id.user_id.id,
                'team_id' : self.lead_id.team_id.id,
            }
            self.env['crm.quotation.request'].create(vals)
        
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


class QuotationProductTypeValues(models.Model):
    _name = 'quotation.product.type.values'
    _description = 'Product Type Values'

    name = fields.Char()