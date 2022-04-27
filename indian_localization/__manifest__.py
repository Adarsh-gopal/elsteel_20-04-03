# -*- coding: utf-8 -*-
{
    'name': "Indian Localization",

    'summary': """
        Indian Localization""",

    'description': """
        Indian Localization
        GST Code Validations

        Instead of GST code, functionality is based on TIN Number which is same as GST Code
    """,

    'license': 'LGPL-3',

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Customization',
    'version': '15.0.0.2_Beta',

    'depends': ['base'],

    'data': [
        'views/localization.xml',
        'views/gst_code_validation_views.xml',
        # 'data/state_code.xml',
    ],
}
