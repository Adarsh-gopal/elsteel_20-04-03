# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"
    
    code = fields.Selection([('incoming', 'Receipt'), ('incoming_return', 'Purchase Return'), ('outgoing', 'Delivery'), ('outgoing_return', 'Sale Return'), 
                             ('internal', 'Internal Transfer'),('production', 'Production'),('consumption', 'Consumption'),
                             ('positive_adjustment', 'Positive Adjustment'),('negative_adjustment', 'Negative Adjustment')], string='Type of Transaction')
    
    @api.model
    def create(self, vals_list):
        res = super(StockValuationLayer, self).create(vals_list)
        if res.stock_move_id and res.stock_move_id.location_id and res.stock_move_id.location_id.usage and res.stock_move_id.location_dest_id and res.stock_move_id.location_dest_id.usage:
            if res.stock_move_id.location_id.usage == 'supplier' and res.stock_move_id.location_dest_id.usage == 'internal':
                res.code = 'incoming'
            elif res.stock_move_id.location_id.usage == 'internal' and res.stock_move_id.location_dest_id.usage == 'supplier':
                res.code = 'incoming_return'
            elif res.stock_move_id.location_id.usage == 'internal' and res.stock_move_id.location_dest_id.usage == 'customer':
                res.code = 'outgoing'
            elif res.stock_move_id.location_id.usage == 'customer' and res.stock_move_id.location_dest_id.usage == 'internal':
                res.code = 'outgoing_return'
            elif res.stock_move_id.location_id.usage == 'production' and res.stock_move_id.location_dest_id.usage == 'internal':
                res.code = 'production'
            elif res.stock_move_id.location_id.usage == 'internal' and res.stock_move_id.location_dest_id.usage == 'production':
                res.code = 'consumption'
            elif res.stock_move_id.location_id.usage == 'internal' and res.stock_move_id.location_dest_id.usage == 'internal':
                res.code = 'internal'
            elif res.stock_move_id.location_id.usage == 'inventory' and res.stock_move_id.location_dest_id.usage == 'internal':
                res.code = 'positive_adjustment'
            elif res.stock_move_id.location_id.usage == 'internal' and res.stock_move_id.location_dest_id.usage == 'inventory':
                res.code = 'negative_adjustment'
        return res
    
    def update_operation_type(self):
        for rec in self:
            if rec.stock_move_id and rec.stock_move_id.location_id and rec.stock_move_id.location_id.usage and rec.stock_move_id.location_dest_id and rec.stock_move_id.location_dest_id.usage:
                if rec.stock_move_id.location_id.usage == 'supplier' and rec.stock_move_id.location_dest_id.usage == 'internal':
                    rec.code = 'incoming'
                elif rec.stock_move_id.location_id.usage == 'internal' and rec.stock_move_id.location_dest_id.usage == 'supplier':
                    rec.code = 'incoming_return'
                elif rec.stock_move_id.location_id.usage == 'internal' and rec.stock_move_id.location_dest_id.usage == 'customer':
                    rec.code = 'outgoing'
                elif rec.stock_move_id.location_id.usage == 'customer' and rec.stock_move_id.location_dest_id.usage == 'internal':
                    rec.code = 'outgoing_return'
                elif rec.stock_move_id.location_id.usage == 'production' and rec.stock_move_id.location_dest_id.usage == 'internal':
                    rec.code = 'production'
                elif rec.stock_move_id.location_id.usage == 'internal' and rec.stock_move_id.location_dest_id.usage == 'production':
                    rec.code = 'consumption'
                elif rec.stock_move_id.location_id.usage == 'internal' and rec.stock_move_id.location_dest_id.usage == 'internal':
                    rec.code = 'internal'
                elif rec.stock_move_id.location_id.usage == 'inventory' and rec.stock_move_id.location_dest_id.usage == 'internal':
                    rec.code = 'positive_adjustment'
                elif rec.stock_move_id.location_id.usage == 'internal' and rec.stock_move_id.location_dest_id.usage == 'inventory':
                    rec.code = 'negative_adjustment'

    

