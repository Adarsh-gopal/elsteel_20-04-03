# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import SUPERUSER_ID, _, api, fields, models



class PickingType(models.Model):
    _name = "stock.picking.type"
    _inherit = ['stock.picking.type','mail.thread', 'mail.activity.mixin']
    
    def _default_show_operations(self):
        return self.user_has_groups('stock.group_production_lot,'
                                    'stock.group_stock_multi_locations,'
                                    'stock.group_tracking_lot')
    name = fields.Char('Operation Type', required=True, translate=True,tracking=True)
    sequence_code = fields.Char('Code', required=True,tracking=True)
    sequence_id = fields.Many2one(
        'ir.sequence', 'Reference Sequence',
        check_company=True, copy=False,tracking=True)
    default_location_src_id = fields.Many2one(
        'stock.location', 'Default Source Location',
        check_company=True,tracking=True,
        help="This is the default source location when you create a picking manually with this operation type. It is possible however to change it or that the routes put another location. If it is empty, it will check for the supplier location on the partner. ")
    default_location_dest_id = fields.Many2one(
        'stock.location', 'Default Destination Location',
        check_company=True,tracking=True,
        help="This is the default destination location when you create a picking manually with this operation type. It is possible however to change it or that the routes put another location. If it is empty, it will check for the customer location on the partner. ")
    code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer')], 'Type of Operation', required=True,tracking=True)
    code = fields.Selection(selection_add=[('mrp_operation', 'Manufacturing')], tracking=True, ondelete={'mrp_operation': 'cascade'})
    use_create_lots = fields.Boolean(
        'Create New Lots/Serial Numbers', default=True,
        help="If this is checked only, it will suppose you want to create new Lots/Serial Numbers, so you can provide them in a text field. ",tracking=True)
    use_existing_lots = fields.Boolean(
        'Use Existing Lots/Serial Numbers', default=True,
        help="If this is checked, you will be able to choose the Lots/Serial Numbers. You can also decide to not put lots in this operation type.  This means it will create stock with no lot or not put a restriction on the lot taken. ",tracking=True)
    return_picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type for Returns',
        check_company=True,tracking=True)
    show_operations = fields.Boolean(
        'Show Detailed Operations',default=_default_show_operations,
        help="If this checkbox is ticked, the pickings lines will represent detailed stock operations. If not, the picking lines will represent an aggregate of detailed stock operations.",tracking=True)
    show_reserved = fields.Boolean(
        'Pre-fill Detailed Operations', default=True,
        help="If this checkbox is ticked, Odoo will automatically pre-fill the detailed "
        "operations with the corresponding products, locations and lot/serial numbers.",tracking=True)
    reservation_method = fields.Selection(
        [('at_confirm', 'At Confirmation'), ('manual', 'Manually'), ('by_date', 'Before scheduled date')],
        'Reservation Method', required=True, default='at_confirm',
        help="How products in transfers of this operation type should be reserved.",tracking=True)