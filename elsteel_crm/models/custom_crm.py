# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class CRMLead(models.Model):
    _inherit =  "crm.lead"

    lead_type = fields.Selection([('primary', 'Primary'),('secondary', 'Secondary'),],"Lead Type",default='primary')
    distributer_id = fields.Many2one('res.partner',string="Route Through Distributor")
    customer_group_id = fields.Many2one('partner.category',related="partner_id.z_partner_category",string="Customer Group",readonly=False)
    state = fields.Selection([('new','New'),('redirect','Redirected')], default='new',compute='_compute_state_crm')

    
    
    def write(self,vals):
        for rec in self:
            if vals.get('lead_type') == 'primary':
                vals['state'] = 'new'
        res = super(CRMLead,self).write(vals)
        return res

    # @api.depends('distributer_id')
    def _compute_state_crm(self):
      if self.distributer_id and self.lead_type =='secondary':
          self.state ='redirect'
      else:
          self.state = 'new'

    
    @api.constrains('lead_type')
    def check_item_group_code(self):
        for rec in self:
            if self.lead_type == 'secondary' and self.type == 'opportunity':
                raise ValidationError(_("""Warning!!! :Allowed for Primary Lead Type Only"""))


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    def action_apply(self):
        if self.lead_id.lead_type == 'secondary':
            raise ValidationError(_(""" Warning!!!!: Cannot Convert a Secondary lead type to opportunity"""))
        res = super().action_apply()
        return res
