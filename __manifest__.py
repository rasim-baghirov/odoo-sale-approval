{
    'name': 'Sale Order Approval',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Adds a discount-approval workflow to Sales Orders',
    'description': """
        Sale Order Approval
        ====================
        Extends the native Sales module (no new model, no new app): orders
        with a discount above a configurable threshold require approval from
        a dedicated Sales Approver group before they can be confirmed.
    """,
    'author': 'Rasim Baghirov',
    'depends': ['sale_management'],
    'data': [
        'security/sale_approval_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
