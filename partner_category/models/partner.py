# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import itertools
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class ResPartner(models.Model):
    _inherit = 'res.partner'


    z_partner_category = fields.Many2one('partner.category',string="Partner Category",domain="[('active_id', '=', True)]")
    customer = fields.Boolean('Customer' )
    vendor = fields.Boolean('Vendor')
    contact = fields.Boolean('Contacts' ,compute='is_contact',store=True)
    z_partner = fields.Boolean('Partner')
    ref = fields.Char(tracking=True)

    sequence_present = fields.Boolean(compute="check_seqnece_presence",store=True)

    @api.depends('z_partner_category')
    def check_seqnece_presence(self):
        for rec in self:
            if rec.z_partner_category.partner_category:
                rec.sequence_present = True
            else:
                rec.sequence_present = False





    @api.onchange('customer')
    def Onchange_customer(self):
        for each_sale in self:
            if each_sale.customer:
                each_sale.customer_rank = 1
 
    @api.onchange('vendor')
    def Onchange_vendor(self):
        for each_sale in self:
            if each_sale.vendor:
                each_sale.supplier_rank = 1   

    @api.depends('customer','vendor')
    def is_contact(self):
        for each in self:
            if each.vendor or each.customer:
                each.contact= False
            else:
                each.contact = True



    @api.model
    def create(self, vals):
        if 'z_partner' in vals and vals['z_partner']:
            sequence_type =  vals.get('z_partner_category')
            sequence_type = self.env['partner.category'].browse(sequence_type)
            if sequence_type:
                vals['ref'] = sequence_type.partner_category.next_by_id()

        return super(ResPartner, self).create(vals)

    def write(self, vals):
        if 'z_partner_category' in vals and vals['z_partner_category']:
            partner_category =  self.env['partner.category'].browse(vals.get('z_partner_category'))
            sequence_type = partner_category.partner_category
            if sequence_type:
                vals['ref'] = sequence_type.next_by_id()

        return super(ResPartner, self).write(vals)
    

    # @api.onchange('z_partner_category')
    # def get_partner_ref(self):
    #     print(self.z_partner_category.partner_category,"###########################")
    #     if self.z_partner_category.partner_category:
            
    #         self.ref = self.z_partner_category.partner_category.next_by_id()


    @api.onchange('z_partner_category')
    def Onchange_partner(self):
        for l in self:
            if l.z_partner_category.partner_category:
                l.z_partner = True
            else:
                l.z_partner = False



class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description ='partner.category'
    _parent_name = "zparent"
    _parent_store = True
    _rec_name = 'full_name'
    _order = 'full_name'

    name = fields.Char(string='Name',index=True)
    full_name = fields.Char(string='Category Name',store=True,compute='_compute_complete_name')
    zparent = fields.Many2one('partner.category',string='Parent')
    active_id = fields.Boolean(string='Release')
    partner_category = fields.Many2one('ir.sequence',string="Sequence")
    parent_path = fields.Char(index=True)
   

    @api.depends('name', 'zparent.name')
    def _compute_complete_name(self):
        for location in self:
            if location.zparent:
                location.full_name = '%s / %s' % (location.zparent.full_name, location.name)
            else:
                location.full_name = location.name

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    partner_category_id = fields.Many2one('partner.category',string="Partner Category",compute='get_partner_category',store=True)

    @api.depends('partner_id')
    def get_partner_category(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.z_partner_category:
                    rec.partner_category_id =rec.partner_id.z_partner_category.id
                else:
                    rec.partner_category_id = False
            else:
                rec.partner_category_id = False


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    # partner_reference = fields.Char('Partner Category')
    partner_id = fields.Many2one('res.partner', string='Vendor', domain="[('vendor', '=', True)]")

    partner_category_id = fields.Many2one('partner.category',string="Partner Category",compute='get_partner_category',store=True)

    @api.depends('partner_id')
    def get_partner_category(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.z_partner_category:
                    rec.partner_category_id =rec.partner_id.z_partner_category.id
                else:
                    rec.partner_category_id = False
            else:
                rec.partner_category_id = False


class AccountInvoice(models.Model):
    _inherit = "account.move"

    is_customer = fields.Boolean('Customer',compute='change_domain',store=True)
    is_vendor = fields.Boolean('Vendor',compute='change_domain',store=True)
    # partner_reference = fields.Char('Partner Category',store=True,track_visibility='always',compute='change_partners')
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        domain="['|',('customer', '=', is_customer),('vendor','=',is_vendor),('contact','=', False)]",
        string='Partner', change_default=True)

    partner_category_id = fields.Many2one('partner.category',string="Partner Category",compute='get_partner_category',store=True)

    @api.depends('partner_id')
    def get_partner_category(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.z_partner_category:
                    rec.partner_category_id =rec.partner_id.z_partner_category.id
                else:
                    rec.partner_category_id = False
            else:
                rec.partner_category_id = False


    @api.depends('partner_id')
    def change_domain(self):
        for rec in self:
            vendor_lit=['in_invoice','in_refund','in_receipt']
            customer_lit=['out_invoice','out_refund','out_receipt']
            if rec.move_type in vendor_lit:
                rec.is_vendor = True
            elif rec.move_type in customer_lit:
                rec.is_customer = True
            else:
                rec.is_vendor = False
                rec.is_customer = False

            

class account_payment(models.Model):
    _inherit = "account.payment"

    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True, readonly=True, 
        states={'draft': [('readonly', False)]})
    is_customer = fields.Boolean('Customer')
    is_vendor = fields.Boolean('Vendor')

    @api.onchange('partner_type')
    def find_user(self):
        for rec in self:
            if rec.partner_type == 'customer':
                rec.is_customer = True
                rec.is_vendor = False
            elif rec.partner_type == 'supplier':
                rec.is_vendor = True
                rec.is_customer = False


class SaleReport(models.Model):
    _inherit = "sale.report"


    partner_category_id = fields.Many2one('partner.category',string="Partner Category",readonly=True)
    # lead_no = fields.Char(string="Lead No", readonly=True)


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            coalesce(min(l.id), -s.id) as id,
            l.product_id as product_id,
            t.uom_id as product_uom,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as product_uom_qty,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_delivered / u.factor * u2.factor) ELSE 0 END as qty_delivered,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_invoiced / u.factor * u2.factor) ELSE 0 END as qty_invoiced,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_to_invoice / u.factor * u2.factor) ELSE 0 END as qty_to_invoice,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_total,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_subtotal,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.untaxed_amount_to_invoice / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as untaxed_amount_to_invoice,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.untaxed_amount_invoiced / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as untaxed_amount_invoiced,
            count(*) as nbr,
            s.name as name,
            s.date_order as date,
            s.state as state,
            s.partner_id as partner_id,
            s.partner_category_id as partner_category_id,
            s.user_id as user_id,
            s.company_id as company_id,
            s.campaign_id as campaign_id,
            s.medium_id as medium_id,
            s.source_id as source_id,
            extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
            t.categ_id as categ_id,
            s.pricelist_id as pricelist_id,
            s.analytic_account_id as analytic_account_id,
            s.team_id as team_id,
            p.product_tmpl_id,
            partner.country_id as country_id,
            partner.industry_id as industry_id,
            partner.commercial_partner_id as commercial_partner_id,
            CASE WHEN l.product_id IS NOT NULL THEN sum(p.weight * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as weight,
            CASE WHEN l.product_id IS NOT NULL THEN sum(p.volume * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as volume,
            l.discount as discount,
            CASE WHEN l.product_id IS NOT NULL THEN sum((l.price_unit * l.product_uom_qty * l.discount / 100.0 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END))ELSE 0 END as discount_amount,
            s.id as order_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
                sale_order_line l
                      right outer join sale_order s on (s.id=l.order_id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join uom_uom u on (u.id=l.product_uom)
                    left join uom_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                %s
        """ % from_clause

        groupby_ = """
            l.product_id,
            l.order_id,
            t.uom_id,
            t.categ_id,
            s.name,
            s.date_order,
            s.partner_id,
            s.partner_category_id,
            s.user_id,
            s.state,
            s.company_id,
            s.campaign_id,
            s.medium_id,
            s.source_id,
            s.pricelist_id,
            s.analytic_account_id,
            s.team_id,
            p.product_tmpl_id,
            partner.country_id,
            partner.industry_id,
            partner.commercial_partner_id,
            l.discount,
            s.id %s
        """ % (groupby)

        return '%s (SELECT %s FROM %s GROUP BY %s)' % (with_, select_, from_, groupby_)



class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    partner_category_id = fields.Many2one('partner.category',string="Partner Category",readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.partner_category_id as partner_category_id"
    
    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.partner_category_id"


    # def _select(self):
    #     select_str = """
    #         WITH currency_rate as (%s)
    #             SELECT
    #                 po.id as order_id,
    #                 min(l.id) as id,
    #                 po.date_order as date_order,
    #                 po.state,
    #                 po.date_approve,
    #                 po.dest_address_id,
    #                 po.partner_id as partner_id,
    #                 po.partner_category_id as partner_category_id,
    #                 po.user_id as user_id,
    #                 po.company_id as company_id,
    #                 po.fiscal_position_id as fiscal_position_id,
    #                 l.product_id,
    #                 p.product_tmpl_id,
    #                 t.categ_id as category_id,
    #                 po.currency_id,
    #                 t.uom_id as product_uom,
    #                 extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
    #                 extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
    #                 count(*) as nbr_lines,
    #                 sum(l.price_total / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as price_total,
    #                 (sum(l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2) as price_average,
    #                 partner.country_id as country_id,
    #                 partner.commercial_partner_id as commercial_partner_id,
    #                 analytic_account.id as account_analytic_id,
    #                 sum(p.weight * l.product_qty/line_uom.factor*product_uom.factor) as weight,
    #                 sum(p.volume * l.product_qty/line_uom.factor*product_uom.factor) as volume,
    #                 sum(l.price_subtotal / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as untaxed_total,
    #                 sum(l.product_qty / line_uom.factor * product_uom.factor) as qty_ordered,
    #                 sum(l.qty_received / line_uom.factor * product_uom.factor) as qty_received,
    #                 sum(l.qty_invoiced / line_uom.factor * product_uom.factor) as qty_billed,
    #                 case when t.purchase_method = 'purchase' 
    #                      then sum(l.product_qty / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
    #                      else sum(l.qty_received / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
    #                 end as qty_to_be_billed
    #     """ % self.env['res.currency']._select_companies_rates()
    #     return select_str


    # def _group_by(self):
    #     group_by_str = """
    #         GROUP BY
    #             po.company_id,
    #             po.user_id,
    #             po.partner_id,
    #             po.partner_category_id,
    #             line_uom.factor,
    #             po.currency_id,
    #             l.price_unit,
    #             po.date_approve,
    #             l.date_planned,
    #             l.product_uom,
    #             po.dest_address_id,
    #             po.fiscal_position_id,
    #             l.product_id,
    #             p.product_tmpl_id,
    #             t.categ_id,
    #             po.date_order,
    #             po.state,
    #             line_uom.uom_type,
    #             line_uom.category_id,
    #             t.uom_id,
    #             t.purchase_method,
    #             line_uom.id,
    #             product_uom.factor,
    #             partner.country_id,
    #             partner.commercial_partner_id,
    #             analytic_account.id,
    #             po.id
    #     """
    #     return group_by_str


class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    partner_category_id = fields.Many2one('partner.category',string="Partner Category",readonly=True)

    def _select(self):
        return super()._select() + ", move.partner_category_id as partner_category_id"

