# -*- coding: utf-8 -*-
{
    'name': "Quality Control base Star",

    'summary': """
       """,

    'description': """
Define quality points that will generate quality checks on pickings,
manufacturing orders or work orders (quality_mrp),
Quality alerts can be created independently or related to quality checks,
Possibility to add a measure to the quality check with a min/max tolerance,
Define your stages for the quality alerts.
        """,

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    
    'category': 'Quality',
    'version': '14.0.25',
    'depends': ['base','stock','product','quality','quality_control','mrp','quality_mrp','product_expiry'],
    'data': [
        'security/ir.model.access.csv',
        'data/automation.xml',
        'views/views.xml',
    ],
}
