# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class CRMEnclosure(models.Model):

    _inherit =  "crm.lead"

    crm_project_type = fields.Selection([('standard','Standard'),('enclosure','Special Enclosure')],string="Project Type",default='standard')
    standard = fields.Char(string='Standard')
    special_enclosure = fields.Char()
    name = fields.Char()
    sequence_name = fields.Char("Lead No",readonly=True)
    enclosure_designation = fields.Char(string = 'Special Enclosure Designation')
    assigned_to = fields.Many2one('res.users', string = 'Assigned To')
    drawing_update_no = fields.Char(string = 'Drawing Update Number')
    bom_update_no =  fields.Char(string = 'BOM Update Number')
    doc_deadline = fields.Datetime(string = 'Document Deadline')
    se_qr_no = fields.Char(string = 'SE QR Number')
    se_qr_deadline = fields.Char(string = 'SE QR Deadline')
    se_qr_rev_no = fields.Char(string = 'SE QR Revision Number')
    se_qt_status = fields.Many2one('crm.enclosure.stage',string="SE QR Status")
    se_req_received = fields.Selection([('p','Pending'),('ip','In Progree'),('rj','Rejected'),('cm','Completed'),('ng','Negotiation'),('cl','Cancelled')],string="SE Request Received")
    se_cust_drawing_sent = fields.Selection([('p','Pending'),('ip','In Progree'),('rj','Rejected'),('cm','Completed'),('ng','Negotiation'),('cl','Cancelled')],string="SE Customer Confirmation Drawing Sent")
    po_received = fields.Selection([('r','Recieved'),('l','Lost'),('pr','Price'),('ck','Cheeck')],string="Purchase order Received")
    spcl_encls_button = fields.Boolean(string="Spcl Encl Button")

    
    def spcl_encls_button_method(self):
        for rec in self:
            rec.spcl_encls_button = True
            # self.env['spcl.enclosure'].create({

            # })
            


    def action_spcl_enclosure_function(self):
        return {
        'res_model':'spcl.enclosure',
        'type':'ir.actions.act_window',
        'view_mode': 'form',
        'view_type': 'form',
        'view_id': self.env.ref("elsteel_crm_enclosure.view_special_enclosure_form").id,
        'context' : dict(self._context,default_name=self.name,default_enclosure_designation=self.enclosure_designation,
            default_sequence_name=self.sequence_name,default_lead_id_new = self.id),
        'target':self
        }

    




