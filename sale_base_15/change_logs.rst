V15.0.0.5-----> 15.0.0.6 (11-Feb-2022) **Anke**
==================================================================
 Restricted Record: multi-company in Document type

V15.0.0.6-----> 15.0.0.7 (14-Feb-2022) **Anke**
==================================================================
added domain ('state','in',('sent', 'draft')) for action Sale Quotation,

V15.0.0.7 ------> V15.0.0.8 (18-Feb-2022) **Anke
================================================
Added delete restriction all masters in sale module

V15.0.0.8 ------> V15.0.0.9 (24-Mar-2022) **Anke
================================================
removed revision state in so tree view

15.0.0.9 ------> 15.0.1.0 (25-Mar-2022) **Anke
================================================
Update state cancel in Domain Quotations tree view

15.0.1.0 ------> 15.0.1.1 (04-Apr-2022) **Anke
================================================
document type level approval to be enabled

15.0.1.1 ------> 15.0.1.2 (04-Apr-2022) **Anke
================================================
Revision SO => date_order = SO.date_order
IN SO => date_order = fields.Datetime.now()
        date_validity = self._default_validity_date()
        validity_date =date_validity