# -*- coding: utf-8 -*-
{
    'name': "Purchase Offset",

    'summary': """
        Purchase Offset Base App""",

    'description': """
        On posting of Vendor Bill add purchase and purchase offset account entries to journal items
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "http://www.prixgen.com",

    'category': 'Accounting',
    'version': '15.0.0.1',
    'license': 'LGPL-3',

    'depends': ['base','product','account','account_accountant'],

    'data': [
        'views/account.xml'
    ],
}
