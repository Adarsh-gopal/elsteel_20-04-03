# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class EnclosureStage(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "crm.enclosure.stage"

    # @api.model
    # def default_get(self, fields):
    #     """ As we have lots of default_team_id in context used to filter out
    #     leads and opportunities, we pop this key from default of stage creation.
    #     Otherwise stage will be created for a given team only which is not the
    #     standard behavior of stages. """
    #     if 'default_team_id' in self.env.context:
    #         ctx = dict(self.env.context)
    #         ctx.pop('default_team_id')
    #         self = self.with_context(ctx)
    #     return super(Stage, self).default_get(fields)

    name = fields.Char('Enclosure Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    requirements = fields.Text('Requirements', help="Enter here the internal requirements for this stage (ex: Offer sent to customer). It will appear as a tooltip over the stage's name.")
    team_id = fields.Many2one('crm.team', string='Sales Team', ondelete="set null",
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.')
    fold = fields.Boolean('Folded in Pipeline',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    approval_lines = fields.One2many("enclosure.approval.line","approval_id",tracking=True)
    approval_method = fields.Selection(selection=[
            ('1', 'Level-I'),
            ('2', 'Level-II'),
            ('3', 'Level-III'),
            ],string='Approval Level')
    approve_bool = fields.Boolean(string="Approval")


class EnclosureAppprovalLine(models.Model):
    _name = "enclosure.approval.line"
    _description ="enclosure.approval.line"

    def _group_internal_users(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []


    user_ids = fields.Many2many("res.users",string="Users",domain=_group_internal_users)
    approval_id = fields.Many2one("crm.enclosure.stage",string="Appove")
    approval_amount = fields.Float("Amount(UP To)")
    approval_one= fields.Boolean("1")
    approval_two= fields.Boolean("2")
