# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from openerp.exceptions import Warning
from fabric.contrib.files import exists
from openerp.addons.base.res.res_request import referencable_models
import os


class support_new_issue_wizzard(models.TransientModel):
    _name = "support.new_issue.wizard"
    _description = "Support - New Issue Wizard"

    user_id = fields.Many2one(
        'res.users',
        required=True,
        default=lambda self: self.env.user,
        )
    company_id = fields.Many2one(
        'res.users',
        required=True,
        )
    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now
        )
    name = fields.Char(
        string='Title',
        required=True,
        )
    description = fields.Html(
        string='Description',
        required=True,
        )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'new_issue_ir_attachments_rel'
        'wizard_id', 'attachment_id',
        string='Attachments',
        required=False,
        )
    resource = fields.Reference(
        selection=lambda self: referencable_models(
            self, self.env.cr, self.env.uid, self.env.context),
        string='Resource',
        help='You can reference the model and record related to the issue,\
        this will help our technicians to resolve the issue faster',
        required=False,
        )
    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Normal'), ('2', 'High')],
        'Priority',
        select=True
        )

    @api.onchange('user_id')
    def change_user(self):
        self.company_id = self.user_id.company_id.id

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        active_contract = self.env['support.contract'].get_active_contract()
        # TODO tal vez podemos crear el user y las companies si no existe y llevar los ids
        description = self.description
        if self.resource:
            description += '\nReference: %s' % str(self.reference)
        vals = {
            'db_user': self.user_id.login,
            'db_company': self.company_id.name,
            'date': self.date,
            'issue_description': self.description,
            'name': self.name,
            'priority': self.priority,
        }
        print 'vals ', vals
        issue_id = active_contract.create_issue(vals)
        raise Warning(_('Your issue was succesfully loaded.\
            For your reference and if you contact support by another channel:\
            \n* Issue ID: %s') % (issue_id))
        return True