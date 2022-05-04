# -*- coding: utf-8 -*-
{
    'name': "Order Planning12",

    'summary': """
         Order Planning""",

    'description': """
         Order Planning
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Sales',
    'version': '15.0.0.6',
    'license': 'LGPL-3',

    'depends': ['base','sale','product','stock','mrp','web'],

    'data': [
        'security/ir.model.access.csv',
        'views/order_planning.xml',
        'views/res_company.xml',
    ],

    'assets':{
        'web.assets_backend':[
            'order_planning/static/src/js/models.js',
            'order_planning/static/src/js/clear_boms.js'
        ],
        'web.assets_qweb':[
        'order_planning/static/src/xml/**/*',
        ],  
    },
}
