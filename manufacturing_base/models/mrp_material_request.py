from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpMaterialRequest(models.Model):
    _inherit = 'mrp.production'

    def mrp_materal_request_action(self):
        mr_ids = self.filtered(lambda mr:mr.state in ('confirmed','to_close','progress'))
        if len(mr_ids):
            mr_lines = self.env['material.request.line']

            mr_lines = [(0, 0, {
                'product_id' : mrp_line.product_id.id,
                'planned_qty' : mrp_line.product_uom_qty - mrp_line.reserved_availability,
                'source_id' : mrp_line.raw_material_production_id.id,
                'picking_type_id' : False,
                'source_location_id' : False,
                'dest_location_id' : False,
                'request_type' : 'stock'
            }) for mrp_line in mr_ids.mapped('move_raw_ids').filtered(lambda move: move.reserved_availability != move.product_uom_qty)]
        
            
            mr_id = self.env['material.request'].create({
                'mrp_ids':[(6, 0, mr_ids.ids)],
                'material_request_line_ids' : mr_lines
                })
            
            
    