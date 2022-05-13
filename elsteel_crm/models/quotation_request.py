# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


PARTNER_ADDRESS_FIELDS_TO_SYNC = [
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'country_id',
]

class CrmQuotationRequest(models.Model):
    _name = 'crm.quotation.request'
    _description = "Quotation Request"
    _order = "id desc"

    name = fields.Char()
    project_name = fields.Text(string="Project Name")
    partner_id = fields.Many2one('res.partner', string='Customer',domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    # Address fields
    street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True)
    state_id = fields.Many2one("res.country.state", string='State',compute='_compute_partner_address_values', readonly=False, store=True,domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country',compute='_compute_partner_address_values', readonly=False, store=True)
    company_id = fields.Many2one('res.company')
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()    

    #General Information
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    # team_id = fields.Many2one('crm.team', string='Sales Team', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",compute='_compute_team_id', ondelete="set null", readonly=False, store=True)
    

    
    revision_number = fields.Integer(string="Revision No.")

    # @api.depends('user_id')
    # def _compute_team_id(self):
    #     for lead in self:
    #         if not lead.user_id:
    #             continue
    #         user = lead.user_id
    #         if lead.team_id and user in (lead.team_id.member_ids | lead.team_id.user_id):
    #             continue
    #         team_domain = [('use_leads', '=', True)] if lead.type == 'lead' else [('use_opportunities', '=', True)]
    #         team = self.env['crm.team']._get_default_team_id(user_id=user.id, domain=team_domain)
    #         lead.team_id = team.id


    @api.depends('partner_id')
    def _compute_partner_address_values(self):
        for request in self:
            request.update(request._prepare_address_values_from_partner(request.partner_id))


    def _prepare_address_values_from_partner(self, partner):
        if any(partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC):
            values = {f: partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values = {f: self[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        return values
