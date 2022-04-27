from odoo import models, fields, api, _
import itertools


class MrpReport(models.Model):
    _inherit = 'mrp.report'

    product_category_id = fields.Many2one('product.category',string="Product Category",related='product_id.categ_id',store=True)

    def _select(self):
        select_str = """
            SELECT
                min(mo.id)             AS id,
                mo.id                  AS production_id,
                mo.company_id          AS company_id,
                mo.date_finished       AS date_finished,
                mo.product_id          AS product_id,
                mo.product_category_id AS product_category_id,
                prod_qty.product_qty   AS qty_produced,
                comp_cost.total * currency_table.rate                                                                                   AS component_cost,
                op_cost.total * currency_table.rate                                                                                     AS operation_cost,
                (comp_cost.total + op_cost.total) * currency_table.rate                                                                 AS total_cost,
                op_cost.total_duration                                                                                                  AS duration,
                comp_cost.total * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate                    AS unit_component_cost,
                op_cost.total * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate                      AS unit_operation_cost,
                (comp_cost.total + op_cost.total) * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate  AS unit_cost,
                op_cost.total_duration / prod_qty.product_qty                                                                           AS unit_duration,
                (comp_cost.total + op_cost.total) * cost_share.byproduct_cost_share * currency_table.rate                               AS byproduct_cost
        """

        return select_str


class Operation(models.Model):
    _inherit = 'mrp.routing.workcenter'

    is_master = fields.Boolean()

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_category_id = fields.Many2one('product.category',string="Product Category",related='product_id.categ_id',store=True)
    item_group = fields.Many2one('item.group')
    product_group_1 = fields.Many2one('product.group.1')
    product_group_2 = fields.Many2one('product.group.2')
    product_group_3 = fields.Many2one('product.group.3')

    @api.onchange('product_id')
    def Onchange_product(self):
        for l in self:
            l.item_group = l.product_id.product_tmpl_id.item_group.id
            l.product_group_1 = l.product_id.product_tmpl_id.product_group_1.id
            l.product_group_2 = l.product_id.product_tmpl_id.product_group_2.id
            l.product_group_3 = l.product_id.product_tmpl_id.product_group_3.id


class StockMove(models.Model):
    _inherit = 'stock.move'

    # serial_no = fields.Char(string='#',compute="_compute_sl")

    # @api.depends('production_id')
    # def _compute_sl(self):
    #     if self.production_id:
    #         for order in self.mapped('production_id'):
    #             number=1
    #             for line in order.move_raw_ids:
    #                 if line.product_id:
    #                     line.serial_no = str(number)
    #                     number += 1
    #                 else:
    #                     line.serial_no= str(number)
    #     else:
    #         self.serial_no= str(1)

    #     self.env['mrp.production'].browse(self._context.get('params').get('id'))



    serial_no = fields.Char(string='#',compute="_compute_sl")

    @api.depends('product_id')
    def _compute_sl(self):
        var = 1
        for rec in self:
            if rec.serial_no == False:
                rec.serial_no = ord(chr(var + int(rec.serial_no)))
                var += 1
            else:
                rec.serial_no = int(False)