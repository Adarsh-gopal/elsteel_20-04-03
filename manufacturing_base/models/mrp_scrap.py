from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpScrap(models.Model):
    _inherit = 'stock.scrap'


    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    
    @api.model
    def create(self,vals):
        production = self.env['mrp.production'].search([('id','=',vals.get('production_id'))])
        if production.analytic_account_id:
            vals['analytic_account_id'] = production.analytic_account_id.id
        if production.analytic_tag_ids:
            vals['analytic_account_id'] = [(6, 0, production.analytic_tag_ids.ids)]

        res = super(MrpScrap,self).create(vals)

        return res
