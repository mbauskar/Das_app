import frappe

def on_sales_order_submit(doc,method):
    """
        On submit
        1: create new Payment information doctype
        2: insert the sales order name, and sales order amount
    """
    payment = frappe.new_doc("Payment Information")

    payment.sales_order = doc.name
    payment.so_amt = doc.grand_total
    payment.transaction_date = doc.transaction_date
    payment.technician = doc.technician
    payment.customer = doc.customer

    payment.save(ignore_permissions=True)

def on_sales_order_cancel(doc,method):
    """
        On Cancel
        1: remove sales invoice details child table details
        2: remove delivery note details child table details
        3: delete doc
    """
    payment = get_payment_information_doc(doc.name)
    if payment:
        [payment.remove(row) for row in payment.si_details]
        [payment.remove(row) for row in payment.dn_details]
        # deleting the doc
        frappe.delete_doc("Payment Information", payment.name, ignore_permissions=True)

def get_payment_information_doc(sales_order):
    payment_doc_name = frappe.db.get_value("Payment Information", {"sales_order":sales_order}, "name")
    if payment_doc_name:
        return frappe.get_doc("Payment Information", payment_doc_name)
    else:
        return None

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
        0: get sales order and get the payment information doc
        1: create Sales Invoice Details row
        2: save the sales invoice name
        3: save the sales invocie amount
        4: set sales invoice paid in case of advanced
    """
    sales_orders = get_sales_orders_from_sales_invoice([doc.name])

    for sales_order in sales_orders:
        payment = get_payment_information_doc(sales_order)
        if payment:
            # creating child table for si_details
            si_detail = payment.append('si_details', {})
            si_detail.sales_invoice = doc.name
            si_detail.parent = doc.name
            si_detail.parentfield = "si_details"
            si_detail.parenttype = "Payment Information"
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
    sales_orders = get_sales_orders_from_sales_invoice([doc.name])
    for sales_order in sales_orders:
        payment = get_payment_information_doc(sales_order)
        if payment:
            to_remove = []
            for si_detail_row in payment.si_details:
                if si_detail_row.sales_invoice == doc.name:
                    to_remove.append(si_detail_row)

            if to_remove:
                [payment.remove(si) for si in to_remove]

            payment.save(ignore_permissions=True)

def get_sales_orders_from_sales_invoice(sales_invoices):
    if not sales_invoices:
        return []
    else:
        condition = "('%s')" % "','".join(tuple(sales_invoices))
        orders = frappe.db.sql("""SELECT DISTINCT sales_order FROM `tabSales Invoice Item` WHERE parent IN %s"""%(condition),
            as_list=1)
        return [order[0] for order in orders]

def get_sales_orders_from_delivery_note(delivery_note):
    if not delivery_note:
        return []
    else:
        sales_orders = []
        orders = frappe.db.sql("""SELECT DISTINCT against_sales_order FROM `tabDelivery Note Item` WHERE parent='%s'
            AND against_sales_order IS NOT NULL"""%(delivery_note),as_list=1)
        invoices = frappe.db.sql("""SELECT DISTINCT against_sales_invoice FROM `tabDelivery Note Item` WHERE parent='%s' and
            against_sales_invoice IS NOT NULL"""%(delivery_note),as_list=1)
        sales_orders.extend([so[0] for so in orders])
        orders = get_sales_orders_from_sales_invoice([inv[0] for inv in invoices if not inv])
        sales_orders.extend([so for so in orders])
        # removing duplicates and returning list of sales order
        return list(set(sales_orders))

def on_delivery_note_submit(doc, method):
    """
        On submit
        0: get sales order/sales invoice get the payment information doc
        1: create delivery details row
        2: save the delivery note name, qty, batch number
        3: get the incoming_rate from stock ledger entry and calculate total amount
    """
    sales_orders = get_sales_orders_from_delivery_note(doc.name)

    for sales_order in sales_orders:
        payment = get_payment_information_doc(sales_order)
        if payment:
            for dn_item in doc.items:
                dn_detail_row = payment.append('dn_details', {})
                dn_detail_row.parent = payment.name
                dn_detail_row.parentfield = "dn_details"
                dn_detail_row.parenttype = "Payment Information"
                dn_detail_row.delivery_note = doc.name
                dn_detail_row.qty = dn_item.qty
                dn_detail_row.batch_number = dn_item.batch_no

                # get the incoming_rate from stock ledger entry
                dn_detail_row.incoming_rate = get_incoming_rate_from_batch(dn_item.batch_no)
                dn_detail_row.total_amount = dn_detail_row.incoming_rate * dn_item.qty

            payment.save(ignore_permissions=True)

def get_incoming_rate_from_batch(batch_no):
    """
        Get the incoming rate rate from lated stock ledger entry
        voucher_type and voucher_no ??
    """
    rate = frappe.db.sql("""SELECT incoming_rate FROM `tabStock Ledger Entry` WHERE batch_no='%s' AND voucher_type='Purchase Receipt' ORDER BY posting_date DESC,posting_time DESC LIMIT 1"""%(batch_no), as_list=1)
    if rate:
        return rate[0][0]
    else:
        return 0.0

def on_delivery_note_cancel(doc, method):
    """
        On cancel
        0: get the payment information doc
        1: remove all the rows with delivery_note = doc.name
    """
    sales_orders = get_sales_orders_from_delivery_note(doc.name)

    for sales_order in sales_orders:
        payment = get_payment_information_doc(sales_order)
        if payment:
            to_remove = []
            for dn_detail_row in payment.get("dn_details"):
                if dn_detail_row.delivery_note == doc.name:
                    to_remove.append(dn_detail_row)

            if to_remove:
                [payment.remove(dn) for dn in to_remove]

            payment.save(ignore_permissions=True)

def get_doctype_name_from_je(doc):
    result = {}

    for je_detail in doc.accounts:
        if je_detail.against_invoice:
            return {
                "against_doctype":"Sales Invoice",
                "docname":je_detail.against_invoice
            }
        elif je_detail.against_voucher:
            return {
                "against_doctype":"Purchase Invoice",
                "docname":je_detail.against_voucher
            }
        else:
            return {}
    return result

def on_journal_entry_submit(doc, method):
    """
        On submit
        0: check against which doc type journal entry is made
        1: retrieve sales order from journal entry
        2: get the payment information doc
        3: update(add) the respective paid amounts (i.e sales invoice, purchase invoice)
    """

    info = get_doctype_name_from_je(doc)

    # if against_doctype is sales invoice get the sales orders from sales invoice items
    if info:
        sales_orders = get_sales_orders_from_sales_invoice([info.get("docname")]) if info.get("against_doctype") == "Sales Invoice" else [frappe.db.get_value("Purchase Invoice",info.get("docname"),"sales_order")]
        for sales_order in sales_orders:
            payment = get_payment_information_doc(sales_order)
            if info.get("against_doctype") == "Purchase Invoice":
                payment.pi_paid += doc.total_debit
            elif info.get("against_doctype") == "Sales Invoice":
                # find si detail row and update the paid
                for si_detail_row in payment.si_details:
                    si_detail_row.paid += doc.total_debit if si_detail_row.sales_invoice == info.get("docname") else 0

            payment.save(ignore_permissions=True)

def on_journal_entry_cancel(doc, method):
    """
        On cancel
        0: check against which doc type journal entry is made
        1: retrieve sales order from journal entry
        2: get the payment information doc
        3: update(subtract) the respective paid amounts (i.e sales invoice, purchase invoice)
    """
    info = get_doctype_name_from_je(doc)

    # if against_doctype is sales invoice get the sales orders from sales invoice items
    if info:
        sales_orders = get_sales_orders_from_sales_invoice([info.get("docname")]) if info.get("against_doctype") == "Sales Invoice" else [frappe.db.get_value("Purchase Invoice",info.get("docname"),"sales_order")]
        for sales_order in sales_orders:
            payment = get_payment_information_doc(sales_order)
            if info.get("against_doctype") == "Purchase Invoice":
                payment.pi_paid -= doc.total_debit
            elif info.get("against_doctype") == "Sales Invoice":
                # find si detail row and update the paid
                for si_detail_row in payment.si_details:
                    si_detail_row.paid -= doc.total_debit if si_detail_row.sales_invoice == info.get("docname") else 0

            payment.save(ignore_permissions=True)
