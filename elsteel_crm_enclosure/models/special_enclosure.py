# -*- coding: utf-8 -*-

from psutil import swap_memory
from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError
from itertools import cycle
import pdb


class SpecialEnclosure(models.Model):

    _name =  "spcl.enclosure"
    _inherit = ['mail.thread', 'mail.activity.mixin',]
    _rec_name = "name"

    def _get_default_stage(self):
        return self.env['crm.enclosure.stage'].search([], limit=1)

    enclosure_stage_approve_bool = fields.Boolean(related="enclosure_stage_id.approve_bool")

    req_num =fields.Char(string= "Request Number",default=lambda self: self.env['ir.sequence'].next_by_code('req.num.sequence'),index=True,readonly=True)
    se_qr_name = fields.Char(string="SE QR Number", readonly=True, required=True, copy=False, default = "New")
    lead_id_new = fields.Many2one('crm.lead')
    contact_name = fields.Char('Contact Name', related = 'lead_id_new.contact_name')
    name = fields.Char()
    sequence_name = fields.Char("Lead No", related = 'lead_id_new.sequence_name')
    probability = fields.Float(related = 'lead_id_new.probability')
    email_from = fields.Char(related = 'lead_id_new.email_from')
    phone =fields.Char(related = 'lead_id_new.phone')
    city =fields.Char(related = 'lead_id_new.city')
    state_id =fields.Many2one("res.country.state", related = 'lead_id_new.state_id')
    country_id =fields.Many2one("res.country",related = 'lead_id_new.country_id')
    user_id =fields.Many2one("res.users",related = 'lead_id_new.user_id',string ="Quotation Team")
    partner_id =fields.Many2one('res.partner',related = 'lead_id_new.partner_id')
    company_id =fields.Many2one('res.company',related = 'lead_id_new.company_id')
    team_id =fields.Many2one('crm.team',related = 'lead_id_new.team_id',string="Project Team")
    se_qr_no =fields.Char(related = 'lead_id_new.se_qr_no')
    enclosure_designation =fields.Char(related = 'lead_id_new.enclosure_designation')
    project_team_assignee =fields.Many2one('res.users' , string='Project Team Assigned To')
    quotation_team_assignee =fields.Many2one('res.users' , string='Quotation Team Assigned To')
    drawing_update_no =fields.Char(related = 'lead_id_new.drawing_update_no')
    expected_revenue =fields.Monetary(currency_field='company_currency',related = 'lead_id_new.expected_revenue')
    prorated_revenue =fields.Monetary(currency_field='company_currency',related = 'lead_id_new.prorated_revenue')
    recurring_revenue =fields.Monetary(currency_field='company_currency',related = 'lead_id_new.recurring_revenue')
    recurring_plan =fields.Many2one('crm.recurring.plan',related = 'lead_id_new.recurring_plan')
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    cust_confirmation_drawing = fields.Many2many(
        comodel_name='ir.attachment',
        relation='m2m_ir_cust_confirmation_drawing_rel', string="Customer Confirmation Drawing")
    cust_confirmation = fields.Many2many(
        comodel_name='ir.attachment',
        relation='m2m_ir_cust_confirmation_rel', string="Customer Confirmation")
    spcl_encl_req_1 = fields.Many2many(
        comodel_name='ir.attachment',
        relation='m2m_ir_spcl_encl_req_2_rel')
    spcl_encl_req_2 = fields.Many2many(
        comodel_name='ir.attachment',
        relation='m2m_ir_spcl_encl_req_2_rel')
        
    spcl_encl_req_3 = fields.Many2many(
        comodel_name='ir.attachment',
        relation='m2m_ir_spcl_encl_req_3_rel')
        
    pdt_dcmntn = fields.Selection([('dwg','DWG Update Note No'),('bom','BOM Update No')],string="Product Documenation")
    deadline = fields.Datetime(string = 'Deadline')
    quotation_deadline = fields.Datetime(string = 'Quotation Request Deadline')
    quotation_submited = fields.Datetime(string = 'Quotation Request Submitted')
    quotation_accepted = fields.Datetime(string = 'Quotation Request Accepted')
    quotation_completed = fields.Datetime(string = 'Quotation Request Completed')
    quotation_request_cust = fields.Datetime(string = 'Quotation Request Sent to Customer')
    drawing_cust = fields.Datetime(string = 'Drawing Sent to Customer')
    drawing_confirm = fields.Datetime(string = 'Drawing Confirmation')
    lost_reason = fields.Char(string = 'Lost Reason')
    request_no = fields.Char(string = 'Request No')
    enclosure_stage_id = fields.Many2one('crm.enclosure.stage', string='Enclosure Stage',default=_get_default_stage)
    bom_update_no = fields.Char(string="BOM Update Number")
    approval_one= fields.Selection(selection=[
            ('1', 'Approved'),
            ('2', 'Reject')],string='Approval-1',readonly=1,copy=False)
    approval_two= fields.Selection(selection=[
            ('1', 'Approved'),
            ('2', 'Reject')],string='Approval-2',readonly=1,copy=False)
    
    approval_line_ids = fields.One2many('spcl.enclosure.line','line_id')










    def action_update_opportunity(self):
        return {}

    def action_send_quotation_request(self):
        return {}

    def action_approval(self):
        approval_ids = self.enclosure_stage_id
        
        for line in self.approval_line_ids:
            line.approval_b = True
            # print("YEssssssssssssssssssssssssss","\n"*25)

        if approval_ids:
            for each in approval_ids.approval_lines:
                if self.env.user.id in each.user_ids.ids:
                    if each.approval_one:
                        user_approve = 1
                    elif each.approval_two:
                        user_approve = 2
                    # elif each.approval_three:
                    #     user_approve = 3
                    # approval_level =int(each.requisition_id.approval_method)
                    if not self.approval_one:
                        if each.approval_one:
                            self.approval_one = '1'
                            msg = """
                            <div style="color:green;">Level I Approved-%s</div>
                            """
                            self.message_post(body=msg)
                            break
                    elif not self.approval_two:
                        if each.approval_two:
                            self.approval_two = '1'
                            msg = """
                            <div style="color:green;">Level I Approved-%s</div>
                            """
                            self.message_post(body=msg)
                    else:
                        raise UserError (_("You can't approve the order Twice"))
                elif not self.approval_one:
                    raise UserError (_("Pending for Approval"))
                elif self.approval_one and not each.approval_one:
                    raise UserError (_("You can't approve the order Twice"))
        else:
            raise UserError (_("You can't approve the order"))

        
        

        # if (self.requisition_id.current_approvall ==1 and self.approval_one =='1') or (self.requisition_id.current_approvall ==2 and self.approval_two =='1') or (self.requisition_id.current_approvall ==3 and self.approval_three =='1'):
        #     self.write({'state': 'approved'})
        # else:
        #     self.write({'state': 'to_approve'})

    def action_lost(self):
        print(self.lead_id_new,"qqqqqqqqqqqqqqqqqqqqqqqqq",self.lead_id_new.contact_name)
        
        return {
        'name': _('Lost Reason Wizard'),
        'res_model':'lost.reason.enclosure',
        'type':'ir.actions.act_window',
        'view_mode': 'form',
        'view_type': 'form',
        # 'target': 'current',
        'view_id': self.env.ref("elsteel_crm_enclosure.view_lost_reason_enclosure_form").id,
        'context' : self.id,
        'target':'new'
        }

    # def action_view_opportunity_sources(self):
    #     self.ensure_one()
    #     mrp_production_ids = self.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.mrp_production_ids.ids
    #     action = {
    #         'res_model': 'mrp.production',
    #         'type': 'ir.actions.act_window',
    #     }
    #     if len(mrp_production_ids) == 1:
    #         action.update({
    #             'view_mode': 'form',
    #             'res_id': mrp_production_ids[0],
    #         })
    #     else:
    #         action.update({
    #             'name': _("MO Generated by %s") % self.name,
    #             'domain': [('id', 'in', mrp_production_ids)],
    #             'view_mode': 'tree,form',
    #         })
    #     return action

    # def load_approvals(self):
    #      if self.enclosure_stage_id.approve_bool:
    #         self.approval_line_ids = [(2,id) for id in self.approval_line_ids.ids]
    #         self.approval_line_ids = [(0,0,{'stage_approval_line_id':id}) for id in self.enclosure_stage_id.approval_lines.ids]
        

    def move_to_next_stage(self):
        curr_index = []
        self.enclosure_stage_id = self.env['crm.enclosure.stage'].search([('sequence','=',self.enclosure_stage_id.sequence+1)]).id
        # self.load_approvals()
        if self.enclosure_stage_id.approve_bool:
            self.approval_line_ids = [(2,id) for id in self.approval_line_ids.ids]
            self.approval_line_ids = [(0,0,{'stage_approval_line_id':id}) for id in self.enclosure_stage_id.approval_lines.ids]
        
                        

    @api.model
    def create(self, vals): 
        if vals.get('se_qr_name', 'New') == 'New':
            vals['se_qr_name'] = self.env['ir.sequence'].next_by_code('spcl.enclosure') or 'New'
        result = super(SpecialEnclosure, self).create(vals)
        return result
    
class approvalSuppmodel(models.Model):
    _name = 'spcl.enclosure.line'

    line_id = fields.Many2one('spcl.enclosure', string="Line ID")
    stage_approval_line_id = fields.Many2one('enclosure.approval.line')
    user_id = fields.Many2many('res.users', string="User's", related='stage_approval_line_id.user_ids')
    # bool_app= fields.Boolean("1",related='stage_approval_line_id.approval_one')
    approval_b = fields.Boolean("Approved")





    

