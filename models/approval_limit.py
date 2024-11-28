from odoo import models, fields

class ApprovalLimit(models.Model):
    _name = 'purchase.approval.limit'
    _description = 'Approval Limit per User Group'

    group_id = fields.Many2one('res.groups', string='User Group', required=True)
    amount_limit = fields.Monetary(string='Amount Limit', required=True)
    is_unlimited = fields.Boolean(string='Unlimited Approval', default=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
