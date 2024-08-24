# -*- coding: utf-8 -*-
{
    'name': "ab_odoo_replication",

    'summary': """
    ab_odoo_replication
""",

    'description': """
ab_odoo_replication    """,

    'author': "abdinpharmacies",
    'website': "https://www.abdinpharmacies.com",

    'license': 'LGPL-3',
    'category': 'Abdin',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'abdin_js', 'abdin_css', 'web_progress', 'ab_hr', 'ab_product', 'ab_announcement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/cron_ab_odoo_replication.xml',
    ],
    # only loaded in demonstration mode
}
