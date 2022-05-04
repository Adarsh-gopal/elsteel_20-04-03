# -*- coding: utf-8 -*-
{
    'name': "Split Manufacturing",

    'summary': """
         Split Manufacturing""",

    'description': """
         Split Manufacturing
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Manufacturing',
    'version': '15.0.0.4',
    'license': 'LGPL-3',

    'depends': ['base','mrp'],

    'data': [
        'security/ir.model.access.csv',
        'views/manufacturing_split.xml',
        'views/split_production.xml',
    ],
}
