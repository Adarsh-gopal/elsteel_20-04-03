# -*- coding: utf-8 -*-
{
    'name': "Sale Base Odoo 15",

    'summary': """
        Sale Base Odoo 15""",

    'description': """
        Sale Base Odoo 15
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "http://www.prixgen.com",

    'category': 'Sale',
    'version': '15.0.1.2',
    'license': 'LGPL-3',

    'depends': ['base','sale','inventory_base','account','sales_team','crm','sale_management','mail','delivery','product'],

    'data': [
        'security/ir.model.access.csv',
        'security/sales_team_security.xml',
        'views/views.xml',
        'views/sale_restriction.xml',
        'views/master_delete_restriction.xml',
    ],
}
