{
    'name': 'SO Status Report',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',    
    
    'version': '15.0.0.5_Beta',
    'license': 'LGPL-3',
    
    'category': 'Sales',

    'summary': 'This module is useful to show the sale order lines with status of Delivery and Invoice',

    'description': """This module is useful to show the sale order lines with status of Delivery and Invoice""",
    
    'depends': ['sale'],
    
    'data': [
        'views/sale_order_line.xml',
    ],
    
    'auto_install': False,
    'installable' : True,
    'application': True,
}
