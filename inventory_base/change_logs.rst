13.0.1.0 --> 13.0.1.1

Date-03 July 2020
By- Aniruddh Sisodia
Affected files- product_group.xml
List of changes-
    1)name field (Description) made mandetory on Group Master Trees


13.0.1.1 --> 13.0.1.2

Date-09 July 2020
By- Aniruddh Sisodia
Affected files- product_groups.py/xml
List of changes-
    1)new field 'product_category_id' added to master of ProductGroup1
    2)Domain filter of product category on product_group 1 in product masters


13.0.1.2 --> 13.0.1.3


Date-21 July 2020
By- Aniruddh Sisodia
Affected files- product_groups.py/xml
List of changes-
    1)new field 'product_category_id' added to inventory summary (stock.quant) and subsiquent views


13.0.1.3 --> 13.0.1.4

Date-27 July 2020
By- Aniruddh Sisodia
Affected files- disallow_negative_inv.py/xml
List of changes-
    1)If allow negative inv on location is true then allow negative inventory


14.0.5 ------> 15.0.0.1 (12-Oct-2021) **Meghana
================================================
Conversion to odoo15



15.0.0.2 ------> 15.0.0.3 (18-Oct-2021) **Meghana
================================================
View changes in product template


15.0.0.7 ------> 15.0.0.8 (1-Jan-2022) **Anke
================================================
Remove Manual Revaluation Access group in inventory,
changed parent menu for purchase approval and document type

15.0.0.8 ------> 15.0.0.9 (3-Jan-2022) **Anke
================================================
remove create and edit option internal refernce field in product catogery,
added below group fields in product catogery tree view.
 >>Inventory Valuation
 >>Account Stock Properties
 >>Account Properties


15.0.1.1 ------> 15.0.1.2 (8-Feb-2022) **Anke
================================================
Removed two fields purchase offset related and added in purchase offset,
 product category(app) logs added in inventory base

15.0.1.2 ------> 15.0.1.3 (9-Feb-2022) **Anke
================================================
added restriction create and edit options groups (item group and product group 1,2,3)

15.0.1.3 ------> 15.0.1.4 (11-Feb-2022) **Anke
================================================
Changed Product Category Validation Error
added new User Error for inventory_quantity field(constrains)

15.0.1.4 ------> 15.0.1.5 (15-Feb-2022) **Anke
================================================
group fileds added in optional

15.0.1.5 ------> 15.0.1.6 (21-Feb-2022) **Anke
================================================
Added delete restriction all masters

15.0.1.6 ------> 15.0.1.7 (21-Feb-2022) **Anke
================================================
merged operation_type_extend(base14,Star) both


15.0.1.7 ------> 15.0.1.8 (06-Mar-2022) **Anke
================================================
Warehouse master incresed the size of Short Name 5 to 10