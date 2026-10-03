from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    # _inherit (not _name!) -- we are NOT creating a new table, we are
    # adding fields/methods to the existing sale.order model/table.
    # This is the core trick this whole module demonstrates.
    _inherit = 'sale.order'

    discount_percent = fields.Float(
        string='Discount (%)',
        help='Overall discount requested for this order.',
    )

    # computed field: stored so it can be used in view domains/filters
    approval_threshold = fields.Float(
        string='Approval Threshold (%)',
        compute='_compute_approval_threshold',
        help='Discount % above which the order needs approval.',
    )

    requires_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_approval',
        store=True,
    )

    # selection_add: extends an existing Selection field instead of
    # overwriting it. 'ondelete' tells Odoo what to do with existing
    # records if this module is ever uninstalled.
    state = fields.Selection(
        selection_add=[('to_approve', 'To Approve')],
        ondelete={'to_approve': 'set default'},
    )

    @api.depends('company_id')
    def _compute_approval_threshold(self):
        # Hardcoded for now -- in a real project this would likely be
        # a res.config.settings field instead.
        for order in self:
            order.approval_threshold = 15.0

    @api.depends('discount_percent', 'approval_threshold')
    def _compute_requires_approval(self):
        for order in self:
            order.requires_approval = (
                order.discount_percent > order.approval_threshold
            )

    def action_confirm(self):
        """Override the native confirm action: orders needing approval
        are routed to 'to_approve' instead of being confirmed directly.
        """
        to_hold = self.filtered(
            lambda o: o.requires_approval and o.state != 'to_approve'
        )
        for order in to_hold:
            order.state = 'to_approve'
            order._notify_approver()

        remaining = self - to_hold
        if remaining:
            return super(SaleOrder, remaining).action_confirm()
        return True

    def action_approve(self):
        self.ensure_one()
        if not self.env.user.has_group('sale_approval.group_sale_approver'):
            raise UserError('Only a Sales Approver can approve this order.')
        # Re-run the normal confirm logic now that it's approved.
        self.requires_approval = False
        return super(SaleOrder, self).action_confirm()

    def action_reject(self):
        self.ensure_one()
        if not self.env.user.has_group('sale_approval.group_sale_approver'):
            raise UserError('Only a Sales Approver can reject this order.')
        self.state = 'draft'
        return True

    def _notify_approver(self):
        template = self.env.ref(
            'sale_approval.mail_template_approval_request',
            raise_if_not_found=False,
        )
        if template:
            template.send_mail(self.id, force_send=True)
