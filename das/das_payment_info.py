import frappe

def on_sales_order_submit(doc,method):
    """
        On submit
        1: create new Payment information doctype
        2: insert the sales order name, and sales order amount
    """
    payment = frappe.new_doc("Payment Information")

    payment.sales_order = doc.name
    payment.so_amount = doc.grand_total

    payment.save(ignore_permissions=True)

def on_sales_order_cancel(doc,method):
    """
        On Cancel
        1: remove sales invoice details child table details
        2: remove delivery note details child table details

    """

def get_payment_information_doc(sales_order):
    payment_doc_name = frappe.db.get_value("Payment Information", {"sales_order":doc.sales_order}, "name")
    if payment_doc_name:
        return frappe.get_doc("Payment Information", payment_doc_name)
    else:
        frappe.throw("Payment Information record for %s not found"%sales_order)

def on_purchase_invoice_submit(doc, method):
    """
        On submit
        1: save the purchase invoice name
        2: save the purchase invoice amount
    """
    payment = get_payment_information_doc(doc.sales_order)
    if  payment:
        payment.purchase_invoice = doc.name
        payment.pi_amt = doc.grand_total
        # set amount paid if advanced amt paid
        payment.pi_paid = doc.grand_total - doc.outstanding_amount

        payment.save(ignore_permissions=True)

def on_purchase_invoice_cancel(doc, method):
    """
        On cancel
        0: get the payment Information doc
        1: set the purchase invoice name to None
        2: set the purchase invoice amount to 0
        3: set the purchase invoice amount paid to 0
    """
    payment = get_payment_information_doc(doc.sales_order)
    if payment:
        payment.purchase_invoice = ""
        payment.pi_amt = 0
        payment.pi_paid = 0

        payment.save(ignore_permissions=True)

def on_sales_invoice_submit(doc, method):
    """
        On submit
        0: get the payment information doc
        1: create Sales Invoice Details row
        2: save the sales invoice name
        3: save the sales invocie amount
        4: set sales invoice paid in case of advanced
    """
    payment = get_payment_information_doc(doc.sales_order)
    if payment:
        # creating child table for si_details
        si_detail = payment.append('si_details', {})
        si_detail.sales_invoice = doc.grand_total
        si_detail.si_amt = doc.grand_total
        # if advance amount is paid then set paid
        si_detail.paid = doc.grand_total - doc.outstanding_amount

        payment.save(ignore_permissions=True)

def on_sales_invoice_cancel(doc, method):
    """
        On cancel
        0: get the payment information doc
        1: remove respective sales invoice details row
    """
    payment = get_payment_information_doc(doc.sales_order)
    if payment:
        for si_detail_row in si_details:
            if si_detail_row.sales_invoice == doc.name:
                self.remove(si_detail_row)

def on_delivery_note_submit(doc, method):
    """
        On submit
        0: get the payment information doc
        1: create delivery details row
        2: save the delivery note name, qty, batch number
        3: get the incoming_rate from stock ledger entry and calculate total amount
    """
    payment = get_payment_information_doc(doc.sales_order)
    if payment:
        for dn_item in items:
            dn_detail_row = payment.append('dn_details', {})
            dn_detail_row.delivery_note = doc.name
            dn_detail_row.qty = dn_item.qty
            dn_detail_row.batch_number = item.batch_no

            # get the incoming_rate from stock ledger entry
            dn_detail_row.incoming_rate = get_incoming_rate_from_batch(item.batch_no)
            dn_detail_row.total_amount = dn_detail_row.incoming_rate * item.qty

        payment.save(ignore_permissions=True)

def on_delivery_note_cancel(doc, method):
    """
        On cancel
        0: get the payment information doc
        1: remove all the rows with delivery_note = doc.name
    """
    payment = get_payment_information_doc(doc.sales_order)
    if payment:
        dn_to_remove = []
        for dn_detail_row in dn_details:
            if dn_detail_row.delivery_note == doc.name:
                dn_to_remove.append(dn_detail_row)
        # remove all the rows whose delivery note value is doc.name
        [self.remove(dn_item) for dn_item in dn_detils]

def on_journal_entry_submit(doc, method):
    """
        On submit
        0: check against which doc type journal entry is made
        1: retrieve sales order from journal entry
        2: get the payment information doc
        3: update(add) the respective paid amounts (i.e sales invoice, purchase invoice)
    """
    against_doctype = ""
    docname = ""

    for je_detail in accounts:
        if je_detail.against_invoice:
            against_doctype = "Sales Invoice"
            docname = je_detail.against_invoice
        elif je_detail.against_purchase_invoice:
            against_doctype = "Purchase Invoice"
            docname = je_detail.against_voucher
    pass

def on_journal_entry_cancel(doc, method):
    """
        On cancel
        On submit
        0: check against which doc type journal entry is made
        1: retrieve sales order from journal entry
        2: get the payment information doc
        3: update(subtract) the respective paid amounts (i.e sales invoice, purchase invoice)
    """
