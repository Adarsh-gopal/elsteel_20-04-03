# -*- coding: utf-8 -*-
{
    'name': "SUB Manufacturing Order",

    'summary': """
         SUB Manufacturing Order""",

    'description': """
         SUB Manufacturing Order
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Manufacturing',
    'version': '15.0.0.1',
    'license': 'LGPL-3',

    'depends': ['base','mrp'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
