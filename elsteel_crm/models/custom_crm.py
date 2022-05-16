# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class CrmLead2opportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    @api.model
    def default_get(self, fields):
        res = super(CrmLead2opportunityPartner, self).default_get(fields)
        res.update({'action': 'create','name':'convert'})
        return res


    
class LeadPartner(models.Model):
    _name = 'crm.lead.customer.line'
    _description = "Lead Customer Line"

    name = fields.Char(index=True)
    title = fields.Many2one('res.partner.title')
    function = fields.Char(string='Job Position')
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    lead_customer = fields.Many2one('crm.lead')

class CRMLead(models.Model):
    _inherit =  "crm.lead"

    lead_type = fields.Selection([('primary', 'Primary'),('secondary', 'Secondary'),],"Lead Type",default='primary')
    distributer_id = fields.Many2one('res.partner',string="Route Through Distributor")
    customer_group_id = fields.Many2one('partner.category',related="partner_id.z_partner_category",string="Customer Group",readonly=False,store=True)
    state = fields.Selection([('new','New'),('redirect','Redirected')], default='new',compute='_compute_state_crm')

    lead_child_ids = fields.One2many('crm.lead.customer.line','lead_customer')
    
    
    def project_type_quotation_request(self):
        return{
            'name' : _('Project Type Wizard'),
            'res_model' : 'lead.project.type.quotation.wizard',
            'type' : 'ir.actions.act_window',
            'view_mode' : 'form',
            'view_type' : 'form',
            'view_id' : self.env.ref("elsteel_crm.lead_project_type_quotation_wizard_form").id,
            'context' : self._context,
            'target' : 'new',
        }

    def _handle_partner_assignment(self, force_partner_id=False, create_missing=True):
        """ Update customer (partner_id) of leads. Purpose is to set the same
        partner on most leads; either through a newly created partner either
        through a given partner_id.

        :param int force_partner_id: if set, update all leads to that customer;
        :param create_missing: for leads without customer, create a new one
          based on lead information;
        """
        # for lead in self:
        #     if force_partner_id:
        #         lead.partner_id = force_partner_id
        #     if not lead.partner_id and create_missing:
        #         partner = lead._create_customer()
        #         lead.partner_id = partner.id
        lead_customer = self.env['res.partner'].create({
            'name' : self.partner_name,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'website': self.website,
            'company_type' : 'company',
            'z_partner_category': self.customer_group_id.id,
            'child_ids' : [(6, 0, self._generate_chiled_lead_customer().ids)],
            'company_id':self.company_id.id,
            
            })
        if lead_customer.child_ids:
            self.partner_id = lead_customer.child_ids[0]
        else:
            self.partner_id = lead_customer
            

    
    def _generate_chiled_lead_customer(self):
        lead_child = []
        for rec in self.lead_child_ids:
            lead_child.append({
                'name' : rec.name,
                'title' : rec.title.id,
                'function' : rec.function,
                'type' : 'contact', 
                'email': rec.email,
                'phone': rec.phone,
                'mobile': rec.mobile,
                'company_id':self.company_id.id,
            })

        lead_child_ids = self.env['res.partner'].create(lead_child)
        return lead_child_ids


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
