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
		_("ID") + ":Link/Sales Order:100",
		_("Customer") + ":Link/Customer:100",
		_("Sales Order Total") + ":Float/2:150",
		_("Amount Billed") + ":Float/2:100",
		_("Amount Received") + ":Float/2:150",
		_("Services Billed") + ":Float/2:150",
		_("Services Paid") + ":Float/2:100",
		_("Product Billed") + ":Float/2:200"]

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

	sales_orders = get_sales_order_fields_values(filters)

	for sales_order in sales_orders:
		payment_report_data.update({
			sales_order[0]:{
				"sales_order":sales_order[0],
				"customer_name":sales_order[1],
				"order_amount":sales_order[2]
			}
		})
	so_names = [sales_order[0] for sales_order in sales_orders]

	si_amts = get_sales_invoice_fields_values(so_names)
	for key,value in si_amts.iteritems():
		payment_report_data[key].update(value)

	tech_amts = get_technician_fields_values(so_names)
	for tech_amt in tech_amts:
		payment_report_data[tech_amt[0]].update({
			"technician_payment":tech_amt[1],
			"amt_paid":tech_amt[2]
		})

	pr_amts = get_purchase_amount_values(so_names)
	for key, value in pr_amts.iteritems():
		payment_report_data[key].update({
			"purcese_product_amt":value
		})
	
	return get_formatted_payment_report_data(payment_report_data)

def get_sales_order_fields_values(filters):
	conditions = get_conditions(filters)
	sales_orders = frappe.db.sql("""select name,customer_name,grand_total from `tabSales Order`
									where docstatus=1 and (transaction_date between %(start)s and %(end)s)
									{conditions}""".format(conditions=conditions), 
									{
										"start": filters.get("from"),
										"end": filters.get("to") if filters.get("to") else filters.get("start")
									},
									as_list=True)

	return sales_orders

def get_sales_invoice_fields_values(sales_orders):
	result = {so:{"invoice_amt":0,"invoice_payment":0} for so in sales_orders}

	so_names = "('%s')" % "','".join(tuple(sales_orders))
	si_amts = frappe.db.sql("""SELECT sii.sales_order,si.grand_total,(si.grand_total-si.outstanding_amount) FROM 
		`tabSales Invoice` AS si JOIN `tabSales Invoice Item` AS sii ON sii.parent=si.name WHERE si.docstatus=1 
		AND si.name=sii.parent AND sii.sales_order in {so_names} GROUP BY sii.parent""".format(so_names=so_names),
		as_list=True)

	for si_amt in si_amts:
		result[si_amt[0]].update({
			"invoice_amt": result[si_amt[0]].get("invoice_amt") + si_amt[1],
			"invoice_payment":result[si_amt[0]].get("invoice_payment") + si_amt[2]
		})

	return result

def get_technician_fields_values(so_names):
	so_names = "('%s')" % "','".join(tuple(so_names))

	tech_amts = frappe.db.sql("""select sales_order,sum(grand_total),(sum(grand_total)-sum(outstanding_amount)) from `tabPurchase Invoice`
								 where  docstatus=1 and sales_order in {so_names} group by sales_order""".format(so_names=so_names),
								 as_list=True)

	return tech_amts

def get_purchase_amount_values(so_names):
	result = {so:0 for so in so_names}
	
	so_names = "('%s')" % "','".join(tuple(so_names))
	pr_amts = frappe.db.sql("""SELECT sii.sales_order,SUM(sle.incoming_rate * sii.qty),sle.item_code 
		FROM `tabSales Invoice` AS si,`tabSales Invoice Item` AS sii, `tabStock Ledger Entry` AS sle 
		WHERE sle.voucher_type='Purchase Receipt' AND sle.batch_no=sii.batch_no AND sle.item_code=sii.item_code 
		AND si.docstatus=1 AND si.name=sii.parent AND sii.sales_order IN {so_names} GROUP BY sii.sales_order
		""".format(so_names=so_names), as_list=True)

	for amt in pr_amts:
		result[amt[0]] = amt[1]

	return result

def get_formatted_payment_report_data(payment_report_data):
	report_data = []
	if not payment_report_data:
		return report_data
	else:
		data = []
		for values in payment_report_data.values():
		
			data.append(values.get("sales_order") if values.get("sales_order") else 0.0)
			data.append(values.get("customer_name") if values.get("customer_name") else "")
			data.append(values.get("order_amount") if values.get("order_amount") else 0.0)
			data.append(values.get("invoice_amt") if values.get("invoice_amt") else 0.0)
			data.append(values.get("invoice_payment") if values.get("invoice_payment") else 0.0)
			data.append(values.get("technician_payment") if values.get("technician_payment") else 0.0)
			data.append(values.get("amt_paid") if values.get("amt_paid") else 0.0)
			data.append(values.get("purcese_product_amt") if values.get("purcese_product_amt") else 0.0)
			# data.append("to be fetch")

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