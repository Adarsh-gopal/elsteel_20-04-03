# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import pdb
from odoo.exceptions import AccessError, UserError, ValidationError

class MrpSubMFGMoWiz(models.Model):
    _name = 'mrp.submfg.mo.wiz'
    _description = 'Mrp submfg Mo Wiz'

    mo_id = fields.Many2one('mrp.production')
    quantity = fields.Float(related='mo_id.product_qty')
    submfg_mo_lines = fields.One2many('mrp.submfg.mo.wiz.line','submfg_mo')

    def submfg(self):
        for line in self.submfg_mo_lines:
            sequence = self.env['ir.sequence'].browse(int(self.env['ir.config_parameter'].sudo().get_param('mrpd.submfg_sequence')))
            if sequence:
                name_seq = self.env['ir.sequence'].next_by_code(sequence.code)
                rec = self.mo_id.copy({
                    'name' :name_seq,
                    'product_qty':line.quantity,
                    'date_planned_start':line.scheduled_date,
                    'user_id':line.responsible.id,
                    'submfg_source_id':self.mo_id.id,
                    'origin':self.mo_id.origin,  
                  })
            else:
                rec = self.mo_id.copy({
                    'product_qty':line.quantity,
                    'date_planned_start':line.scheduled_date,
                    'user_id':line.responsible.id,
                    'submfg_source_id':self.mo_id.id,
                    'origin':self.mo_id.origin,  
                  })


            rec._onchange_move_raw()
            rec._onchange_product_qty()
            self.mo_id.product_qty -= line.quantity

        if self.mo_id.state == 'confirmed':

            # submfg button is made visible for confirmed state also.
            # since the standard is goes back to draft state once submfg is called for confirmed state,
            # we are updating the state again once the method is called

            self.mo_id._onchange_move_raw()
            self.mo_id.write({'state': 'confirmed'})

        else:
            self.mo_id._onchange_move_raw()
        self.mo_id._onchange_product_qty()
       
    
   

class MrpSubMFGMoWizLine(models.Model):
    _name = 'mrp.submfg.mo.wiz.line'
    _description = 'Mrp submfg Mo Wiz Line'

    submfg_mo = fields.Many2one('mrp.submfg.mo.wiz')
    quantity = fields.Float()
    scheduled_date = fields.Datetime()
    responsible = fields.Many2one('res.users')

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    submfg_source_id = fields.Many2one('mrp.production',string="SUB MFG Order")
    suborder_mfg_ids = fields.One2many('mrp.production','submfg_source_id')
    suborder_mfg_count = fields.Integer(compute='_count_submfg_order')
    

    @api.depends('suborder_mfg_ids')
    def _count_submfg_order(self):
        for rec in self:
            rec.suborder_mfg_count = len(rec.suborder_mfg_ids)

    def action_view_mo_sub_mfg_order(self):
        tree_view = self.env.ref('mrp.mrp_production_tree_view')
        view_id = self.env.ref('mrp.mrp_production_form_view')
        return {
            'name': _('SUB MFG Orders'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'mrp.production',
            'domain': [('submfg_source_id', '=', self.id)],
            'view_id': view_id.id,
            'views': [(tree_view.id, 'tree'),(view_id.id, 'form')],
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
            }

    def submfg(self):
        if self.workorder_ids:
            for each in self.workorder_ids:
                if each.date_planned_start and each.date_planned_finished:
                    raise UserError(_('Unplan the MO: %s in order to create Sub MFG Order.') % (self.name))

                else:
                    view_id = self.env.ref('sub_manufacturing.mrp_submfg_mo_wiz_view_form')
                    return {
                        'name': _("{}({})".format(self.name,self.product_qty)),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'mrp.submfg.mo.wiz',
                        'context':{'default_mo_id': self.id},
                        'view_id': view_id.id,
                        'views': [(view_id.id, 'form')],
                        'type': 'ir.actions.act_window',
                        'target': 'new'
                        }
        else:
            view_id = self.env.ref('sub_manufacturing.mrp_submfg_mo_wiz_view_form')
            return {
                'name': _("{}({})".format(self.name,self.product_qty)),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mrp.submfg.mo.wiz',
                'context':{'default_mo_id': self.id},
                'view_id': view_id.id,
                'views': [(view_id.id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new'
                }


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    submfg_sequence_id = fields.Many2one('ir.sequence',string='Destribution Sequence')

    def set_values(self):
        super(ResConfigSettings,self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('mrpd.submfg_sequence',self.submfg_sequence_id.id)
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            submfg_sequence_id = int(params.get_param('mrpd.submfg_sequence'))
        )
        return res