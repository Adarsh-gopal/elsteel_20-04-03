# -*- coding: utf-8 -*-

from odoo import models, api, fields,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date

import pdb
class PurchaseRequisitionType(models.Model):
    _inherit = 'purchase.requisition.type'

    sequence_id = fields.Many2one('ir.sequence','Purchase Request Sequence')
    agreement_types = fields.Selection([('purchase_request','Purchase Request'),('blanket_order','Blanket Order'),('other','Other Agreements')],string="Agreement Category")
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    
    
    @api.constrains('agreement_types','company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['purchase.requisition.type'].search([('agreement_types','=','purchase_request'),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""Purchase Request already exists!"""))
            docs1=rec.env['purchase.requisition.type'].search([('agreement_types','=','blanket_order'),('company_id','=',rec.company_id.id)])
            if len(docs1) > 1:
                raise ValidationError(_("""Blanket Order already exists!"""))


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    on_hand_qty_req = fields.Integer("On Hand Quantity")
    name = fields.Char(related='requisition_id.name',string='Reference')
    state = fields.Selection([('to_approve','To Approved'),('approved','Approved'),('refuse','Refuse')],default='to_approve',string="Status")
    required_approvals = fields.Integer(related='requisition_id.current_approvall',string="Required Approvals")
    available_quantity = fields.Float('Available Quantity')
    serial_no = fields.Char(string='#',compute='_compute_sl')


    @api.depends('requisition_id')
    def _compute_sl(self):
        for order in self.mapped('requisition_id'):
            number=1
            for line in order.line_ids:
                if line.product_id:
                    line.serial_no = str(number)
                    number += 1
                else:
                    line.serial_no= str(number)



    @api.onchange('product_id')
    def get_on_hand_qty_req(self):
        self.on_hand_qty_req = self.product_id.free_qty
        self.price_unit = self.product_id.standard_price

        # available_quantity
        stock_quants = self.env['stock.quant'].search([('product_id','=',self.product_id.id)])
        for line in stock_quants:
            if line.location_id == self.requisition_id.picking_type_id.default_location_dest_id:
                self.available_quantity = line.available_quantity

    # def _compute_state_requisition_line(self):
    #     for rec in self:
    #         if (rec.requisition_id.current_approvall ==1 and rec.approval_one =='1') or (rec.requisition_id.current_approvall ==2 and rec.approval_two =='1') or (rec.requisition_id.current_approvall ==3 and rec.approval_three =='1'):
    #             rec.write({'state': 'approved'})
    #         else:
    #             rec.write({'state': 'to_approve'})


    approval_one= fields.Selection(selection=[
            ('1', 'Approved'),
            ('2', 'Reject')],string='Approval-1',readonly=1,copy=False)
    approval_two= fields.Selection(selection=[
            ('1', 'Approved'),
            ('2', 'Reject')],string='Approval-2',readonly=1,copy=False)
    approval_three= fields.Selection(selection=[
            ('1', 'Approved'),
            ('2', 'Reject')],string='Approval-3',readonly=1,copy=False)


   

    def get_approval(self):
        # approval_ids = self.env['requisition.approval'].search([
        #                         ('warehouse_id','=',self.requisition_id.picking_type_id.warehouse_id.id),
        #                         ('document_type_id','=',self.requisition_id.request_type_id.id)])
        approval_ids = self.env['requisition.approval'].search([('document_type_id','=',self.requisition_id.request_type_id.id)])


        if approval_ids:
            for each in approval_ids.approval_lines:
                if self.env.user.id in each.user_ids.ids:
                    if each.approval_one:
                        user_approve = 1
                    elif each.approval_two:
                        user_approve = 2
                    elif each.approval_three:
                        user_approve = 3
                    approval_level =int(each.requisition_id.approval_method)
                    if not self.approval_one:
                        if each.approval_one:
                            self.approval_one = '1'
                            msg = """
                            <div style="color:green;">Level I Approved-%s</div>
                            """%(self.product_id.name)
                            self.requisition_id.message_post(body=msg)
                            break
                    elif not self.approval_two:
                        if each.approval_two:
                            self.approval_two = '1'
                            msg = """
                            <div style="color:green;">Level I Approved-%s</div>
                            """%(self.product_id.name)
                            self.requisition_id.message_post(body=msg)
                    else:
                        raise UserError (_("You can't approve the order Twice"))
                elif not self.approval_one:
                    raise UserError (_("Pending for Approval"))
                elif self.approval_one and not each.approval_one:
                    raise UserError (_("You can't approve the order Twice"))
                    # if user_approve == 1:
                    #     if user_approve == 1 and not self.approval_one:
                    #         self.approval_one = '1'
                    #         msg = """
                    #         <div style="color:green;">Level I Approved-%s</div>
                    #         """%(self.product_id.name)
                    #         self.requisition_id.message_post(body=msg)
                    #     else:
                    #         raise UserError (_("You can't approve the order Twice"))

                    # elif user_approve == 2:
                    #     if not self.approval_one:
                    #         raise UserError (_("You can't approve the order before Approval-1"))
                    #     else:
                    #         if user_approve == 2 and not self.approval_two :
                    #             self.approval_two ='1'
                    #             msg = """
                    #             <div style="color:green;">Level II Approved-%s</div>
                    #             """%(self.product_id.name)
                    #             self.requisition_id.message_post(body=msg)
                    #         else:
                    #             raise UserError (_("You can't approve the order Twice"))
                    # elif user_approve == 3:
                    #     if not self.approval_two:
                    #         raise UserError (_("You can't approve the order before Approval-1I"))
                    #     else:
                    #         if user_approve == 3 and not self.approval_three :
                    #             self.approval_three ='1'
                    #             msg = """
                    #             <div style="color:green;">Level III Approved-%s</div>
                    #             """%(self.product_id.name)
                    #             self.requisition_id.message_post(body=msg)
                    #         else:
                    #             raise UserError (_("You can't approve the order Twice"))
        else:
            raise UserError (_("You can't approve the order Create Requisition Approval"))
        if (self.requisition_id.current_approvall ==1 and self.approval_one =='1') or (self.requisition_id.current_approvall ==2 and self.approval_two =='1') or (self.requisition_id.current_approvall ==3 and self.approval_three =='1'):
            self.write({'state': 'approved'})
        else:
            self.write({'state': 'to_approve'})

        
                        
        
class RequisitionAppproval(models.Model):
    _name = "requisition.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description ="requisition.approval"

    active = fields.Boolean(default=True)
    name = fields.Char("Name",tracking=True)
    document_type_id = fields.Many2one("purchase.requisition.type","Agreement Type",tracking=True)
    warehouse_id = fields.Many2one("stock.warehouse","Warehouse",tracking=True)
    approval_lines = fields.One2many("requisition.approval.line","requisition_id")
    approval_method = fields.Selection(selection=[
            ('1', 'Level-I'),
            ('2', 'Level-II'),
            ('3', 'Level-III'),
            ],tracking=True,string='Approval Level')

    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)

    @api.constrains('name','company_id')
    def check_requisition_approval_name(self):
        for rec in self:
            docs=rec.env['requisition.approval'].search([('name','=',rec.name),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""name already exists!"""))



    @api.onchange("document_type_id")
    def get_name(self):
        if self.document_type_id:
            self.name=self.document_type_id.name

    @api.constrains('document_type_id', 'warehouse_id')
    def _check_duplicate(self):
        existing_id=self.env['requisition.approval'].search([
                                            ('document_type_id','=',self.document_type_id.id),
                                            ("warehouse_id",'=',self.warehouse_id.id),
                                            ])
        if not len(existing_id) ==1:
            raise UserError (_("You Can't create the Purchase Requisition Approval for the same Warehouse and Document Type"))



class RequisitionAppprovalLine(models.Model):
    _name = "requisition.approval.line"
    _description ="requisition.approval.line"

    user_ids = fields.Many2many("res.users",string="Users")
    requisition_id = fields.Many2one("requisition.approval",string="Requisition")
    approval_one= fields.Boolean("1")
    approval_two= fields.Boolean("2")
    approval_three= fields.Boolean("3")
    approval_all= fields.Boolean("Parallel")
    role = fields.Char("Role")



    @api.onchange('approval_all')
    def _update_approval_all(self):
        if self.approval_all:
            self.approval_one = False
            self.approval_two = False
            self.approval_three = False
    @api.onchange('approval_one')
    def _update_approval_one(self):
        if self.approval_one:
            self.approval_two = False
            self.approval_three = False
            self.approval_all = False

    @api.onchange('approval_two')
    def _update_approval_two(self):
        if self.approval_two:
            self.approval_one = False
            self.approval_three = False
            self.approval_all = False

    @api.onchange('approval_three')
    def _update_approval_three(self):
        if self.approval_three:
            self.approval_one = False
            self.approval_two = False
            self.approval_all = False

    


class RequisitionOrderApproval(models.Model):
    _name="requisition.order.approval"
    _description  = 'requisition.order.approval'

    approvals = fields.Selection(selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', 'All'),
            ('amount', 'Amount'),
            ],string='Approvals')
    is_approve = fields.Boolean("Approved")
    requisition_id = fields.Many2one('purchase.requisition')
    user_ids= fields.Many2many('res.users', string='Users')
    amount = fields.Float("Amount")
    approved_date = fields.Datetime("Approved Date")
    remarks = fields.Char("Remarks")
    role = fields.Char("Roles")
    approval_method = fields.Selection(selection=[
            ('1', 'Level-I'),
            ('2', 'Level-II'),
            ('3', 'Level-III'),
            ],string='Approval Level')


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'


    def _default_type_aggrement(self):
        if self._context.get('default_is_blank_ord') == True:
            type_id = self.env['purchase.requisition.type'].search([('agreement_types','=','blanket_order')])
            if type_id:
                return type_id.id
        if self._context.get('default_is_pur_req') == True:
            type_id = self.env['purchase.requisition.type'].search([('agreement_types','=','purchase_request')])
            if type_id:
                return type_id.id
        return False

    type_id = fields.Many2one(string="Type")
    request_type_id = fields.Many2one('purchase.requisition.type', string="Request Type",default=_default_type_aggrement)
    agreement_type_id = fields.Many2one('purchase.requisition.type', string="Agreement Type",default=_default_type_aggrement)
    requisition_approval_line = fields.One2many("requisition.order.approval",'requisition_id')
    is_pur_req = fields.Boolean()
    pur_req_help = fields.Boolean(compute='_get_pur_req_help',store=True)
    req_date_end = fields.Datetime(string='Request Deadline', tracking=True)
    agre_date_end = fields.Datetime(string='Agreement Deadline', tracking=True)
    date_end = fields.Datetime(string='Deadline', tracking=True)
    data_for_approval = fields.Boolean(compute='_get_approval_data',store=True)
    current_approvall = fields.Integer("Current Approval",compute='_get_approval_data',store=True)
    approval_method = fields.Selection(selection=[
            ('1', 'Level-I'),
            ('2', 'Level-II'),
            ('3', 'Level-III'),
            ],string='Approval Level')
    is_lines_state = fields.Boolean(compute='_compute_line_ids_state')
    is_blank_ord = fields.Boolean(default=True)

    # state = fields.Selection(
    #     selection_add=[('approved', 'Approved'),('ongoing',)],ondelete={'approved':'set default'})

    # state_blanket_order = fields.Selection(
    #     selection_add=[('approved', 'Approved'),('ongoing',)]
    # )
    

    @api.depends('line_ids.state')
    def _compute_line_ids_state(self):
        for rec in self:
            if 'to_approve' in rec.line_ids.mapped('state'):
                rec.is_lines_state = False
            else:
                rec.is_lines_state = True

    
    
    def get_approval_all(self):
        for line in self.line_ids:
            line.get_approval()
    
    @api.depends('type_id','request_type_id','activity_type_id')
    def _get_pur_req_help(self):
        for rec in self:
            if rec.type_id and not rec.request_type_id and not rec.agreement_type_id:
                if rec.type_id.sequence_id:
                    rec.request_type_id = rec.type_id.id
                    rec.pur_req_help = True
                else:
                    rec.agreement_type_id = rec.type_id.id
                    rec.pur_req_help = False
                rec.is_pur_req = rec.pur_req_help
            else:
                rec.pur_req_help = rec.is_pur_req


  
    
    @api.onchange('agreement_type_id')
    def _oc_ati(self):
        self.type_id = self.agreement_type_id.id

    def action_in_progress(self):
        self.ensure_one()
        res = super(PurchaseRequisition, self).action_in_progress()
        # if not self.agreement_type_id:
        #     for line in self.line_ids:
        #         # Compute name
        #         if self.current_approvall == 1:
        #             if not line.approval_one:
        #                 raise UserError (_("You cannot Confirm the order"))
        #         elif self.current_approvall == 2 :
        #             if not line.approval_two:
        #                 raise UserError (_("You cannot Confirm the order"))
        #         elif self.current_approvall == 3 :
        #             if not line.approval_three:
        #                 raise UserError (_("You cannot Confirm the order"))

        if self.is_pur_req == True:
            if 'approved' not in self.line_ids.mapped('state'):
                    raise UserError (_("Pending for Approval"))
            if self.type_id.sequence_id:
                self.name = self.type_id.sequence_id.next_by_id()

        return res
        
    @api.depends('picking_type_id','request_type_id')
    def _get_approval_data(self):
        for each in self:
            if each.picking_type_id.id or  each.request_type_id.id:
                # approval_ids = self.env['requisition.approval'].search([('warehouse_id','=',each.picking_type_id.warehouse_id.id),('document_type_id','=',each.request_type_id.id)])
                approval_ids = self.env['requisition.approval'].search([('document_type_id','=',each.request_type_id.id)])
                if self.requisition_approval_line:
                    self.requisition_approval_line = False

                each.write({'current_approvall': int(approval_ids.approval_method)})
                for each_line in approval_ids.approval_lines:
                   
                    if each_line.approval_one:
                        value='1'
                    elif each_line.approval_two:
                        value='2'
                    elif each_line.approval_three:
                        value='3'
                    else:
                        value='4'

                    valas={
                    'approvals':value ,
                    'user_ids': [(6, 0, each_line.user_ids.ids)],
                    'requisition_id':each.id,
                    'role':each_line.role,
                    }
                    self.env['requisition.order.approval'].create(valas)




    @api.onchange('req_date_end')
    def _oc_rdt(self):
        self.date_end = self.req_date_end
    
    @api.onchange('agre_date_end')
    def _oc_adt(self):
        self.date_end = self.agre_date_end


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        self = self.with_company(self.company_id)
        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id).get_fiscal_position(partner.id)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = fields.Datetime.now()
        # if requisition.type_id.line_copy != 'copy':
        #     return
        
        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            # if the agreement type is not there (When create Purchase Request)
            if not requisition.agreement_type_id:
                if (line.requisition_id.current_approvall ==1 and line.approval_one =='1') or (line.requisition_id.current_approvall ==2 and line.approval_two =='1') or (line.requisition_id.current_approvall ==3 and line.approval_three =='1'):
                    product_lang = line.product_id.with_context(
                        lang=partner.lang,
                        partner_id=partner.id
                    )
                    name = product_lang.display_name
                    if product_lang.description_purchase:
                        name += '\n' + product_lang.description_purchase

                    # Compute taxes
                    taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

                    # Compute quantity and price_unit
                    if line.product_uom_id != line.product_id.uom_po_id:
                        product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                        price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
                        on_hand_qty = line.on_hand_qty_req
                    else:
                        product_qty = line.product_qty
                        price_unit = line.price_unit
                        on_hand_qty = line.on_hand_qty_req

                    if requisition.type_id.quantity_copy != 'copy':
                        product_qty = 0

                    # Create PO line
                    order_line_values = line._prepare_purchase_order_line(
                        name=name, product_qty=product_qty, price_unit=price_unit,
                        taxes_ids=taxes_ids)
                    order_line_values['on_hand_qty'] = on_hand_qty
                    order_lines.append((0, 0, order_line_values))
            else:
                # the agreement type is available (When they are create Purchase Agreements)
                product_lang = line.product_id.with_context(
                lang=partner.lang,
                partner_id=partner.id
                )
                name = product_lang.display_name
                if product_lang.description_purchase:
                    name += '\n' + product_lang.description_purchase

                # Compute taxes
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

                # Compute quantity and price_unit
                if line.product_uom_id != line.product_id.uom_po_id:
                    product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                    price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
                    on_hand_qty = line.on_hand_qty_req
                else:
                    product_qty = line.product_qty
                    price_unit = line.price_unit
                    on_hand_qty = line.on_hand_qty_req

                if requisition.type_id.quantity_copy != 'copy':
                    product_qty = 0

                # Create PO line
                order_line_values = line._prepare_purchase_order_line(
                    name=name, product_qty=product_qty, price_unit=price_unit,
                    taxes_ids=taxes_ids)
                order_line_values['on_hand_qty'] = on_hand_qty
                order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines

class CustomFields(models.Model):
    _inherit = 'purchase.order.line'

    on_hand_qty = fields.Integer("On Hand Qty")
    serial_no = fields.Char(string='#',compute='_compute_sl')
    available_quantity = fields.Float('Available Quantity')


    @api.depends('sequence','order_id')
    def _compute_sl(self):
        for order in self.mapped('order_id'):
            number=1
            for line in order.order_line:
                if line.product_id:
                    line.serial_no = str(number)
                    number += 1
                else:
                    line.serial_no= str(number)

           
    @api.onchange('product_id')
    def get_on_hand_qty(self):
        self.on_hand_qty = self.product_id.qty_available        
        # available_quantity
        stock_quants = self.env['stock.quant'].search([('product_id','=',self.product_id.id)])
        for line in stock_quants:
            if line.location_id == self.order_id.picking_type_id.default_location_dest_id:
                self.available_quantity = line.available_quantity


# class StockValuationLayerInherit(models.Model):
#     _inherit = 'stock.valuation.layer'

#     analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

#     @api.model
#     def create(self,vals):
#         mo = self.env['purchase.order'].search([('id','=',self._context.get('active_id'))])
#         if self._context.get('active_model') == 'purchase.order' and mo:
#             vals['analytic_account_id'] = mo.analytic_account_id.id            
#         res =super(StockValuationLayerInherit,self).create(vals)
#         return res
