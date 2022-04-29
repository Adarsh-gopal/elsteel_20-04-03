# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pdb 
from datetime import datetime
from dateutil.relativedelta import relativedelta

class QualityTitleWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    quality_point_title = fields.Char(string="Quality Check",related='current_quality_check_id.point_id.title')
    quality_point_norm = fields.Float(string="Norm",related='current_quality_check_id.point_id.norm')
    quality_point_tolerance_max = fields.Float(string="Tolerance Max",related='current_quality_check_id.point_id.tolerance_max')
    quality_point_tolerance_min = fields.Float(string="Tolerance Min",related='current_quality_check_id.point_id.tolerance_min')
    
#Inspection Plan
class InspectionPlan(models.Model):
    _name = "inspection.plan"
    _inherit = ['mail.thread']
    _description = "Inspection Plan"

    name = fields.Char()
    team_id = fields.Many2one('quality.alert.team', 'Team', check_company=True)
    product_id = fields.Many2one('product.product',domain="[('product_tmpl_id', '=', product_tmpl_id)]")
    product_tmpl_id = fields.Many2one('product.template', check_company=True,domain="[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    picking_type_id = fields.Many2one('stock.picking.type', "Operation Type", check_company=True)
    quality_point_ids = fields.One2many('quality.point','inspection_plan_id', check_company=True)
    transaction = fields.Selection([('before','Before'),('after','After')],string="Transaction")
    company_id = fields.Many2one('res.company', string='Company', index=True,default=lambda self: self.env.company)
    start_date = fields.Date()
    end_date = fields.Date()
    days = fields.Integer()
    hours = fields.Integer()
    minutes = fields.Integer()
    seconds = fields.Integer()
    is_lot_based = fields.Boolean(string="Lot Based Inspection")
    
    _sql_constraints = [('product_uniq', 'unique(picking_type_id, product_tmpl_id, product_id)',
                         'Inspection Plan for this Operation type and Product already exist.')]
    
    @api.constrains('days','hours','minutes','seconds')
    def check_days_time(self):
        if self.hours > 23:
            raise UserError(_("Please Enter Correct Hours"))
        if self.minutes > 59:
            raise UserError(_("Please Enter Correct Minutes"))
        if self.seconds > 59:
            raise UserError(_("Please Enter Correct Seconds"))
            
    @api.model
    def create(self,vals):
        sequence = self.env['stock.picking.type'].browse(vals.get('picking_type_id')).sequence_for_inspection_plan
        if sequence:
            vals['name'] = sequence.next_by_id()
        else:
            raise UserError(_("Please Enter The sequence for this operation Type"))
        return super(InspectionPlan,self).create(vals)

    @api.constrains('start_date','end_date')
    def _check_quantities(self):
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError(_("""End Date Can not be less than Start Date"""))


# Quality Point
class QualityPoint(models.Model):
    _inherit = "quality.point"

    inspection_plan_id = fields.Many2one('inspection.plan', ondelete='cascade')
    team_id = fields.Many2one(
        'quality.alert.team', 'Team', check_company=True,
        default=False, required=False,
        compute='_compute_details',store=True,readonly=False)
    product_ids = fields.Many2many(
        'product.product', string='Products',
        compute='_compute_details',store=True,readonly=False)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product', required=False, check_company=True,
        domain="[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute='_compute_details',store=True,readonly=False)
    picking_type_ids = fields.Many2many(
        'stock.picking.type', string='Operation Types', required=True, check_company=True,
        compute='_compute_details',store=True,readonly=False)
    company_id = fields.Many2one(
        'res.company', string='Company', required=False, index=True,default=False,
        compute='_compute_details',store=True,readonly=False)
    code = fields.Char(compute="_compute_details",store=True)

    @api.depends('inspection_plan_id','inspection_plan_id.team_id')
    def _compute_details(self):
        for rec in self:
            if rec.inspection_plan_id:
                if not rec.inspection_plan_id.product_id:
                    prod_id = self.env[('product.product')].search([('product_tmpl_id','=',rec.inspection_plan_id.product_tmpl_id.id)])
                else:
                    prod_id = rec.inspection_plan_id.product_id

                rec.product_ids = [(6,0,prod_id.ids)]
                # rec.product_tmpl_id = rec.inspection_plan_id.product_tmpl_id.id
                rec.picking_type_ids = rec.inspection_plan_id.picking_type_id
                rec.team_id = rec.inspection_plan_id.team_id.id
                rec.company_id = rec.inspection_plan_id.company_id.id
                rec.code = rec.picking_type_ids.code
            else:
                rec.picking_type_ids = rec.team_id = rec.code = False

    test_method_id = fields.Many2one('quality.test.method')
    characteristic = fields.Many2one('quality.characteristic')

    @api.onchange('characteristic')
    def _set_title(self):
        self.title = self.characteristic.description


#Inspection Sheet
class InspectionSheet(models.Model):
    _name = "inspection.sheet"
    _inherit = ['mail.thread']
    _description = "Inspection Sheet"

    name = fields.Char()
    source = fields.Char(compute='_get_source')
    product_id = fields.Many2one('product.product')
    picking_id = fields.Many2one('stock.picking')
    production_id = fields.Many2one('mrp.production')
    lot_id = fields.Many2one('stock.production.lot')
    team_id = fields.Many2one('quality.alert.team')
    company_id = fields.Many2one('res.company')
    quality_check_ids = fields.One2many('quality.check','inspection_sheet_id')
    date = fields.Date(default=fields.Date.today())
    quantity_recieved = fields.Float(compute='compute_quantity_received',inverse="inverse_quantity_received",string="Quantity Received",store=True)
    quantity_accepted = fields.Float()
    quantity_rejected = fields.Float()
    quantity_destructive = fields.Float()
    under_deviation = fields.Float()
    status = fields.Selection([('open','Open'),
                            ('accept','Accept'),
                            ('reject','Reject'),
                            ('acceptud','Accepted Under Deviation')],default='open')
    state = fields.Selection([('open','Open'),
                            ('accept','Accepted'),
                            ('reject','Rejected')],default='open')
    processed = fields.Boolean()
    sampled_quantity = fields.Float()
    revised_sheet_ids = fields.One2many('inspection.sheet.revision','inspection_sheet_id')
    code = fields.Selection(related="picking_id.picking_type_code")
    plan_id = fields.Many2one('inspection.plan',compute="compute_inspection_plan",store=True)
    is_editable = fields.Boolean(compute="compute_is_editable")
    related_sheet_id = fields.Many2one('inspection.sheet',string="Related Sheet",compute="compute_related_sheet",store=True)
    
    @api.depends('picking_id','production_id')
    def compute_related_sheet(self):
        for rec in self:
            if rec.picking_id and rec.picking_id.backorder_id:
                sheet = self.env['inspection.sheet'].search([('picking_id','=',rec.picking_id.backorder_id.id),('product_id','=',rec.product_id.id)],limit=1)
                rec.related_sheet_id = sheet.id if sheet else False
    
    @api.depends('production_id','picking_id','product_id')
    def compute_inspection_plan(self):
        for rec in self.filtered(lambda x: x.product_id):
            if rec.production_id and rec.production_id.picking_type_id and rec.product_id:
                plan = self.env['inspection.plan'].search([('picking_type_id','=',rec.production_id.picking_type_id.id),('product_tmpl_id','=',rec.product_id.product_tmpl_id.id)],limit=1)
                if plan and plan.filtered(lambda x: x.product_id and x.product_id == rec.product_id):
                    rec.plan_id = plan.filtered(lambda x: x.product_id and x.product_id == rec.product_id).id if plan else False
                else:
                    rec.plan_id = plan.id if plan else False
            elif rec.picking_id and rec.picking_id.picking_type_id and rec.product_id:
                plan = self.env['inspection.plan'].search([('picking_type_id','=',rec.picking_id.picking_type_id.id),('product_tmpl_id','=',rec.product_id.product_tmpl_id.id)],limit=1)
                if plan and plan.filtered(lambda x: x.product_id and x.product_id == rec.product_id):
                    rec.plan_id = plan.filtered(lambda x: x.product_id and x.product_id == rec.product_id).id if plan else False
                else:
                    rec.plan_id = plan.id if plan else False
            else:
                rec.plan_id = False
    
    def compute_is_editable(self):
        for rec in self:
            if rec.plan_id and rec.plan_id.transaction == 'before':
                rec.is_editable = True 
            else:
                rec.is_editable = False
            
    @api.depends('picking_id','product_id','production_id')
    def _get_source(self):
        for rec in self:
            if rec.picking_id:
                rec.source = rec.picking_id.origin
            elif rec.production_id:
                rec.source = rec.production_id.name
            else:
                rec.source = False
    
    def inverse_quantity_received(self):
        for rec in self:
            if rec.picking_id and rec.quantity_recieved > sum(rec.picking_id.move_ids_without_package.filtered(lambda x: x.product_id == rec.product_id).mapped('product_uom_qty')):
                raise UserError(_("""Qty received should not be greater than the qty of the product in the source document"""))
            elif rec.production_id and rec.quantity_recieved > rec.production_id.product_qty:
                raise UserError(_("""Qty received should not be greater than the qty of the product in the source document"""))
    
    @api.depends('picking_id','picking_id.move_ids_without_package','production_id','production_id.product_qty')
    def compute_quantity_received(self):
        for rec in self:
            if rec.picking_id:
                rec.quantity_recieved = sum(rec.picking_id.move_ids_without_package.filtered(lambda x: x.product_id == rec.product_id).mapped('product_uom_qty'))
            elif rec.production_id:
                rec.quantity_recieved = rec.production_id.product_qty
            else:
                rec.quantity_recieved = 0
                
    @api.onchange('quantity_recieved','quantity_accepted','quantity_rejected','quantity_destructive','under_deviation')
    def onchange_quantity_validation(self):
        if self.quantity_accepted > (self.quantity_recieved + self.quantity_rejected + self.quantity_destructive + self.under_deviation):
            raise UserError(_(""" The Accepted Quantity should not be greater than the Received Qty, Rejected Qty, Destructive Qty, Under Deviation"""))

    def state_approve(self):
        if self.env.user.id in self.team_id.approver_ids.ids:
            current_sates=self.quality_check_ids.mapped('quality_state')
            if 'none' in current_sates:
                raise UserError(_("""OOPS!!!\nStill you need to do quality testing"""))
            else:
                self.state = 'accept'
                self.message_post(body="Approved")

        else:
            raise UserError(_("""OOPS!!!\nLooks like you aren't authorized to Approve"""))
        if self.quantity_accepted + self.quantity_rejected + self.quantity_destructive + self.under_deviation != self.quantity_recieved:
            raise ValidationError(_("""Sum of Quantities (Accepeted, Rejected, Destructive and Accepeted under Deviation) "MUST" be equal to Recieved Quantity"""))

        checks = self.env['quality.check'].search([('picking_id','=',self.picking_id.id),
                                                    ('production_id','=',self.production_id.id),
                                                    ('inspection_sheet_id','!=',False),
                                                    ('quality_state','=','none')])
        if not checks:
            for rec in self.env['quality.check'].search([('picking_id','=',self.picking_id.id),('production_id','=',self.production_id.id),('inspection_sheet_id','=',False)]):
                rec.unlink()

    def state_reject(self):
        if self.env.user.id in self.team_id.approver_ids.ids:
            current_sates=self.quality_check_ids.mapped('quality_state')
            if 'none' in current_sates:
                raise UserError(_("""OOPS!!!\nStill you need to do quality testing"""))
            else:
                self.state = 'reject'
        else:
            raise UserError(_("""OOPS!!!\nLooks like you aren't authorized to Reject"""))
        if self.quantity_accepted + self.quantity_rejected + self.quantity_destructive + self.under_deviation != self.quantity_recieved:
            raise ValidationError(_("""Sum of Quantities (Accepeted, Rejected, Destructive and Accepeted under Deviation) "MUST" be equal to Recieved Quantity"""))

    @api.model
    def create(self,vals):
        sequence = self.env['stock.picking'].browse(vals.get('picking_id')).picking_type_id.sequence_for_inspection_sheet or \
                    self.env['mrp.production'].browse(vals.get('production_id')).picking_type_id.sequence_for_inspection_sheet
        if sequence:
            vals['name'] = sequence.next_by_id()
        return super(InspectionSheet,self).create(vals)

    def process_quantities(self):
        if self.picking_id:
            line = {
                    'product_id':self.product_id.id,
                    'location_dest_id':self.picking_id.location_dest_id.id,
                    'product_uom_id':self.product_id.product_tmpl_id.uom_id.id,
                    'location_id':self.picking_id.location_id.id,
                    'lot_id':self.lot_id.id,
                    'no_inspect':True
                    }
            if self.quantity_accepted or self.under_deviation:
                line.update({'qty_done':self.quantity_accepted+self.under_deviation})
                self.picking_id.move_line_nosuggest_ids = [(0,0,line)]

            # if self.quantity_rejected:
                # dest = self.env['stock.location'].search([('reject_location','=',True)])
                # if not dest:
                    # raise UserError(_("Please set a Reject Location."))
                # line.update({'qty_done':self.quantity_rejected,'location_dest_id': dest.id})
                # self.picking_id.move_line_nosuggest_ids = [(0,0,line)]

            if self.quantity_destructive:
                dest = self.env['stock.location'].search([('destructive_location','=',True)])
                if not dest:
                    raise UserError(_("Please set a Destructive Location."))
                current_move_id = self.env['stock.move'].search([('picking_id','=', self.picking_id.id),('product_id','=',self.product_id.id)])
                line.update({'qty_done': self.quantity_destructive,'location_dest_id': dest.id})
                current_move_id.location_dest_id = self.env['stock.location'].search([('destructive_location','=',True)]).id
                # line.move_id.update({'location_dest_id':self.env['stock.location'].search([('destructive_location','=',True)]).id})
                self.picking_id.move_line_nosuggest_ids = [(0,0,line)]
        
        self.processed = True

    def revise(self):
        ids = []
        for line in self.quality_check_ids:
            ids.append(self.env['quality.check.revision'].create({
                                'point_id':line.point_id.id,
                                'title':line.title,
                                'test_type':line.test_type,
                                'test_type_id':line.test_type_id.id,
                                'test_method_id':line.test_method_id.id,
                                'measure':line.measure,
                                'norm':line.norm,
                                'norm_unit':line.norm_unit,
                                'tolerance_min':line.tolerance_min,
                                'tolerance_max':line.tolerance_max,
                                'quality_state':line.quality_state,
                                }).id)

        revise_sheet = self.env['inspection.sheet.revision'].create({
                                'name':self.name,
                                'source':self.source,
                                'product_id':self.product_id.id,
                                'picking_id':self.picking_id.id,
                                'production_id':self.production_id.id,
                                'lot_id':self.lot_id.id,
                                'team_id':self.team_id.id,
                                'company_id':self.company_id.id,
                                'date':self.date,
                                'quantity_recieved':self.quantity_recieved,
                                'quantity_accepted':self.quantity_accepted,
                                'quantity_rejected':self.quantity_rejected,
                                'quantity_destructive':self.quantity_destructive,
                                'under_deviation':self.under_deviation,
                                'status':self.status,
                                'sampled_quantity':self.sampled_quantity,
                                'quality_check_ids':[(6,0,ids)],
                                })

        self.revised_sheet_ids = [(4,revise_sheet.id,0)]
        
        name = self.name.split('-')
        number = int(name[1]) if len(name)>1 else 0
        name = name[0]
        self.name = name + '-' + str(number+1)
        self.state = 'open'
        
    @api.model
    def auto_revise(self):
        sheets = self.env['inspection.sheet'].search(['|',('production_id','!=',False),('picking_id','!=',False),('plan_id','!=',False)])
        for sheet in sheets:
            if sheet.production_id and sheet.production_id.date_confirm and sheet.production_id.state in ['confirmed','progress','to_close']:
                if not sheet.production_id.set_interval and (sheet.plan_id.days or sheet.plan_id.hours or sheet.plan_id.minutes or sheet.plan_id.seconds):
                    sheet.production_id.date_confirm = sheet.production_id.date_confirm + relativedelta(days=sheet.plan_id.days,hours=sheet.plan_id.hours,minutes=sheet.plan_id.minutes,seconds=sheet.plan_id.seconds)
                    sheet.production_id.set_interval= True
                if sheet.production_id.set_interval and sheet.production_id.date_confirm <= datetime.now():
                    sheet.revise()
                    sheet.production_id.date_confirm = sheet.production_id.date_confirm + relativedelta(days=sheet.plan_id.days,hours=sheet.plan_id.hours,minutes=sheet.plan_id.minutes,seconds=sheet.plan_id.seconds)
            elif sheet.picking_id and sheet.picking_id.date_confirm and sheet.picking_id.state in ['draft','waiting','confirmed','assigned']:
                if not sheet.picking_id.set_interval and (sheet.plan_id.days or sheet.plan_id.hours or sheet.plan_id.minutes or sheet.plan_id.seconds):
                    sheet.picking_id.date_confirm = sheet.picking_id.date_confirm + relativedelta(days=sheet.plan_id.days,hours=sheet.plan_id.hours,minutes=sheet.plan_id.minutes,seconds=sheet.plan_id.seconds)
                    sheet.picking_id.set_interval= True
                if sheet.picking_id.set_interval and sheet.picking_id.date_confirm <= datetime.now():
                    sheet.revise()
                    sheet.picking_id.date_confirm = sheet.picking_id.date_confirm + relativedelta(days=sheet.plan_id.days,hours=sheet.plan_id.hours,minutes=sheet.plan_id.minutes,seconds=sheet.plan_id.seconds)


#Desctructive Location
class StockLocation(models.Model):
    _inherit = 'stock.location'

    destructive_location = fields.Boolean('Is a Desctructive Location?')
    reject_location = fields.Boolean('Is a Reject Location?')

    @api.onchange('destructive_location','reject_location')
    def _check_one(self):
        if self.destructive_location:
            if len(self.env['stock.location'].search([('destructive_location','=',True)])):
                self.destructive_location = False
                raise ValidationError(_("""Can not have more than one destructive location"""))
        if self.reject_location:
            if len(self.env['stock.location'].search([('reject_location','=',True)])):
                self.reject_location = False
                raise ValidationError(_("""Can not have more than one Reject location"""))



# Quality Check
class QualityCheck(models.Model):
    _inherit = "quality.check"

    inspection_sheet_id = fields.Many2one('inspection.sheet',compute='_get_inspection_sheet', store=True)

    @api.depends('product_id','picking_id','lot_id','picking_id.state')
    def _get_inspection_sheet(self):
        for rec in self:
            plan = self.env['inspection.plan'].search(['|',('picking_type_id','=',rec.picking_id.picking_type_id.id),('picking_type_id','=',rec.production_id.picking_type_id.id),
                                                       '|',('product_tmpl_id','=',rec.product_id.product_tmpl_id.id),('product_id','=',rec.product_id.id)],limit=1)
            if plan and (not plan.is_lot_based or self._context.get('create_sheet')):
                if (rec.production_id or rec.picking_id.state == 'assigned','done','cancel') and (rec.product_id.tracking != 'lot' or rec.lot_id or (plan and plan.transaction == 'before')):
                    search_params = [('product_id','=',rec.product_id.id),
                                    ('team_id','=',rec.team_id.id,),
                                    ('company_id','=',rec.company_id.id)]
                    if rec.picking_id:
                        search_params.append(('picking_id','=',rec.picking_id.id))
                    if rec.lot_id:
                        search_params.append(('lot_id','=',rec.lot_id.id))
                    if rec.production_id:
                        search_params.append(('production_id','=',rec.production_id.id))
                    sheet = self.env['inspection.sheet'].search(search_params,limit=1).id
                    if not sheet:
                        create_params = {'product_id':rec.product_id.id,
                                        'team_id':rec.team_id.id,
                                        'company_id':rec.company_id.id}
                        if rec.picking_id:
                            create_params.update({'picking_id':rec.picking_id.id})
                        if rec.lot_id:
                            create_params.update({'lot_id':rec.lot_id.id})
                        if rec.production_id:
                            create_params.update({'production_id':rec.production_id.id})
                        sheet = self.env['inspection.sheet'].create(create_params).id
                    rec.inspection_sheet_id = sheet
                else:
                    rec.inspection_sheet_id = False


    norm = fields.Float(related="point_id.norm")
    tolerance_min = fields.Float(related="point_id.tolerance_min")
    tolerance_max = fields.Float(related="point_id.tolerance_max")
    norm_unit = fields.Char(related="point_id.norm_unit")
    test_method_id = fields.Many2one('quality.test.method',related="point_id.test_method_id")


    quality_state = fields.Selection([
        ('none', 'To do'),
        ('pass', 'Passed'),
        ('fail', 'Failed')], string='Status', tracking=True,
        default='none', copy=False, store=True, compute='_set_state')

    confirm_measurement = fields.Boolean()

    @api.depends('test_type','measure','confirm_measurement')
    def _set_state(self):
        for rec in self:
            if rec.test_type == 'measure' and rec.confirm_measurement:
                # this condition for the negative values
                if not rec.tolerance_min >= 0.0 and not rec.tolerance_max > 0.0:
                    if rec.measure <= rec.tolerance_min and rec.measure >= rec.tolerance_max:
                         rec.quality_state = 'pass'
                    else:
                        rec.quality_state = 'fail'
                elif rec.measure >= rec.tolerance_min and rec.measure <= rec.tolerance_max:

                    rec.quality_state = 'pass'
                else:
                    rec.quality_state = 'fail'
            else:
                rec.quality_state = 'none'

    title = fields.Char(related="point_id.title")

    def confirm_measure_btn(self):
        
        if self.test_type == 'measure':
            self.confirm_measurement = True
        else:
            self.quality_state = 'pass'
    def fail_btn(self):
        self.quality_state = 'fail'



class QualityTestMethod(models.Model):
    _name = "quality.test.method"
    _description = "Quality Test Method"

    name = fields.Char(string="Test Method")


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    sequence_for_inspection_plan = fields.Many2one('ir.sequence')
    sequence_for_inspection_sheet = fields.Many2one('ir.sequence')

    code = fields.Selection(required=False)


#Quality Characteristics
class QualityCharacteristic(models.Model):
    _name = 'quality.characteristic'
    _description = 'QualityCharacteristic'

    name = fields.Char(compute='_generate_name',store=True)
    code = fields.Char()
    description = fields.Char()

    @api.depends('code','description')
    def _generate_name(self):
        for rec in self:
            rec.name = "%s %s"%(rec.code or '',rec.description or '')


class QualityAlertTeam(models.Model):
    _inherit = 'quality.alert.team'

    approver_id = fields.Many2one('res.users', 'Approver ')
    approver_ids = fields.Many2many('res.users', string='Approver')
    inspection_sheet_count = fields.Integer('# Inspection Sheet Alerts', compute='_compute_inspection_sheet_count')

    def _compute_inspection_sheet_count(self):
        sheet_data = self.env['inspection.sheet'].read_group([('team_id', 'in', self.ids), ('state', '=', 'open')], ['team_id'], ['team_id'])
        sheet_result = dict((data['team_id'][0], data['team_id_count']) for data in sheet_data)
        for team in self:
            team.inspection_sheet_count = sheet_result.get(team.id, 0)

class StockMove(models.Model):
    _inherit = "stock.move"

    is_edit = fields.Boolean(compute="compute_edit_lot")
    
    @api.depends('picking_id','picking_id.picking_type_id','picking_id.picking_type_id.show_operations','picking_id.picking_type_id.show_reserved')
    def compute_edit_lot(self):
        for rec in self:
            if rec.picking_id and rec.picking_id.picking_type_id and not rec.picking_id.picking_type_id.show_operations and not rec.picking_id.picking_type_id.show_reserved and rec.picking_id.check_ids and 'open' in rec.picking_id.check_ids.inspection_sheet_id.filtered(lambda x: x.product_id == rec.product_id).mapped('state'):
                rec.is_edit = False
            else:
                rec.is_edit = True

# Quality with lots from Picking
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    inspection_sheet_id = fields.Many2one('inspection.sheet',compute='_get_inspection_sheet', store=True)
    no_inspect = fields.Boolean()

    @api.depends('product_id','picking_id','lot_id')
    def _get_inspection_sheet(self):
        for rec in self:
            plan = self.env['inspection.plan'].search(['|',('product_id','=',rec.product_id.id),('product_tmpl_id','=',rec.product_id.product_tmpl_id.id),
                                                       ('picking_type_id','=',rec.picking_id.picking_type_id.id),('company_id','=',rec.company_id.id)],limit=1)
            if plan and plan.is_lot_based:
                if rec.picking_id:
                    for check in self.env['quality.check'].search([('product_id','=',rec.product_id.id),('picking_id','=',rec.picking_id.id),('lot_id','=',False)]):
                        if rec.lot_id and not rec.no_inspect:
                            quality_check = check.with_context({'create_sheet':True}).copy({'lot_id':rec.lot_id.id})
                            rec.inspection_sheet_id = quality_check.inspection_sheet_id.id
                
                elif rec.move_id.production_id:
                    for check in self.env['quality.check'].search([('product_id','=',rec.product_id.id),('production_id','=',rec.move_id.production_id.id),('lot_id','=',False)]):
                        if rec.lot_id and not rec.no_inspect:
                            quality_check = check.with_context({'create_sheet':True}).copy({'lot_id':rec.lot_id.id})
                            rec.inspection_sheet_id = quality_check.inspection_sheet_id.id



#Quality Check Revision
class QualityCheckRevision(models.Model):
    _name = "quality.check.revision"
    _description = "Quality Check Revision"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    inspection_sheet_id = fields.Many2one('inspection.sheet.revision')
    
    point_id = fields.Many2one('quality.point','Control Point')
    title = fields.Char(related="point_id.title")
    test_type = fields.Char("TTP")
    quality_state = fields.Selection([
        ('none', 'To do'),
        ('pass', 'Passed'),
        ('fail', 'Failed')], string='Status', tracking=True,
        default='none', copy=False, store=True, compute='_set_state')
    test_type_id = fields.Many2one('quality.point.test_type')
    test_method_id = fields.Many2one('quality.test.method',related="point_id.test_method_id")
    measure = fields.Float()
    norm = fields.Float(related="point_id.norm")
    norm_unit = fields.Char(related="point_id.norm_unit")
    tolerance_min = fields.Float(related="point_id.tolerance_min")
    tolerance_max = fields.Float(related="point_id.tolerance_max")

    
    @api.depends('test_type','measure')
    def _set_state(self):
        for rec in self:
            if rec.test_type == 'measure':
                if rec.measure >= rec.tolerance_min and rec.measure <= rec.tolerance_max:
                    rec.quality_state = 'pass'
                else:
                    rec.quality_state = 'fail'
            else:
                rec.quality_state = 'none'



#Inspection Sheet Revision
class InspectionSheetRevision(models.Model):
    _name = "inspection.sheet.revision"
    _inherit = ['mail.thread']
    _description = "Inspection Sheet Revision"

    inspection_sheet_id = fields.Many2one('inspection.sheet')

    name = fields.Char()
    
    date = fields.Date(default=fields.Date.today())
    company_id = fields.Many2one('res.company')
    team_id = fields.Many2one('quality.alert.team')
    source = fields.Char()
    picking_id = fields.Many2one('stock.picking')
    production_id = fields.Many2one('mrp.production')
    product_id = fields.Many2one('product.product')
    lot_id = fields.Many2one('stock.production.lot')
    
    status = fields.Selection([('open','Open'),
                            ('accept','Accept'),
                            ('reject','Reject'),
                            ('acceptud','Accepted Under Deviation')],default='open')
    quantity_recieved = fields.Float()
    sampled_quantity = fields.Float()
    quantity_accepted = fields.Float()
    quantity_rejected = fields.Float()
    quantity_destructive = fields.Float()
    under_deviation = fields.Float()
    quality_check_ids = fields.One2many('quality.check.revision','inspection_sheet_id')
    
    
class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    date_confirm = fields.Datetime()
    set_interval = fields.Boolean()
    
    def action_confirm(self):
        res = super().action_confirm()
        self.date_confirm = datetime.now()
        return res
    
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    date_confirm = fields.Datetime()
    set_interval = fields.Boolean()
    
    @api.model
    def create(self, vals):
        vals['date_confirm'] = datetime.now()
        return super(StockPicking, self).create(vals)
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for line in self.move_line_ids_without_package.filtered(lambda x: x.lot_id):
            line.lot_id.expiration_date = line.expiration_date
        if self.check_ids:
            sheets = self.env['inspection.sheet'].search([('picking_id','=',self.id)])
            if not len(self.move_ids_without_package) > 1:
                open_sheet = sheets.filtered(lambda x: x.product_id == self.move_ids_without_package.product_id)
                if open_sheet and 'open' in open_sheet.mapped('state'):
                    raise UserError(_("Please Complete the QC Check in the Inspection Sheet."))
            elif not sum(self.move_ids_without_package.mapped('quantity_done')):
                raise UserError(_("Please Complete the QC Check in the Inspection Sheet."))
            
            # for line in self.move_ids_without_package.filtered(lambda x: not x.quantity_done):
                # for sheet in sheets.filtered(lambda x: x.product_id == line.product_id):
                    # for rec in sheet.quality_check_ids:
                        # rec.fail_btn()
                    # sheet.quantity_rejected = sheet.quantity_recieved
                    # sheet.state_reject()
        return res
    
    
class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    
    
    def process(self):
        res = super().process()
        for rec in self:
            for line in rec.pick_ids.filtered(lambda x: x.check_ids):
                sheets = self.env['inspection.sheet'].search([('picking_id','=',line.id),('state','=','open')])
                for sheet in sheets:
                    for quality_line in sheet.quality_check_ids:
                        quality_line.fail_btn()
                    sheet.quantity_rejected = sheet.quantity_recieved
                    sheet.state_reject()
        return res
    
    def process_cancel_backorder(self):
        res = super().process_cancel_backorder()
        for rec in self:
            for line in rec.pick_ids.filtered(lambda x: x.check_ids):
                sheets = self.env['inspection.sheet'].search([('picking_id','=',line.id),('state','=','open')])
                for sheet in sheets:
                    for quality_line in sheet.quality_check_ids:
                        quality_line.fail_btn()
                    sheet.quantity_rejected = sheet.quantity_recieved
                    sheet.state_reject()
        return res        
        
        


