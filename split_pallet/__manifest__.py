# -*- coding: utf-8 -*-
{
    'name': "Split MO Based on Pallet",

    'summary': """
         This module is used to split the MO based on pallet capacity""",

    'description': """
         This module is used to split the MO based on pallet capacity
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Manufacturing',
    'version': '15.0.0.1',
    'license': 'LGPL-3',

    'depends': ['base','mrp','split_manufacturing'],

    'data': [
        'views/pallet_product_template.xml',
    ],
}
