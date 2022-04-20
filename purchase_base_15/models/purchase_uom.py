from odoo import models, fields, api, _
import itertools

class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    product_uom_category_id = fields.Many2one(related='product_tmpl_id.uom_po_id.category_id')
    uom_product = fields.Many2one('uom.uom',string="Purchase UOM")
    active = fields.Boolean(default=True)
    # product_uom = fields.Many2one('uom.uom',related=False)



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

   
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine,self).onchange_product_id()
        for line in self:
            if line.order_id.partner_id:
                prod_tmp_id = self.env['product.template'].search([('id','=',line.product_id.product_tmpl_id.id)])
                vendor_info = self.env['product.supplierinfo'].search([('name','=',line.order_id.partner_id.id),('product_tmpl_id','=',prod_tmp_id.id)],limit=1, order='id desc')
                if vendor_info:
                    line.product_uom = vendor_info.uom_product
                else:
                    line.product_uom = line.product_id.uom_id or line.product_id.uom_po_id
            