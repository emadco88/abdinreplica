{
    'name': 'ePlus Odoo Replication',
    'license': 'LGPL-3',
    'category': 'AbdinSupplyChain',
    'application': True,
    'depends': ['base',
                'ab_eplus_connect',
                'ab_product',
                'ab_store',
                'ab_supplier',
                'web_progress',
                ],
    'data': [
        'security/security_groups.xml',
        'security/record_rules.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/ab_product_view_inherit.xml',
        'views/ab_store_inherit.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         '/ab_sales/static/src/js/read_barcode.js']}

}
