# -*- coding: utf-8 -*-
{
    'name': "Manufacturing Base Odoo 15",

    'summary': """
        Manufacturing Base Odoo 15""",

    'description': """
        Manufacturing Base
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Manufacturing',
    'version': '15.0.2.9_Beta',
    'license': 'LGPL-3',

    'depends': ['mrp','base','sale','mrp_account_enterprise','mrp_subcontracting','inventory_base'],

    'data': [
        'security/ir.model.access.csv',
        'security/mo_user_validation.xml',
        'views/item_group.xml',
        'views/workcenter_category.xml',
        'views/saleorder_number.xml',
        'views/restriction.xml',
        'views/mrp_scrap.xml',
        'views/master_delete_button.xml',
    ],
}
