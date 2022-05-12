from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError



class CurrencyMasterMessagePost(models.Model):
    _inherit = 'custom.currency.master'

    def write(self, vals):
        if vals.get('currency_line_ids'):
            new_list = []
            for list1 in vals.get('currency_line_ids'):
                if list1[-1] != False:
                    new_list.append(list1)

            component_lines_ids = self.currency_line_ids.filtered(lambda x:x.id in [value[1] for value in new_list])
            new_dist = []
            for dicts in component_lines_ids:
                for newval in new_list:
                    if newval[1] == dicts.id:
                        new_dist.append('{}({}--->{})'.format(dicts.currency_id.name,dicts.inverse_company_rate,newval[-1].get('inverse_company_rate')))
            if new_dist:
                msg = ', '.join(dic for dic in new_dist)
                self.message_post(body=msg)
        res = super(CurrencyMasterMessagePost,self).write(vals)
        return res
