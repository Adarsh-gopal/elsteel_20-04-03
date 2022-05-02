from odoo import fields,models,api, _
# from datetime import datetime
import pdb
from datetime import datetime, time, timedelta
import datetime
from dateutil.relativedelta import relativedelta

class ProductMaster(models.Model):
    _inherit="product.template"

    planning_ids=fields.One2many('order.planning.line','order_planning_id',string="Planning")
    def create(self,vals):
        res=super(ProductMaster,self).create(vals)
        res.message_post(body="")
        return res

    def write(self,vals):
        res=super(ProductMaster,self).write(vals)
        for rec in self.planning_ids:
            msg=rec.company_id.name
            self.message_post(body=msg)
        return res
    


class PlanningMaster(models.Model):
    _name = 'order.planning.line'

    order_planning_id=fields.Many2one('product.template',string="Product planning")
    company_id=fields.Many2one('res.company',string="Company")
    route_id=fields.Many2one('stock.location.route',string="Route")
    activate=fields.Boolean(string="Activate",default=True)

    
    

class StockRule(models.Model):
    _inherit="stock.rule"

    vendor_id=fields.Many2one('res.partner',string="Vendor")

class MrpWorkCenter(models.Model):
    _inherit="mrp.workcenter"

    capacity_wt=fields.Float(string="Capacity In Weight")

class ResCompanys(models.Model):
    _inherit = "res.company"

    planning_worksheet = fields.Boolean("Planning Worksheet")


class PlanningCalculation(models.Model):
    _name = "planning.calculation"


    product_id = fields.Many2one('product.product',string='Product ID')
    plannig_sheet_id = fields.Many2one('planning.worksheet')
    workcenter_capacity_ids=fields.One2many('workcenter.capacity','planning_workcenter_id',string="Work Center Capacity")    
    material_capacity_ids=fields.One2many('material.capacity','planning_material_id',string="Material Center Capacity")    
    resource_capacity_ids=fields.One2many('resource.capacity','planning_resource_id',string="Resource Center Capacity")    

    def generate_all_bom(self):
        if self.product_id and self.plannig_sheet_id:
            without_bom = []
            with_bom =[]
            comp_dict = self._fetch_components_product(self.product_id,with_bom,without_bom)
            

    def _fetch_components_product(self,product_id,with_bom,without_bom):
        bom_id = product_id.product_tmpl_id.bom_ids
        if bom_id.company_id == self.plannig_sheet_id.company_id:
                with_bom.append({'product_id':product_id.id,
                                'product_name':product_id.name})
                bom_lines = product_id.product_tmpl_id.bom_ids.bom_line_ids
                if bom_lines:
                    for rec in bom_lines:
                        self._fetch_components_product(rec.product_id,with_bom,without_bom)
        else:
            without_bom.append({'product_id':product_id.id,
                                'product_name':product_id.name})

        return {'without_bom':without_bom,
                'with_bom':with_bom}

class WorkCenterCapacity(models.Model):
    _name = "workcenter.capacity"

    planning_workcenter_id = fields.Many2one('planning.calculation',"Planning Worksheet",ondelete='cascade')
    product_id=fields.Many2one('product.product',string="Product")
    bom_id = fields.Many2one(
        'mrp.bom', string='Bill of Materials')
    required_qty=fields.Float(string="Required Qty")
    work_center=fields.Many2one('mrp.workcenter',relation='mrp_workcenter_new',string="Work Centre")
    alt_work_center=fields.Many2many('mrp.workcenter',relation='mrp_workcenter_alt',string="Alternate Work Centre")
    wc_available_on= fields.Datetime(string='W/c available on', default=fields.Datetime.now)
    lead_days=fields.Integer(string="Lead Days")







class MaterialCapacity(models.Model):
    _name = "material.capacity"

    planning_material_id = fields.Many2one('planning.calculation',"Planning Worksheet",ondelete='cascade')
    material_id=fields.Many2one('product.product',string="Material")
    required_qty=fields.Float(string="Required Qty")
    onhand_qty=fields.Float(string="On Hand qty")
    available_qty=fields.Float(string="Available Qty")
    lead_days=fields.Float(string="Lead Days")






class ResourceCapacity(models.Model):
    _name = "resource.capacity"

    planning_resource_id = fields.Many2one('planning.calculation',"Planning Worksheet")
    operator = fields.Char(String="Operator")
    available_on= fields.Datetime(string='Available on', default=fields.Datetime.now)
    lead_days=fields.Integer(string="Lead Days")



class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    planning_worksheet = fields.Boolean(related='company_id.planning_worksheet',string="Planning Worksheet")


    # def set_values(self):
    #     super(ResConfigSetting,self).set_values()
    #     param = self.env['ir.config_parameter'].sudo()
    #     param.set_param('order_planning.planning_worksheet',self.planning_worksheet)

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSetting, self).get_values()
    #     param = self.env['ir.config_parameter'].sudo()
    #     res.update(planning_worksheet = param.get_param('order_planning.planning_worksheet'))

    #     return res

class PlanningWorksheet(models.Model):
    _name = "planning.worksheet"

    product_id=fields.Many2one('product.product',string="Product")
    company_id=fields.Many2one('res.company',string="Company")
    required_qty=fields.Float(string="Required Qty")
    lead_time=fields.Float(string="Lead Time")
    source_id=fields.Many2one("sale.order",string='Source')
    line_ids = fields.Many2one("sale.order.line",string='line ids')
    route=fields.Many2one('stock.location.route',string="Route")

    def calculation(self):
        cal_obj= self.env['planning.calculation'].search([('plannig_sheet_id','=',self.id)])
        form_view_id = self.env.ref('order_planning.view_planning_calculation_form_').id
        context = self._context.copy()
        return {
            'name': _("Planning Worksheet"),
            'type': 'ir.actions.act_window',
            'res_model': 'planning.calculation',
            'res_id': cal_obj.id,
            'context':self._context,
            'views': [(form_view_id, 'form')],
            'domain': [('plannig_sheet_id', '=', self.id)],
        }

    def generate_all_bom(self):
        plann_sheets = self.env['planning.worksheet'].search([('source_id','=',self.id)])
        for plann_sheet in plann_sheets:
            without_bom = []
            with_bom =[]
            bom_id = plann_sheet.product_id.product_tmpl_id.bom_ids
            if bom_id.company_id == plann_sheet.company_id:
                bom_lines = bom_id.bom_line_ids
                if bom_lines:
                    for rec in bom_lines:
                        comp_dict = plann_sheet._fetch_components_product(rec.product_id,with_bom,without_bom,plann_sheet.company_id,plann_sheet.required_qty,rec.product_qty)
            
                    vals_dict = {'plannig_sheet_id':plann_sheet.id,
                                'product_id':plann_sheet.product_id.id,
                                'material_capacity_ids':[(0,0,lines_1) for lines_1 in comp_dict.get('without_bom')],
                                'workcenter_capacity_ids':[(0,0,lines_2) for lines_2 in comp_dict.get('with_bom')]}
                    plann_obj = self.env['planning.calculation'].search([('plannig_sheet_id','=',plann_sheet.id)])
                    if not plann_obj:
                        pln_cal= self.env['planning.calculation'].create(vals_dict)
                    else:
                       plann_obj.write(vals_dict)

    def _lead_days_calculate(self,rec):
        lead_days = []
        avialabe_date = []
        if rec.workcenter_id.order_ids[-1].date_planned_finished == False or rec.workcenter_id.order_ids[-1].date_planned_finished <= datetime.datetime.now():
            if rec.workcenter_id.order_ids[-1].date_planned_finished == False:
                lead_days.append(0)
                return  lead_days
            lead_days.append((rec.workcenter_id.order_ids[-1].date_planned_finished - datetime.datetime.now()).total_seconds() / 60)
            return  lead_days
        else:
            lead_days.append((rec.workcenter_id.order_ids[-1].date_planned_finished - datetime.datetime.now()).total_seconds() / 60)
            if rec.workcenter_id.alternative_workcenter_ids:
                print(lead_days,88888888888811111111199999999)        
                for availability in rec.workcenter_id.alternative_workcenter_ids:
                    print(lead_days,11111119998888888888)
                    if availability.order_ids[-1].date_planned_finished == False or availability.order_ids[-1].date_planned_finished <= datetime.datetime.now():
                        if availability.order_ids[-1].date_planned_finished == False:
                            lead_days.append(0)
                            return  lead_days
                        lead_days.append((availability.order_ids[-1].date_planned_finished - datetime.datetime.now()).total_seconds() / 60)
                        return lead_days
                    lead_days.append((availability.order_ids[-1].date_planned_finished - datetime.datetime.now()).total_seconds() / 60)       
        return lead_days

    def _fetch_components_product(self,product_id,with_bom,without_bom,company_id,planned_qty,comp_qty):
        bom_id = product_id.product_tmpl_id.bom_ids
        if bom_id.company_id == company_id:
            if len(bom_id.operation_ids) > 1:
                for rec in bom_id.operation_ids:
                    days_date = self._lead_days_calculate(rec)
                    print(type(days_date),99999999999988888888888888)
                    with_bom.append({'product_id':product_id.id,
                            'required_qty':(planned_qty*comp_qty),
                            'work_center':rec.workcenter_id.id,
                            'alt_work_center':[(6,0,rec.workcenter_id.alternative_workcenter_ids.ids)] if rec.workcenter_id.alternative_workcenter_ids else False,
                            'wc_available_on': datetime.datetime.now()+ relativedelta(minutes=days_date[0]) if days_date[0] < 1440 else datetime.datetime.now() + relativedelta(minutes=sorted(days_date)[0]),
                            'lead_days': (days_date[0]/(60*24)) if days_date[0] < 1440 else (sorted(days_date)[0])/(60*24)})

            else:
                days_date = self._lead_days_calculate(bom_id.operation_ids)
                print(sorted(days_date),888888888888899999999999999)
                with_bom.append({'product_id':product_id.id,
                            'required_qty':(planned_qty*comp_qty),
                            'work_center':bom_id.operation_ids.workcenter_id.id,
                            'alt_work_center':[(6,0,bom_id.operation_ids.workcenter_id.alternative_workcenter_ids.ids)] if bom_id.operation_ids.workcenter_id.alternative_workcenter_ids else False,
                            'wc_available_on': datetime.datetime.now()+ relativedelta(minutes=days_date[0]) if days_date[0] < 1440 else datetime.datetime.now() + relativedelta(minutes=sorted(days_date)[0]),
                            'lead_days': (days_date[0]/(60*24) if days_date[0] < 1440 else (sorted(days_date)[0])/(60*24)) })
            bom_lines = product_id.product_tmpl_id.bom_ids.bom_line_ids
            if bom_lines:
                for rec in bom_lines:
                    self._fetch_components_product(rec.product_id,with_bom,without_bom,company_id,planned_qty,rec.product_qty)
        else:
            without_bom.append({'material_id':product_id.id,
                                'required_qty':(planned_qty*comp_qty)})

        return {'without_bom':without_bom,
                'with_bom':with_bom} 

    def unlink_records(self):
        plann_sheets = self.env['planning.worksheet'].search([('source_id','=',self.id)])
        for plann_sheet in plann_sheets:
            plann_calculations = self.env['planning.calculation'].search([('plannig_sheet_id','=',plann_sheet.id)])
            workcenter_capacity = self.env['workcenter.capacity'].search([('planning_workcenter_id','=',plann_calculations.id)])
            material_capacity = self.env['material.capacity'].search([('planning_material_id','=',plann_calculations.id)])
            material_capacity.unlink()
            workcenter_capacity.unlink()
            plann_calculations.unlink()

class SaleMaster(models.Model):
    _inherit = "sale.order"


    worksheet_visible = fields.Boolean()


    def action_execute_worksheet(self):
        for rec in self.order_line:
            line_obj = self.env['planning.worksheet'].search([('line_ids','=',rec.id)])
            if not line_obj:
                for plannig_id in rec.product_id.product_tmpl_id.planning_ids:
                    if plannig_id.activate == True:
                        vals={
                        'product_id':rec.product_id.id,
                        'company_id':plannig_id.company_id.id,
                        'required_qty':rec.product_uom_qty,
                        'route':plannig_id.route_id.id,
                        'source_id':self.id,
                        'line_ids':rec.id,
                        }
                        worksheet_obj = self.env['planning.worksheet'].create(vals)
                        self.worksheet_visible = True
                





    def planning_worksheet(self):
        tree_view_id = self.env.ref('order_planning.planning_worksheet_view_inheritss').id
        # context = self._context.copy()
        # context = dict(self._context,default_source_id = self.id),
        return {
            'name': _("Planning Worksheet"),
            'type': 'ir.actions.act_window',
            'res_model': 'planning.worksheet',
            'view_mode': 'tree,form',
            'context':{},
            'views': [(tree_view_id, 'tree')],
            'target': 'current',
            'domain': [('source_id', '=', self.id)],
        } 






    

