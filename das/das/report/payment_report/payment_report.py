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
# payment_report_data = {}

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

	payment_report_data = {}

	so_names = get_sales_order_fields_values(filters)
	set_sales_invoice_fields_values(so_names)
	set_technician_fields_values(so_names)
	# set_purchase_amount()
	
	return get_formatted_payment_report_data()

def get_sales_order_fields_values(filters):
	conditions = get_conditions(filters)
	sales_orders = frappe.db.sql("""select name,grand_total from `tabSales Order`
									where (transaction_date between %(start)s and %(end)s)
									{conditions}""".format(conditions=conditions), 
									{
										"start": filters.get("from"),
										"end": filters.get("to") if filters.get("to") else filters.get("start")
									},
									as_list=True,debug=1)

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

	si_amts = frappe.db.sql("""select sii.sales_order,sum(si.grand_total),(sum(si.grand_total)-sum(si.outstanding_amount)) 
							from `tabSales Invoice` as si,`tabSales Invoice Item` as sii
							where si.name=sii.parent and sii.sales_order in {so_names} 
							group by sii.sales_order""".format(so_names=so_names), as_list=True)

	for si_amt in si_amts:
		payment_report_data[si_amt[0]].update({
			"invoice_amt":si_amt[1],
			"invoice_payment":si_amt[2]
		})

def set_technician_fields_values(so_names):
	so_names = "('%s')" % "','".join(tuple(so_names))

	tech_amts = frappe.db.sql("""select sales_order,sum(grand_total),(sum(grand_total)-sum(outstanding_amount)) from `tabPurchase Invoice`
								 where sales_order in {so_names} group by sales_order""".format(so_names=so_names),
								 as_list=True)

	for tech_amt in tech_amts:
		payment_report_data[tech_amt[0]].update({
			"technician_payment":tech_amt[1],
			"amt_paid":tech_amt[2]
		})

def set_purchase_amount(so_names):
	pass

def get_formatted_payment_report_data():
	report_data = []
	if not payment_report_data:
		return report_data
	else:
		data = []
		for values in payment_report_data.values():
			data.append(values.get("sales_order"))
			data.append(values.get("order_amount"))
			data.append(values.get("invoice_amt"))
			data.append(values.get("invoice_payment"))
			data.append(values.get("technician_payment"))
			data.append(values.get("amt_paid"))
			data.append(0)

			report_data.append(data)
			data = []

	return report_data


def get_conditions(filters):
	conditions = []
	if filters.get("sales_order"):
		conditions.append("name='%(sales_order)s'"%filters)
	if filters.get("technician"):
		conditions.append("technician='%(technician)s'"%filters)

	return " and {}".format(" and ".join(conditions)) if conditions else ""