# -*- coding: utf-8 -*-
{
    'name': "Basic Inventory",

    'summary': """
        Base Customization On Inventory(stock)""",

    'description': """
        Included Functionalities -
            1) Disallow negative inventory in the product master.-----------------------------(disallow_negative_inv.py/xml)
            2) Product Category Filtered based on 'release' Boolean and Description Field.----(categ_release_and_desc.py/xml)
            3) Product/Item Groups.-----------------------------------------------------------(product_groups.py/.xml)
            4) Update Quantity Button Invisible and 'quantity on hand' readonly.--------------(update_qty.xml)
            5) Product Category Dropdown No Create Edit.--------------------------------------(product_categ_no_create_edit.xml)
            6) Product Internal Reference Sequence Based on Category.-------------------------(prod_internal_ref_on_categ.py/xml)
            7) Product Category, Cost in Log note and Category change authorization-----------(product_cost_categ_track.py, product_categ_change_access.xml)
            8) Product Category, Item Group, Product Group1, Product Group2, Product Group3 is add to the filter and groupby.------------(product_groups.xml)
            9)  Lot quantity should be greater than ZERO--------------------------------------(stock_lot.xml) """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Customization',
    'version': '15.0.1.8',

    'depends': ['base','stock','product','sale','stock_landed_costs','mrp_landed_costs','mail','uom'],
    
    'license': 'LGPL-3',

    'data': [
        'security/route_access.xml',
        'security/ir.model.access.csv',
        'security/product_categ_change_access.xml',
        'views/update_qty.xml',
        'views/product_groups.xml',
        'views/disallow_negative_inv.xml',
        'views/categ_release_and_desc.xml',
        'views/product_categ_no_create_edit.xml',
        'views/prod_internal_ref_on_categ.xml',
        'views/stock_lot.xml',
        'views/lognote_operation.xml',
        'views/lognote_locations.xml',
        'views/log_rules.xml',
        'views/stock_picking.xml',
        'views/inventory_restriction.xml',
        'views/product_category.xml',
        'views/master_delete_button.xml',
        'views/stock_view.xml',
        'views/operation_type.xml',
    ],
}
