
from odoo import models, fields,api
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchasrOrderReport(models.Model):

    _inherit='purchase.order'

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super().fields_view_get(view_id, view_type, toolbar, submenu)
    #     if toolbar and 'print' in res['toolbar']:
    #         for record in res['toolbar'].get('print'):
    #             if record.get('name') == 'ELSTEEL Import PO':
    #                 inde_el = res['toolbar'].get('print').index(record)
    #                 res['toolbar'].get('print').pop(inde_el)
    #     return res


    def get_taxes(self):    
        # gst_lit= []
        hsn_list =[]
        for line in self.order_line:
            hsn_list.append(line.product_id.l10n_in_hsn_code)
        hsn_list = list(set(hsn_list))


        taxes = []
        for each_line in self.order_line:
            if each_line.product_id:
		        # pdb.set_trace()
                #curr_val = each_line.price_unit * each_line.quantity
                curr_val = each_line.price_subtotal
                tot_rax_rate =0.0
                igst_val =0.0

                sgst_rate =0.0
                sgst_val = 0.0

                cgst_rate = 0.0
                cgst_val =0.0

                tcs_rate =0.0
                tcs_val =0.0
                group =''
		        # cgst_val = 0.0
                for each_tax in each_line.taxes_id:
                    if each_tax.amount_type == 'group':
                        if each_tax.tax_group_id.name == 'GST':
                            for each_group_line in  each_tax.children_tax_ids:
                                group = each_tax.tax_group_id.name
                                if each_group_line.tax_group_id.name == 'SGST' or each_group_line.tax_group_id.name == 'CGST' :
                                    tot_rax_rate +=round(each_group_line.amount,2)
                                    sgst_val =round(curr_val * (each_group_line.amount/100),2)
                                elif each_group_line.tax_group_id.name == 'TCS':
                                    tcs_rate = each_group_line.amount
                                    tcs_val = round((curr_val+sgst_val*2) * (each_group_line.amount/100),2)

                        elif each_tax.tax_group_id.name == 'IGST':
                            for each_group_line in  each_tax.children_tax_ids:
                                group = each_tax.tax_group_id.name
                                if each_group_line.tax_group_id.name != 'TCS':
                                    tot_rax_rate  += round(each_tax.amount,2)
                                    igst_val =round(curr_val * (each_tax.amount/100),2)
                                elif each_group_line.tax_group_id.name == 'TCS':
                                    tcs_rate = each_group_line.amount
                                    tcs_val = round((curr_val+igst_val) * (each_group_line.amount/100),2)
                    else:
                        group = each_tax.tax_group_id.name
                        tot_rax_rate +=round(each_tax.amount,2)
                        igst_val =round(curr_val * (each_tax.amount/100),2)

                taxes.append({'hsn':each_line.product_id.l10n_in_hsn_code,'tax':each_line.taxes_id,'tax_rate':tot_rax_rate,'igst':igst_val,'sgst':sgst_val,'tcs':tcs_val,'tcs_rate':tcs_rate, 'tax_group':group})


        sorted_tax =[]
        for line in hsn_list:
            tot_rax_rate =0.0
            igst_val =0.0
            sgst_val =0.0
            tcs_val =0.0
            tcs_rate =0.0
            group =''
            tax_id = None

            for each_rec in taxes:
                if line == each_rec['hsn']:
                    tot_rax_rate = each_rec['tax_rate']
                    tcs_rate = each_rec['tcs_rate']
                    igst_val+=each_rec['igst']
                    sgst_val+=each_rec['sgst']
                    tcs_val+=each_rec['tcs']
                    group=each_rec['tax_group']
                    tax_id = each_rec['tax'].id
                else:
                    # tot_rax_rate = each_rec['tax_rate']
                    # igst_val = each_rec['igst']
                    # sgst_val = each_rec['sgst']
                    # tcs_val = each_rec['tcs']
                    # group = each_rec['tax_group']
                    continue

            sorted_tax.append({'hsn':line,'tax':tax_id,'tax_rate':tot_rax_rate,'igst':igst_val,'sgst':sgst_val,'tcs':tcs_val,'tcs_rate':tcs_rate,'tax_group':group})
        print(sorted_tax,'********************')
        return sorted_tax


