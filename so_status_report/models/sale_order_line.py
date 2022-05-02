from odoo import fields,models,api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # z_po_order_date = fields.Datetime(related="order_id.date_order",string="Date Order")
    z_status = fields.Char('Document Status',store=True,compute='_compute_status_type')
    z_currency_id = fields.Many2one('res.currency',' Currency',related="order_id.currency_id")
    z_partner_id = fields.Many2one('res.partner',' Partner',related="order_id.partner_id")
    z_remaining_qty = fields.Float("Pending Qty",compute="qty_remaining",store=True)
    z_client_order_ref = fields.Char('Customer Reference',related="order_id.client_order_ref")
    z_pending_order_value = fields.Float(compute='compute_value',string='Pending Order Value',store=True)
    product_catag_id=fields.Many2one('product.category',related="product_id.categ_id",store=True)
    # open_close_so = fields.Selection([('open_so', 'OPEN SO'), ('close_so', 'CLOSE SO'), ], 'SO Status', related="order_id.open_close_mo", store=True)
    c_order_date = fields.Datetime(related="order_id.date_order", string="Order confirm Date",store=True)
    product_group_1 = fields.Many2one('product.group.1',string="Product Group 1")
    product_group_2 = fields.Many2one('product.group.2',string="Product Group 2")
    product_group_3 = fields.Many2one('product.group.3',string="Product Group 3")
    item_group = fields.Many2one('item.group')
    
    @api.onchange('product_id')
    def onchange_product_id_group(self):
        for rec in self:
            if rec.product_id:
                rec.item_group = rec.product_id.product_tmpl_id.item_group.id
                rec.product_group_1 = rec.product_id.product_tmpl_id.product_group_1.id
                rec.product_group_2 = rec.product_id.product_tmpl_id.product_group_2.id
                rec.product_group_3 = rec.product_id.product_tmpl_id.product_group_3.id
                
    @api.depends('qty_delivered','product_uom_qty')
    def qty_remaining(self):
        for each in self:
            if each.product_uom_qty :
                each.z_remaining_qty = each.product_uom_qty- each.qty_delivered
            else:
                each.z_remaining_qty = 0.0

    @api.depends('z_remaining_qty','price_unit')
    def compute_value(self):
        for l in self:
            l.z_pending_order_value = l.price_unit * l.z_remaining_qty

    @api.depends('qty_delivered','qty_invoiced','product_uom_qty')
    def _compute_status_type(self):
    	for line in self:
            if line.qty_delivered != line.product_uom_qty:
                line.z_status = 'Pending Order'
            if line.qty_delivered != line.qty_invoiced:
                line.z_status = 'Pending for Invoice'
            if line.state == 'cancel':
                line.z_status = 'Cancel'
            if line.qty_delivered == line.product_uom_qty == line.qty_invoiced:
                line.z_status = "Fully Invoiced"
                
                
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def update_sol_groups(self):
        for so in self:
            for line in so.order_line:
                line.onchange_product_id_group()

