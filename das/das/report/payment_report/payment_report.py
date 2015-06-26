# Copyright (c) 2013, Rohit Waghchaure and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_payment_report_columns()
	data = get_payment_report_data(filters)
	return columns, data

def get_payment_report_columns():
	return [
		_("Sales Order") + ":Link/Sales Order:100",
		_("Order Amount") + "::100",
		_("Invoice Amount") + "::100",
		_("Invoice Payment") + "::150",
		_("Technician Payment") + "::150",
		_("Paid") + "::100",
		_("Purchased Product Amount") + "::200"]

"""
	payment_data = {
		"SO-00001":{
			"sales_order":"SO-00001",
			"order_amt": 100,
			"invoice_amt":100,
			"invoice_payment":10,
			"technician_payment":100,
			"amt_paid":10,
			"purcese_product_amt":100
		}
	}
"""
payment_report_data = {}

def get_payment_report_data(filters):
	"""
		Sales Order : sales order number
		Order Amount : Sales Order total Amount
		Invoice Amount : sum of all the sales invoice total amount beloging to sales order
		Invoice Payment : sum of total amount paid against invoice
		Technician Amount : 
		Paid : total amount paid to Technician
		Purchased Product Amount : Amount PR
	"""
	so_names = get_sales_order_fields_values(filters)
	set_sales_invoice_fields_values(so_names)
	set_technician_fields_values(so_names)
	# si_names = set_sales_invoice_fields_values(so_names)

	# journal_entries = set_invoice_payment_entries(so_names)

	return [["SO-00001","100","100","100","100","100","100","100"]]

def get_sales_order_fields_values(filters):
	conditions = get_conditions(filters)

	sales_orders = frappe.db.sql("""select name,grand_total from `tabSales Order`
									where (transaction_date between %(start)s and %(end)s)
									{conditions}""".format(conditions=conditions), 
									{
										"start": filters.get("from"),
										"end": filters.get("to") if filters.get("to") else filters.get("start")
									},
									as_list=True)

	# creating structure to store the report data
	# storing the sales invoice details
	for sales_order in sales_orders:
		payment_report_data.update({
			sales_order[0]:{
				"sales_order":sales_order[0],
				"order_amount":sales_order[1]
			}
		})

	return [sales_order[0] for sales_order in sales_orders]

def set_sales_invoice_fields_values(sales_orders):
	so_names = "('%s')" % "','".join(tuple(sales_orders))

	# si_amts = frappe.db.sql("""select sii.sales_order,si.name,si.grand_total from `tabSales Invoice` as si,
	# 						`tabSales Invoice Item` as sii
	# 						where si.name=sii.parent and sii.sales_order in {so_names} 
	# 						group by si.name""".format(so_names=so_names), as_list=True)

	# si_amts = frappe.db.sql("""select sii.sales_order,sum(si.grand_total) from `tabSales Invoice` as si,
	# 						`tabSales Invoice Item` as sii
	# 						where si.name=sii.parent and sii.sales_order in {so_names} 
	# 						group by sii.sales_order""".format(so_names=so_names), as_list=True)

	si_amts = frappe.db.sql("""select sii.sales_order,sum(si.grand_total),(sum(si.grand_total)-sum(si.outstanding_amount)) 
							from `tabSales Invoice` as si,`tabSales Invoice Item` as sii
							where si.name=sii.parent and sii.sales_order in {so_names} 
							group by sii.sales_order""".format(so_names=so_names), as_list=True, debug=1)

	for si_amt in si_amts:
		payment_report_data[si_amt[0]].update({
			"invoice_amt":si_amt[1],
			"invoice_payment":si_amt[2]
		})
	# return si_amts

def set_technician_fields_values(so_names):
	so_names = "('%s')" % "','".join(tuple(sales_orders))

	tech_amts = frappe.db.sql("""select """)

# def set_invoice_payment_entries(so_names):
# 	# get names of sales invoices, purchase orders, purchase invoices
# 	si_names = get_sales_invoices(so_names);

# def get_sales_invoices(so_names):
# 	names = "('%s')" % "','".join(tuple(so_names))
# 	data = {}
	
# 	invoices = frappe.db.sql("select sales_order, parent from `tabSales Invoice Item` where sales_order in {names}".format(names=names))
	

# 	for inv in invoices:
# 		# payment_report_data[invoice[0]].update({
# 		# 	"invoices": payment_report_data[invoice[0]].invoices.append(invoice[1]) if payment_report_data[invoice[0]].invoices else [invoice[1]]
# 		# })
# 		if data:
# 			invoices = data[inv[0]].get("invoices").append(inv[1]) if data[inv[0]] else [inv[1]]

# 	frappe.errprint(data)
# 	return data

# def get_journal_entries(doctype, names):
# 	condition = ""
# 	names = "('%s')" % "','".join(tuple(names))

# 	if doctype == "Sales Invoice":
# 		condition = "jea.against_invoice in {names}".format(names=names)
# 	elif doctype == "Sales Order":
# 		condition = "jea.againts_sales_order in {names}".format(names=names)
# 	elif doctype == "Purchase Order":
# 		condition = "jea.againts_purchase_order in {names}".format(names=names)
# 	elif doctype == "Purchase Invoice":
# 		condition = "jea.againts_voucher in {names}".format(names=names)

# 	journal_entries = frappe.db.sql("""select sum(je.total_credit) from `tabJournal Entry` as je,
# 								`tabJournal Entry Account` as jea where je.name=jea.parent and
# 								{condition}""".format(condition=condition), as_list=True, debug=1)

# 	frappe.errprint(journal_entries)


def get_conditions(filters):
	conditions = []
	if filters.get("sales_order"):
		conditions.append("sales_order='%(sales_order)s'"%filters)
	if filters.get("technician"):
		conditions.append("technician='%(technician)s'"%filters)

	return " and {}".format(" and ".join(conditions)) if conditions else ""