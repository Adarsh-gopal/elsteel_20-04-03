# -*- coding: utf-8 -*-
{
    'name': "Material Requisition",

    'summary': """
        Material Requisition""",

    'description': """
        Material Requisition
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Customization',
    'version': '15.0.0.3',

    'license': 'LGPL-3',

    'depends': ['base','stock','purchase','purchase_base_15','mrp','purchase_requisition'],

    'data': [
        'security/ir.model.access.csv',
        'views/material_request.xml',
    ],
}
