# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import datetime
import math
import re

from ast import literal_eval
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES



class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    def action_split(self):
        self._pre_action_split_merge_hook(split=True)
        if len(self) > 1:
            productions = [Command.create({'production_id': production.id}) for production in self]
            # Wizard need a real id to have buttons enable in the view
            wizard = self.env['mrp.production.split.multi'].create({'production_ids': productions})
            action = self.env['ir.actions.actions']._for_xml_id('split_manufacturing.action_mrp_production_split_multi')
            action['res_id'] = wizard.id
            return action
        else:
            action = self.env['ir.actions.actions']._for_xml_id('split_manufacturing.action_mrp_production_split')
            action['context'] = {
                'default_production_id': self.id,
            }
            return action

    def _pre_action_split_merge_hook(self, merge=False, split=False):
            if not merge and not split:
                return True
            ope_str = merge and 'merge' or 'split'
            if any(production.state not in ('draft', 'confirmed') for production in self):
                raise UserError(_("Only manufacturing orders in either a draft or confirmed state can be %s.", ope_str))
            if any(not production.bom_id for production in self):
                raise UserError(_("Only manufacturing orders with a Bill of Materials can be %s.", ope_str))
            if split:
                return True

            if len(self) < 2:
                raise UserError(_("You need at least two production orders to merge them."))
            products = set([(production.product_id, production.bom_id) for production in self])
            if len(products) > 1:
                raise UserError(_('You can only merge manufacturing orders of identical products with same BoM.'))
            additional_raw_ids = self.mapped("move_raw_ids").filtered(lambda move: not move.bom_line_id)
            additional_byproduct_ids = self.mapped('move_byproduct_ids').filtered(lambda move: not move.byproduct_id)
            if additional_raw_ids or additional_byproduct_ids:
                raise UserError(_("You can only merge manufacturing orders with no additional components or by-products."))
            if len(set(self.mapped('state'))) > 1:
                raise UserError(_("You can only merge manufacturing with the same state."))
            if len(set(self.mapped('picking_type_id'))) > 1:
                raise UserError(_('You can only merge manufacturing with the same operation type'))
            # TODO explode and check no quantity has been edited
            return True