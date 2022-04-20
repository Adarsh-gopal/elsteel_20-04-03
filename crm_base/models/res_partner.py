# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_a_quothation_customer = fields.Boolean()

    # # quation customer can be only one created on(09-07-2020)
    # @api.onchange('is_a_quothation_customer')
    # def on_change_is_a_quothation_customer(self):
    #     if self.is_a_quothation_customer:
    #         if True in self.env['res.partner'].search([]).mapped('is_a_quothation_customer'):
    #             raise ValidationError(("""You can only have one Quotation Customer"""))


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # def action_confirm(self):
    #     if self.partner_id.is_a_quothation_customer:
    #         raise ValidationError(_("""Please select an actual customer to Confirm the quotation"""))
    #     return super(SaleOrder, self).action_confirm()

   # added the crm.lead model fields data to sale.order model  below to payment_term_id(09-07-2020)
    rel_company_name = fields.Char(string="Customer Name",related='opportunity_id.partner_name')
    rel_contact_name = fields.Char(string="Contact Name",related='opportunity_id.contact_name')
    lead_no = fields.Char(string="Lead No",compute='get_lead_no',store=True)


    @api.depends("opportunity_id")
    def get_lead_no(self):
        for each_lead in self:
            if each_lead.opportunity_id:
                each_lead.lead_no= each_lead.opportunity_id.sequence_name
            else:
                each_lead.lead_no =False

    @api.onchange("opportunity_id")
    def _onchange_opportunity_id(self):
        if self.opportunity_id.crm_product_line_ids:
            order_lines =[]
            for rec in self.opportunity_id.crm_product_line_ids:
                vals = ({
                    # 'order_id' : False,
                    'name' : "[{}]{}".format(rec.cust_product_id.default_code,rec.cust_product_id.name),
                    # 'customer_lead' : False,
                    # 'display_type' : False,
                    'product_uom' : rec.cust_product_id.uom_po_id.id,
                    'product_id' :rec.cust_product_id.id,
                    'product_uom_qty' : rec.cust_qty,
                    'price_unit' : rec.cust_price,
                    })
                order_line = self.env['sale.order.line'].create(vals)
                order_lines.append(order_line.id)            
            self.order_line = [(6, 0, order_lines)]
        else:
            self.order_line = False

   