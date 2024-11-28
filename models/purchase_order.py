from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection=[
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('first_approval', 'First Approval'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    approval_user_ids = fields.Many2many(
        'res.users',
        string='Approval Users',
        compute='_compute_approval_users',
        store=True
    )

    def button_confirm(self):
        for order in self:
            # Check if the user has approval rights
            if not order._user_has_approval_rights():
                raise UserError(_('You do not have the rights to confirm this order.'))
        # Proceed with the original confirm functionality
        return super(PurchaseOrder, self).button_confirm()

    @api.depends('amount_total')
    def _compute_approval_users(self):
        approval_limits = self.env['purchase.approval.limit'].search([])
        for order in self:
            users = self.env['res.users']
            for limit in approval_limits:
                if order.amount_total <= limit.amount_limit:
                    users |= limit.group_id.users
            order.approval_user_ids = users

    def action_request_approval(self):
        self.ensure_one()
        # Check if the user has approval rights
        if self.env.user in self.approval_user_ids:
            self.write({'state': 'first_approval'})
            # Optionally, send a notification
            self._send_approval_notification()
        else:
            raise UserError(_('You do not have the rights to approve this order.'))

    def _send_approval_notification(self):
        # Logic to send notifications to approval users
        approval_users = self.approval_user_ids - self.env.user
        if approval_users:
            # Send notifications to other approvers
            self.message_subscribe(partner_ids=approval_users.mapped('partner_id').ids)
            self.message_post(
                body=_('Approval is required for this Purchase Order.'),
                subtype_xmlid='mail.mt_comment',
                partner_ids=approval_users.mapped('partner_id').ids
            )
