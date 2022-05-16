# -*- coding: utf-8 -*-
{
    'name': "ELSTEEL CRM",

    'summary': """
         ELSTEEL CRM""",

    'description': """
         ELSTEEL CRM
    """,
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',


    'category': 'CRM',
    'version': '15.0.0.5',
    'license': 'LGPL-3',

    'depends': ['base','crm','partner_category'],

    'data': [
        'security/ir.model.access.csv',
        'views/custom_crm.xml',
        'views/quotation_request.xml',
        'views/quotation_category.xml',
        'data/ir.sequence_data.xml',
    ],
}
