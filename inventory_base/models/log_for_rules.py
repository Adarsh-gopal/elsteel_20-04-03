import calendar
from collections import defaultdict, OrderedDict
from datetime import timedelta
from odoo import _, api, fields, models

class Logforrulesproducttemplate(models.Model):
    _name = "product.template"
    _inherit = ['product.template','mail.thread', 'mail.activity.mixin']

    detailed_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service')], tracking=True, string='Product Type', default='consu', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    detailed_type = fields.Selection(selection_add=[
        ('product', 'Storable Product')
    ], tracking=True, ondelete={'product': 'set consu'})
    invoice_policy = fields.Selection([
        ('order', 'Ordered quantities'),
        ('delivery', 'Delivered quantities')], string='Invoicing Policy',  tracking=True,
        help='Ordered Quantity: Invoice quantities ordered by the customer.\n'
             'Delivered Quantity: Invoice quantities delivered to the customer.',
        default='order')
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price', tracking=True,
        help="Price at which the product is sold to customers.",
    )
    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id', help="Default taxes used when selling the product.", tracking=True, string='Customer Taxes',
        domain=[('type_tax_use', '=', 'sale')], default=lambda self: self.env.company.account_sale_tax_id)

    tic_category_id = fields.Many2one('product.tic.category', tracking=True, string="TaxCloud Category",
        help="This refers to TIC (Taxability Information Codes), these are used by TaxCloud to compute specific tax "
        "rates for each product type. The value set here prevails over the one set on the product category.")
    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price', tracking=True,
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the last unit that left the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")
    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code', tracking=True,
        inverse='_set_default_code', store=True)
    l10n_in_hsn_code = fields.Char(string="HSN/SAC Code", tracking=True, help="Harmonized System Nomenclature/Services Accounting Code")
    l10n_in_hsn_description = fields.Char(string="HSN/SAC Description", tracking=True, help="HSN/SAC description is required if HSN/SAC code is not provided.")
    barcode = fields.Char('Barcode', compute='_compute_barcode', inverse='_set_barcode', tracking=True, search='_search_barcode')
    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, tracking=True, group_expand='_read_group_categ_id',
        required=True, help="Select category for the current product")
    

class Logforrulespricelist(models.Model):
    _name = "product.pricelist"
    _inherit = ['product.pricelist','mail.thread', 'mail.activity.mixin']

    name = fields.Char('Pricelist Name', tracking=True, required=True, translate=True)
    currency_id = fields.Many2one('res.currency', 'Currency', tracking=True, required=True)
    company_id = fields.Many2one('res.company', 'Company', tracking=True)
    country_group_ids = fields.Many2many('res.country.group', 'res_country_group_pricelist_rel','pricelist_id', 'res_country_group_id', string='Country Groups', tracking=True)

    # message_follower_ids = fields.One2many('mail.followers', 'res_id', string='Followers', groups='base.group_user')
    # message_ids = fields.One2many('mail.message', 'res_id', string='Messages', domain=lambda self: [('message_type', '!=', 'user_notification')], auto_join=True)

class Logforrulesdeliverycarrier(models.Model):
    _name = "delivery.carrier"
    _inherit = ['delivery.carrier','mail.thread', 'mail.activity.mixin']

    name = fields.Char('Delivery Method', required=True, translate=True, tracking=True)
    delivery_type = fields.Selection([('fixed', 'Fixed Price')], string='Provider', tracking=True, default='fixed', required=True)
    company_id = fields.Many2one('res.company', string='Company', related='product_id.company_id', tracking=True, store=True, readonly=False)
    delivery_type = fields.Selection(selection_add=[('base_on_rule', 'Based on Rules')], tracking=True, ondelete={'base_on_rule': lambda recs: recs.write({ 'delivery_type': 'fixed', 'fixed_price': 0})})
    free_over = fields.Boolean('Free if order amount is above', help="If the order total amount (shipping excluded) is above or equal to this value, the customer benefits from a free shipping", tracking=True, default=False)
    product_id = fields.Many2one('product.product', string='Delivery Product', required=True, ondelete='restrict', tracking=True)
    margin = fields.Float( tracking=True, help='This percentage will be added to the shipping price.')
    fixed_price = fields.Float( tracking=True, compute='_compute_fixed_price', inverse='_set_product_fixed_price', store=True, string='Fixed Price')

    country_ids = fields.Many2many('res.country', 'delivery_carrier_country_rel', 'carrier_id', 'country_id', 'Countries', tracking=True)
    state_ids = fields.Many2many('res.country.state', 'delivery_carrier_state_rel', 'carrier_id', 'state_id', 'States',  tracking=True,)
    zip_from = fields.Char('Zip From', tracking=True)
    zip_to = fields.Char('Zip To', tracking=True)


class Logforrulesuom(models.Model):
    _name = "uom.uom"
    _inherit = ['uom.uom','mail.thread', 'mail.activity.mixin']

    name = fields.Char('Unit of Measure', required=True, tracking=True, translate=True)
    category_id = fields.Many2one(
        'uom.category', 'Category', required=True, tracking=True, ondelete='restrict',
        help="Conversion between Units of Measure can only occur if they belong to the same category. The conversion will be made based on the ratios.")
    uom_type = fields.Selection([
        ('bigger', 'Bigger than the reference Unit of Measure'),
        ('reference', 'Reference Unit of Measure for this category'),
        ('smaller', 'Smaller than the reference Unit of Measure')], 'Type',
        default='reference', tracking=True, required=True)
    l10n_in_code = fields.Char("Indian GST UQC", tracking=True, help="Unique Quantity Code (UQC) under GST")
    rounding = fields.Float(
        'Rounding Precision', default=0.01, digits=0, tracking=True, required=True,
        help="The computed quantity will be a multiple of this value. "
             "Use 1.0 for a Unit of Measure that cannot be further split, such as a piece.")
    active = fields.Boolean('Active', tracking=True, default=True, help="Uncheck the active field to disable a unit of measure without deleting it.")


class Logforrulesuomcategory(models.Model):
    _name = "uom.category"
    _inherit = ['uom.category','mail.thread', 'mail.activity.mixin']

    name = fields.Char('Unit of Measure Category', tracking=True, required=True, translate=True)


class Logforrulesuomcategory(models.Model):
    _name = "mail.activity.type"
    _inherit = ['mail.activity.type','mail.thread', 'mail.activity.mixin']

    def _get_model_selection(self):
        return [
            (model.model, model.name)
            for model in self.env['ir.model'].sudo().search(
                ['&', ('is_mail_thread', '=', True), ('transient', '=', False)])
        ]

    name = fields.Char('Name', required=True, tracking=True, translate=True)
    category = fields.Selection([('default', 'None'),('upload_file', 'Upload Document'),('phonecall', 'Phonecall')], default='default', tracking=True, string='Action', help='Actions may trigger specific behavior like opening calendar view or automatically mark as done when a document is uploaded')
    default_user_id = fields.Many2one("res.users", tracking=True, string="Default User")
    
    default_note = fields.Html(string="Default Note", tracking=True, translate=True)
    res_model = fields.Selection(selection=_get_model_selection, string="Model",
        help='Specify a model if the activity should be specific to a model'
             ' and not available when managing activities for other models.')
    summary = fields.Char('Default Summary', tracking=True, translate=True)
    icon = fields.Char('Icon', tracking=True, help="Font awesome icon e.g. fa-tasks")
    decoration_type = fields.Selection([('warning', 'Alert'),('danger', 'Error')], string="Decoration Type", tracking=True, help="Change the background color of the related activities of this type.")
    
    chaining_type = fields.Selection([('suggest', 'Suggest Next Activity'), ('trigger', 'Trigger Next Activity')], tracking=True, string="Chaining Type", required=True, default="suggest")
    suggested_next_type_ids = fields.Many2many('mail.activity.type', 'mail_activity_rel', 'activity_id', 'recommended_id',tracking=True, string='Suggest',
        domain="['|', ('res_model', '=', False), ('res_model', '=', res_model)]",
        compute='_compute_suggested_next_type_ids', inverse='_inverse_suggested_next_type_ids', store=True, readonly=False,
        help="Suggest these activities once the current one is marked as done.")
    mail_template_ids = fields.Many2many('mail.template', tracking=True, string='Email templates')
    delay_count = fields.Integer(
        'Schedule', default=0, tracking=True,
        help='Number of days/week/month before executing the action. It allows to plan the action deadline.')
    delay_unit = fields.Selection([
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('months', 'months')], string="Delay units", tracking=True, help="Unit of delay", required=True, default='days')
    delay_label = fields.Char(compute='_compute_delay_label', tracking=True)
    delay_from = fields.Selection([
        ('current_date', 'after completion date'),
        ('previous_activity', 'after previous activity deadline')], tracking=True, string="Delay Type", help="Type of delay", required=True, default='previous_activity')
