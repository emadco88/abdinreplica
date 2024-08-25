{
    'name': 'Abdin Product',
    'license': 'LGPL-3',
    'category': 'AbdinSupplyChain',
    'depends': ['base'],
    'data': ['security/ir.model.access.csv',
             'views/ab_product_tag.xml',
             'views/ab_product_card.xml',
             'views/ab_product.xml',
             'views/ab_product_barcode.xml',
             'views/ab_product_company.xml',
             'views/ab_product_group.xml',
             'views/ab_product_origin.xml',
             'views/ab_scientific_group.xml',
             'views/ab_usage_causes.xml',
             'views/ab_usage_manner.xml',
             'views/ab_uom.xml',
             ],
    'assets': {
        'web.assets_backend': [
            # 'ab_product/static/src/js/barcode_scan.js',
        ]
    },

}
