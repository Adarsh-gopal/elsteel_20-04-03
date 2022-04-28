# -*- coding: utf-8 -*-
{
    'name': 'Report Pdf Options',
    'summary': """shows a modal window with options for printing, downloading or opening pdf reports""",
    'description': """
        Choose one of the following options when printing a pdf report:
        - print. print the pdf report directly with the browser
        - download. download the pdf report on your computer
        - open. open the pdf report in a new tab
        You can also set a default options for each report
    """,
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['web'],
    'version': '15.0.0.1_Beta',
    'license': 'LGPL-3',
    'data': [
        # 'views/templates.xml',
        'views/ir_actions_report.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/report_pdf_options.xml'
    # ],

    'assets':{
        'web.assets_backend':[
            'report_pdf_options/static/src/js/qwebactionmanager.js',
            'report_pdf_options/static/src/js/pdf_options.js',
        ],
        'web.assets_qweb':[
        'report_pdf_options/static/src/xml/report_pdf_options.xml',
        ],  
    },

    'installable': True,
    'auto_install': False,

}
