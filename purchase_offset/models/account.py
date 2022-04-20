# -*- coding: utf-8 -*-

from odoo import models, fields, api
import pdb

class ProductCategory(models.Model):
    _inherit = "product.category"

    purchase_account_id = fields.Many2one('account.account')
    purchase_offset_account_id = fields.Many2one('account.account')

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for rec in self:
            if rec.move_type in ('in_invoice','in_refund'):
                for line in rec.line_ids.filtered(lambda line: line.product_id.id != False and not line.tax_line_id.id and line.product_id.categ_id.purchase_account_id.id and line.product_id.categ_id.purchase_offset_account_id.id):
                    # print("\n\n{}\n\n".format(line.product_id.id))
                    amt = line.move_id.currency_id._convert(line.price_subtotal, line.move_id.company_currency_id, line.move_id.company_id, line.move_id.date)
                    rec.line_ids = [(0, 0, {
                        'account_id': line.product_id.categ_id.purchase_account_id.id,
                        'name': line.name,
                        'debit': amt if rec.move_type == 'in_invoice' else 0,
                        'credit': amt if rec.move_type == 'in_refund' else 0,
                        'exclude_from_invoice_tab':True,
                        'purchase_offset_line':True
                    }),(0, 0, {
                        'account_id': line.product_id.categ_id.purchase_offset_account_id.id,
                        'name': line.name,
                        'debit': amt if rec.move_type == 'in_refund' else 0,
                        'credit': amt if rec.move_type == 'in_invoice' else 0,
                        'exclude_from_invoice_tab':True,
                        'purchase_offset_line':True
                    })]
        return super(AccountMove, self).action_post()
    
    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        offset_lines = tuple(self.line_ids.filtered(lambda x: x.purchase_offset_line == True).ids)
        query = """DELETE FROM account_move_line WHERE id in {}""".format(offset_lines)
        # print('\n\n',query,'\n\n')
        if offset_lines:
            self.env.cr.execute(query)

        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_offset_line = fields.Boolean()
