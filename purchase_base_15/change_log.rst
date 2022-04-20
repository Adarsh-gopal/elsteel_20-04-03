14.0.1.8 ------> 15.0.0.1 (20-Oct-2021) **Meghana
================================================
Odoo15 conversion

15.0.0.9 ------> 15.0.1.0 (29-Jan-2022) **Anke
================================================
serial number working only products,
Removed delete option in vendor pricelist,
and and achive in vendor pricelist,
added restriction create and edit options

15.0.1.0 ------> 15.0.1.1 (31-Jan-2022) **Anke
================================================
Columns should be made as option. in collective Approvals.

  =>Columns should be made as options.

        =>Po is not confirming

        =>Product Sourcing

15.0.1.1 ------> 15.0.1.2 (1-Feb-2022) **Anke
================================================
Document type change to Agreement Type in Requisition Approval


15.0.1.2 ------> 15.0.1.3 (1-Feb-2022) **Anke
================================================
added UOM functionality

15.0.1.3 ------> 15.0.1.4 (2-Feb-2022) **Anke
================================================
Approve All Button invisibel if all lines are approved in Purchase Request,
added Availabe Qty in Purchase Request and Purchase,
Change the Conform process in Purchase Request

15.0.1.4 ------> 15.0.1.5 (7-Feb-2022) **Anke
================================================
Changed field string Quotation Number to RFQ Ref

15.0.1.5 ------> 15.0.1.6 (11-Feb-2022) **Anke
================================================
added new functionality (Copy RFQ's) in purchase order

15.0.1.6 ------> 15.0.1.7 (12-Feb-2022) **Anke
================================================
added domain (Copy RFQ's) in purchase order

15.0.1.7 ------> 15.0.1.8 (12-Feb-2022) **Anke
================================================
Copy RFQ's field make readonly and functionality
not work if PO have Purchase Aggrement

15.0.1.8 ------> 15.0.1.9 (14-Feb-2022) **Anke
================================================
=> Copy RFQ's field moved to Other Info,
=> added domain ('state','in',('sent', 'draft')) for action Requests for Quotation
=> added active field in all masters and add filters for active

15.0.1.9 ------> 15.0.2.0 (15-Feb-2022) **Anke
================================================
updated Copy RFQ's code

15.0.2.0 ------> 15.0.2.1 (15-Feb-2022) **Anke
================================================
change sourcing inherited view. and position place after bill group

15.0.2.1 ------> 15.0.2.2 (03-Mar-2022) **Anke
================================================
added invisible domain for approve and reject button in purchase request line
and add create and edit restric for picking id in purchase request

15.0.2.2 ------> 15.0.2.3 (03-Mar-2022) **Anke
================================================
changed analytic account code in valuation.

15.0.2.3 ------> 15.0.2.4 (03-Mar-2022) **Anke
================================================
removed delete option in vendor pricelist form,
and removed delete option in PR line

15.0.2.4 ------> 15.0.2.5 (08-Mar-2022) **Anke
================================================
Changed analytic_account flowing code 

15.0.2.5 ------> 15.0.2.6 (17-Mar-2022) **Anke
================================================
removed approval in purchase aggreemetns

15.0.2.6 ------> 15.0.2.7 (22-Mar-2022) **Anke
================================================
Removed analiytic account in valuation

15.0.2.7 ------> 15.0.2.8 (22-Mar-2022) **Anke
================================================
added blanket order in aggrements

15.0.2.8 ------> 15.0.2.9 (23-Mar-2022) **Anke
================================================
updated approval and aggrements

15.0.2.9 ------> 15.0.3.0 (24-Mar-2022) **Anke
================================================
vendor form move reference to form view header level

15.0.3.0 ------> 15.0.3.1 (25-Mar-2022) **Anke
================================================
Update state cancel in Domain Quotations tree view

15.0.3.1 ------> 15.0.3.2 (04-Apr-2022) **Anke
================================================
name change purchase request and order request
purchase agreement type to agreement type

15.0.3.2 ------> 15.0.3.3 (05-Apr-2022) **Anke
================================================
Revision PO => date_order = PO.date_order
                            date_planned = PO.date_planned
IN PO => date_order = fields.Datetime.now()
                date_planned = fields.Datetime.now()