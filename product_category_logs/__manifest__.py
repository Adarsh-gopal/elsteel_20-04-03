# -*- coding: utf-8 -*-
{
    'name': "Product Category Logs",

    'summary': """
        Product category logs""",

    'description': """
          """,

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': "https://www.prixgen.com",

    'category': 'Custamization',
    'version': '15.0.1',
    'license': 'LGPL-3',

    'depends': ['base', 'purchase', 'sale','stock'],

    'data': [
        'views/product_category.xml',
        'security/route_access.xml'
    ],

}
