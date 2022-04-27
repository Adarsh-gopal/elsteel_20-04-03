# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# class CountryState(models.Model):
#     _inherit = 'res.country.state'

#     gst_code = fields.Char()

class Partner(models.Model):
    _inherit = 'res.partner'

    is_indian_company = fields.Boolean(compute="check_company_id")
    pan_no = fields.Char(string="PAN No",size=10,compute='_get_pan_no',store=True,inverse='_set_pan_no')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)

    @api.depends('company_id')
    def check_company_id(self):
        for rec in self:
            if self.company_id.country_id.name == 'India':
                rec.is_indian_company = True
            else:
                rec.is_indian_company = False


    @api.constrains('pan_no')
    def _check_pan_number(self):
        for rec in self:
            if rec.pan_no and len(rec.pan_no) != 10:
                raise ValidationError(_("The PAN number must be 10 character alphanumeric value"))
        return True

    # to set the limit of pan no
    @api.depends('vat')
    def _get_pan_no(self):
        for r in self:
            if r.vat:
                r.pan_no = r.vat[2:13]

    # pan num to editable
    def _set_pan_no(self):
        for r in self:
            r.pan_no = r.pan_no
            
    @api.onchange('vat','state_id')
    def validate_vat(self):
        if self.state_id.country_id.id == 104 and self.vat:
            vat = self.vat
            sc = self.env['res.country.state'].search([('id','=',self.state_id.id)]).l10n_in_tin
            if vat[:2] != sc:
                raise ValidationError(_("Invalid GST Number"))

class CountryStateTin(models.Model):
    _inherit = 'res.country.state'

    l10n_in_tin = fields.Char('TIN Number', size=2, help="TIN number-first two digits")

    