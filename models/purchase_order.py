from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'



    approval_user_ids = fields.Many2many(
        'res.users',
        string='Approval Users',
        compute='_compute_approval_users',
        store=True
    )
    state = fields.Selection(selection_add=[
        ('first_approval', 'First Approval')
    ])

    def button_confirm(self):
        _logger.info('button_confirm called for order(s): %s by user %s', self.ids, self.env.user.name)
        for order in self:
            # Check if the user has approval rights
            if not order._user_has_approval_rights():
                _logger.warning('User %s does not have approval rights for order %s', self.env.user.name, order.name)
                raise UserError(_('You do not have the rights to confirm this order.'))
            else:
                _logger.info('User %s has approval rights for order %s', self.env.user.name, order.name)
                # Include 'first_approval' in the allowed states
                if order.state not in ['draft', 'sent', 'first_approval']:
                    continue
                order.order_line._validate_analytic_distribution()
                order._add_supplier_to_product()
                # Deal with double validation process
                if order._approval_allowed():
                    order.button_approve()
                else:
                    order.write({'state': 'to approve'})
                if order.partner_id not in order.message_partner_ids:
                    order.message_subscribe([order.partner_id.id])
        _logger.info('Order(s) %s successfully confirmed or moved to approval state', self.ids)
        return True


    def _user_has_approval_rights(self):
        self.ensure_one()
        user_groups = self.env.user.groups_id

        # Fetch approval limits for the user's groups
        user_approval_limits = self.env['purchase.approval.limit'].search([
            ('group_id', 'in', user_groups.ids)
        ])

        if not user_approval_limits:
            return False

        # Convert order amount to the approval limit currency (assuming company currency)
        order_amount_company = self.currency_id._convert(
            self.amount_total,
            self.company_id.currency_id,
            self.company_id,
            self.date_order or fields.Date.today()
        )

        # Check if the user has unlimited approval rights
        unlimited_limits = user_approval_limits.filtered(lambda l: l.is_unlimited)
        if unlimited_limits:
            return True

        # Check if any of the user's approval limits cover the order amount
        applicable_limits = user_approval_limits.filtered(
            lambda l: l.amount_limit >= order_amount_company and l.currency_id == self.company_id.currency_id
        )

        return bool(applicable_limits)

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
