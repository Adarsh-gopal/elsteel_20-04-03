from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleorderNumber(models.Model):
    _inherit = 'mrp.workorder'
    
    so_order_id = fields.Many2one("sale.order", string = "SO Number", compute ="get_sale_order",store=True)
    customer_id = fields.Many2one("res.partner", string = "Customer Name", compute ="get_sale_order",store=True)

    @api.depends('production_id.so_origin')
    def get_sale_order(self):
        for each in self:
            if each.production_id:
                order_number = self.env['sale.order'].search([('name', '=', each.production_id.so_origin)])
                if len(order_number) == 1:
                    each.so_order_id=order_number.id
                    each.customer_id=order_number.partner_id.id
                elif len(order_number) >1:
                    each.so_order_id=order_number[0].id
                    each.customer_id=order_number[0].partner_id.id

                else:
                    each.so_order_id=None
                    each.customer_id= None
            else:
                each.customer_id= None
                each.so_order_id=None




   