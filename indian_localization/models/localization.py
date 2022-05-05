from odoo import models, fields, api, _,exceptions

class ResCompany(models.Model):
    _inherit = "res.company"

    tan_no = fields.Char(string="T.A.N.No")
    factory_number = fields.Char(string= "Factories Act. Regd. No.")
    company_status = fields.Selection([
                                        ('Pulic',"Public Limited Co."),
                                        ('private',"Private Limited Co."),
                                        ('other',"Others"),
                                        ('gov',"Goverment"),
                                        ('inv_pro',"Individual/Proprietary"),
                                        ('reg',"Register Trust"),
                                        ('partnership',"Partnership"),
                                        ('society',"Society/Co-op Society")],string="Company Status")
    msme_code = fields.Char(string="MSME Code")


    is_indian_company = fields.Boolean()
        

    @api.onchange('country_id')
    def check_company_id(self):
        for rec in self:
            if self.country_id.name == 'India':
                rec.is_indian_company = True
            else:
                rec.is_indian_company = False
