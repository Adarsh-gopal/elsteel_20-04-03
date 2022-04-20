# -*- coding: utf-8 -*-
{
    "name": "Automatic Customer Number And Product Number.",
    "version": "15.0.0.2",
    'license': 'LGPL-3',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    "summary": """
    Automatically create the customer number from a sequence when a customer is being created.
    """,
    "description": """
Automatic Customer Number
=========================
Automatically create the customer number from a sequence when a customer is being created.

The customer number can be configured in the sequence "Customer Number".
    """,
    "category": "Sales",
    "depends": [
        "base",
        "sale","contacts","product","account",'purchase','sales_team','delivery',
    ],
    #crm_base given for sales_report implementation
    "data": [
        # "data/sequencer.xml",
        "views/partner.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "auto_install": False,
}
