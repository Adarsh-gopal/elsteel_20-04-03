
from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError
import pdb


class LostReasonEnclosure(models.TransientModel):
    _name =  "lost.reason.enclosure"

    lost_reason = fields.Char(string="Reason For Lost")


    def confirm_reason(self):
        print(self._context)
        # pdb.set_trace()
        # {'lang': 'en_US', 'tz': 'Asia/Calcutta', 'uid': 2, 'allowed_company_ids': [1], 
        # 'params': {'id': 8, 'menu_id': 266, 'cids': 1, 'action': 385, 'model': 'crm.lead', 'view_type': 'form'}, 
        # 'active_model': 'spcl.enclosure', 'active_id': 7, 'active_ids': [7]}