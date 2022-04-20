	# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    customer_title=fields.Many2one('res.partner.title')

    sequence_name = fields.Char("Lead No",readonly=True)

    @api.model
    def create(self,vals):
        if vals.get('sequence_name', _('New')) == _('New'):
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('crm.leads') or _('New')
        res = super(crm_lead, self).create(vals)
        return res


    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        # set default value in context, if not already set (Put stage to 'new' stage)
        context = dict(self._context)
        context.setdefault('default_type', self.type)
        context.setdefault('default_team_id', self.team_id.id)
        # Set date_open to today if it is an opp
        default = default or {}
        default['date_open'] = fields.Datetime.now() if self.type == 'opportunity' else False
        # Do not assign to an archived user
        if not self.user_id.active:
            default['user_id'] = False

        default['sequence_name'] = self.env['ir.sequence'].next_by_code('crm.leads') or _('New')
        return super(crm_lead, self.with_context(context)).copy(default=default)

    # def name_get(self):
    #     names = []
    #     for lead in self:
    #         names.append((lead.id,lead.sequence_name if lead.sequence_name else ''))
    #     return names

    # def action_new_quotation(self):
    #     res = super(crm_lead, self).action_new_quotation()

    #     action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")       
    #     order_lines =[]
    #     for rec in self.crm_product_line_ids:
    #         vals = ({
    #             'order_id' : False,
    #             'name' : rec.cust_product_id.name,
    #             'customer_lead' : False,
    #             'display_type' : False,
    #             'product_uom' : rec.cust_product_id.uom_po_id.id,
    #             'product_id' :rec.cust_product_id.id,
    #             'product_uom_qty' : rec.cust_qty,
    #             'price_unit' : rec.cust_price,
    #             'company_id' : rec.company_currency.id,
    #             })
    #         order_line = self.env['sale.order.line'].create(vals)
    #         order_lines.append(order_line.id)
        
    #         print(order_lines,1111111111111111111111111111111111)
    #     import pdb;
    #     pdb.set_trace()
    #     self.env.context = dict(self.env.context)
    #     self.env.context.update({'default_order_line': order_lines})
    #     print(self.env.context,"self.env.context")
    #     # import pdb;
    #     # pdb.set_trace()
    #     # print(action['context'])
    #     # action['context'] = ({
    #     #     'default_opportunity_id' : self.id,
    #     #     'default_order_line' : [(6, 0, order_lines)]
    #     # })
        
    #     return action

    


class Crmleadcreateopportunity(models.Model):
    _inherit = 'crm.lead2opportunity.partner'

    _name='crm.creatsequencenumber'
    _description = 'crm.creatsequencenumber'
    

    def action_merge(self):
        self.ensure_one()
        merge_opportunity = self.opportunity_ids.merge_opportunity(self.user_id.id, self.team_id.id)
        if self.sequence_name:
            values['sequence_name'] = self.sequence_name

        # The newly created lead might be a lead or an opp: redirect toward the right view
        if merge_opportunity.type == 'opportunity':
            return merge_opportunity.redirect_opportunity_view()
        else:
            return merge_opportunity.redirect_lead_view()




    def action_apply(self):
        """ Convert lead to opportunity or merge lead and opportunity and open
            the freshly created opportunity view.
        """
        self.ensure_one()
        values = {
            'team_id': self.team_id.id,
        }

        if self.partner_id:
            values['partner_id'] = self.partner_id.id

        if self.sequence_name:
            values['sequence_name'] = self.sequence_name

        if self.name == 'merge':
            leads = self.with_context(active_test=False).opportunity_ids.merge_opportunity()
            if not leads.active:
                leads.write({'active': True, 'activity_type_id': False, 'lost_reason': False})
            if leads.type == "lead":
                values.update({'lead_ids': leads.ids, 'user_ids': [self.user_id.id]})
                self.with_context(active_ids=leads.ids)._convert_opportunity(values)
            elif not self._context.get('no_force_assignation') or not leads.user_id:
                values['user_id'] = self.user_id.id
                leads.write(values)
        else:
            leads = self.env['crm.lead'].browse(self._context.get('active_ids', []))
            values.update({'lead_ids': leads.ids, 'user_ids': [self.user_id.id]})
            self._convert_opportunity(values)

        sequence_name = self.env['crm.lead'].browse(values.get('sequence_name'))

        return leads[0].redirect_opportunity_view()




