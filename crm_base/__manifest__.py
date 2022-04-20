# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'CRM Base',
    'version': '15.0.0.5',
    'summary': 'This apps helps create/generate automatic sequence of lead',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'description':"""
     Automatic Sequance on Lead , Pipeline and Opportunity \n 
     Sequance for Lead ,Opportunity and Pipeline \n
     Auto numbering on lead, Opportunity and Pipeline\n     
     Product Mapping""", 
    'license': 'LGPL-3',
    'depends':['base','sale','crm','sale_crm','sale_management','sale_base_15'],
    'data':[
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/bi_lead.xml',
        'views/res_partner.xml',
        'views/base_crm.xml',
        ],
    'installable': True,
    'auto_install': False,
}

