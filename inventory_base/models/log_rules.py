import calendar
from collections import defaultdict, OrderedDict
from datetime import timedelta
from odoo import _, api, fields, models

class Logrules(models.Model):
    _name = "stock.rule"
    _inherit = ['stock.rule','mail.thread', 'mail.activity.mixin']

    name = fields.Char(string = 'Name', required=True, translate=True, tracking=True,
        help="This field will fill the packing origin and the name of its moves")
    action = fields.Selection(
        selection=[('pull', 'Pull From'), ('push', 'Push To'), ('pull_push', 'Pull & Push')], string='Action',
        required=True,tracking=True)
    action = fields.Selection(selection_add=[
        ('manufacture', 'Manufacture')
    ], ondelete={'manufacture': 'cascade'},tracking=True)
    action = fields.Selection(selection_add=[
        ('buy', 'Buy')
    ], ondelete={'buy': 'cascade'},tracking=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, check_company=True, tracking=True,
        domain="[('code', '=?', picking_type_code_domain)]")
    location_src_id = fields.Many2one('stock.location', 'Source Location', check_company=True, tracking=True)
    location_id = fields.Many2one('stock.location', 'Destination Location', required=True, tracking=True, check_company=True)
    auto = fields.Selection([
        ('manual', 'Manual Operation'),
        ('transparent', 'Automatic No Step Added')], string='Automatic Move',
        default='manual', index=True, required=True, tracking=True,
        help="The 'Manual Operation' value will create a stock move after the current one. "
             "With 'Automatic No Step Added', the location is replaced in the original move.")
    procure_method = fields.Selection([
        ('make_to_stock', 'Take From Stock'),
        ('make_to_order', 'Trigger Another Rule'),
        ('mts_else_mto', 'Take From Stock, if unavailable, Trigger Another Rule')], tracking=True,string='Supply Method', default='make_to_stock', required=True,
        help="Take From Stock: the products will be taken from the available stock of the source location.\n"
             "Trigger Another Rule: the system will try to find a stock rule to bring the products in the source location. The available stock will be ignored.\n"
             "Take From Stock, if Unavailable, Trigger Another Rule: the products will be taken from the available stock of the source location."
             "If there is no stock available, the system will try to find a  rule to bring the products in the source location.")
    

    route_id = fields.Many2one('stock.location.route', 'Route', required=True, ondelete='cascade', tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', check_company=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company,
        domain="[('id', '=?', route_company_id)]", tracking=True)
    sequence = fields.Integer('Sequence', default=20, tracking=True)
    
    group_propagation_option = fields.Selection([
        ('none', 'Leave Empty'),
        ('propagate', 'Propagate'),
        ('fixed', 'Fixed')], string="Propagation of Procurement Group", default='propagate', tracking=True)
    propagate_cancel = fields.Boolean(
        'Cancel Next Move', default=False, tracking=True,
        help="When ticked, if the move created by this rule is cancelled, the next move will be cancelled too.")
    propagate_warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse to Propagate', tracking=True,
        help="The warehouse to propagate on the created move/procurement, which can be different of the warehouse this rule is for (e.g for resupplying rules from another warehouse)")
    group_id = fields.Many2one('procurement.group', 'Fixed Procurement Group', tracking=True)

    partner_address_id = fields.Many2one(
        'res.partner', 'Partner Address',
        check_company=True, tracking=True,
        help="Address where goods should be delivered. Optional.")
    delay = fields.Integer('Lead Time', default=0, tracking=True, help="The expected date of the created transfer will be computed based on this lead time.")