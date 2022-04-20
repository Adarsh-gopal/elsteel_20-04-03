# -*- coding: utf-8 -*-
{
    'name': "Purchase Base 15",

    'summary': """
        Purchase Base Odoo 15""",

    'description': """
        1. Purchase Base Odoo 15
        2. Purchase Tolerance (Tolerance for products can be added based on UOM to restrict the receipt of excess material)
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "http://www.prixgen.com",

    'category': 'Purchase',
    'version': '15.0.3.3',
    'license': 'LGPL-3',

    'depends': ['base','purchase','product','purchase_requisition_stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/ir_sequence_data.xml',
        'wizard/wiz_last_purchase_price.xml',
        'views/last_purchase_price.xml',
        'views/purchase_requisition.xml',
        'views/customfields.xml',
        'views/purchase_uom.xml',
        'views/purchase_restriction.xml',
        'views/product_sourcing.xml',
        'views/master_delete_button.xml',
    ],
}
