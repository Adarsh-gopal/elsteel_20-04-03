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
        'views/crm_enclosure.xml',
        'views/special_enclosure.xml',
        'views/crm_enclosure_stage.xml',
        'security/ir.model.access.csv',
        'data/ir.sequence_data.xml',
        'wizard/lost_reason.xml',
    ],
}

#Git Code
#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
