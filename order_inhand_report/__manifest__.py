# -*- coding: utf-8 -*-
{
    'name': "ORDER INHAND REPORT",

    'summary': """
         ORDER INHAND REPORT""",

    'description': """
         ORDER INHAND REPORT
    """,
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',


    'category': 'Sales',
    'version': '15.0.0.3',
    'license': 'LGPL-3',

    'depends': ['base','sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/order_inhand_report_view.xml',
    ],
}
