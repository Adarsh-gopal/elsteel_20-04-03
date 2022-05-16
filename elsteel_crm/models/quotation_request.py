# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

QUOTATION_STEP_STATES = [
    ('draft', "Draft"),
    ('inprogress', "In Progress"),
    ('negotiation',"Negotiation"),
    ('pending', "Pending"),
    ('reject', "Rejected"),
    ('done',"Completed"),
    ('cancel',"Cancelled"),
]



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
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Quotation Request"
    _order = "id desc"

    state = fields.Selection(QUOTATION_STEP_STATES)
    name = fields.Char(default=lambda self: _('New'))
    project_name = fields.Char(string="Project Name")
    partner_id = fields.Many2one('res.partner', string='Customer',domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    # Address fields
    street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True)
    state_id = fields.Many2one("res.country.state", string='State',compute='_compute_partner_address_values', readonly=False, store=True,domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country',compute='_compute_partner_address_values', readonly=False, store=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    email = fields.Char()
    phone = fields.Char()   

    #General Information
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user,tracking=True)
    team_id = fields.Many2one('crm.team', string='Sales Team', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",compute='_compute_team_id', ondelete="set null", readonly=False, store=True,tracking=True)
    
    quotation_category_id = fields.Many2one('quotation.category',string="Quotation Category",tracking=True)
    company_currency_id = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    
    pricelist_id = fields.Many2one('product.pricelist', string='Price Level',readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    value = fields.Float(string="Value")
    revision_number = fields.Integer(string="Revision No.",readonly=True,tracking=True)
    
    documentation_req_1 = fields.Many2many(
        comodel_name='ir.attachment',
        relation='m2m_ir_documentation_req_1_rel')
    
    comments = fields.Text(string="Comments")
    
    #Project Details
    project_assigned_id = fields.Many2one('res.users',string="Assigned To")
    date_deadline = fields.Date(string="Deadline")
    product_type_ids = fields.One2many('quotation.product.type','product_types_id',string="Product Type")
    quotation_req_1 = fields.Many2many(
        comodel_name='ir.attachment',
        relation='m2m_ir_quotation_req_1_rel')

    #ORDER INFORMATION
    sale_order_ids = fields.Many2many('sale.order',string="Sales Order No.")

    #Special Enclosure
    spe_encl_designation = fields.Char(string="Special Enclosure Designation")
    spe_encl_request_1 = fields.Many2many(
        comodel_name='ir.attachment',
        relation='m2m_ir_spe_encl_request_1_rel')
    special_encl_assigned_id = fields.Many2one('res.users',string="Assigned To")

    cust_confirmation_drawing_id = fields.Many2many(comodel_name='ir.attachment',relation='m2m_ir_request_cust_confirmation_drawing_rel', string="Customer Confirmation Drawing")
    cust_confirmation_id = fields.Many2many(comodel_name='ir.attachment',relation='m2m_ir_request_cust_confirmation_rel', string="Customer Confirmation")
    cust_conf_assigned_id = fields.Many2one('res.users',string="Assigned To")
    cust_conf_date_deadline = fields.Date(string="Deadline")
    
    production_documentation = fields.Boolean(string='Production Documentation')
    production_date_deadline = fields.Date(string="Deadline")
    dwg_update_note = fields.Char(string="DWG Update Note No.")
    bom_update_note = fields.Char(string="BOM Update Note No.")

    def action_send_quotation_request(self):
        return {}

    @api.model
    def create(self, vals):
       if vals.get('reference_no', _('New')) == _('New'):
           vals['name'] = self.env['ir.sequence'].next_by_code('crm.quotation.request') or _('New')
       res = super(CrmQuotationRequest, self).create(vals)
       return res

    
    @api.depends('user_id')
    def _compute_team_id(self):
        for request in self:
            if not request.user_id:
                continue
            user = request.user_id
            if request.team_id and user in (request.team_id.member_ids | request.team_id.user_id):
                continue
            # team = self.env['crm.team']._get_default_team_id(user_id=user.id, domain=team_domain)
            request.team_id = user.team_id


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

