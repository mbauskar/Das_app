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

	sales_orders = get_sales_order_fields_values(filters)

	for sales_order in sales_orders:
		payment_report_data.update({
			sales_order[0]:{
				"sales_order":sales_order[0],
				"order_amount":sales_order[1]
			}
		})
	so_names = [sales_order[0] for sales_order in sales_orders]

	si_amts = get_sales_invoice_fields_values(so_names)

	for si_amt in si_amts:
		payment_report_data[si_amt[0]].update({
			"invoice_amt":si_amt[1],
			"invoice_payment":si_amt[2]
		})

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
	sales_orders = frappe.db.sql("""select name,grand_total from `tabSales Order`
									where docstatus=1 and (transaction_date between %(start)s and %(end)s)
									{conditions}""".format(conditions=conditions), 
									{
										"start": filters.get("from"),
										"end": filters.get("to") if filters.get("to") else filters.get("start")
									},
									as_list=True)

	return sales_orders

def get_sales_invoice_fields_values(sales_orders):
	so_names = "('%s')" % "','".join(tuple(sales_orders))

	si_amts = frappe.db.sql("""select sii.sales_order,sum(si.grand_total),(sum(si.grand_total)-sum(si.outstanding_amount)), 
							sii.batch_no from `tabSales Invoice` as si,`tabSales Invoice Item` as sii
							where  si.docstatus=1 and si.name=sii.parent and sii.sales_order in {so_names} 
							group by sii.sales_order""".format(so_names=so_names), as_list=True)

	return si_amts

def get_technician_fields_values(so_names):
	so_names = "('%s')" % "','".join(tuple(so_names))

	tech_amts = frappe.db.sql("""select sales_order,sum(grand_total),(sum(grand_total)-sum(outstanding_amount)) from `tabPurchase Invoice`
								 where  docstatus=1 and sales_order in {so_names} group by sales_order""".format(so_names=so_names),
								 as_list=True)

	return tech_amts

def get_purchase_amount_values(so_names):
	result = {so:0 for so in so_names}
	
	so_names = "('%s')" % "','".join(tuple(so_names))
	batch_nos = frappe.db.sql("""select sii.batch_no,sii.sales_order from `tabSales Invoice` as si,`tabSales Invoice Item` as sii
							where  si.docstatus=1 and si.name=sii.parent and sii.sales_order in {so_names} 
							group by sii.batch_no""".format(so_names=so_names), as_list=True)

	str_mapping = ",".join(":".join(map(str,l)) for l in batch_nos)		#creating string for data mapping
	
	batch_names = "('%s')" % "','".join(tuple([bn[0] for bn in batch_nos if bn[0]]))

	pr_amts = frappe.db.sql("""select sle.batch_no,sum(sle.valuation_rate) from `tabStock Ledger Entry` as sle
	 where sle.voucher_type='Purchase Receipt' and batch_no in {batch_names} 
	 group by sle.batch_no""".format(batch_names=batch_names),as_list=True)
	
	for amt in pr_amts:
		bn_key = str_mapping[str_mapping.index(amt[0]):].split(",")[0]
		key = bn_key.split(":")[1]

		result[key] = result[key] + amt[1] if result[key] else amt[1]

	return result

def get_formatted_payment_report_data(payment_report_data):
	report_data = []
	if not payment_report_data:
		return report_data
	else:
		data = []
		for values in payment_report_data.values():
			data.append(values.get("sales_order") if values.get("sales_order") else 0)
			data.append(values.get("order_amount") if values.get("order_amount") else 0)
			data.append(values.get("invoice_amt") if values.get("invoice_amt") else 0)
			data.append(values.get("invoice_payment") if values.get("invoice_payment") else 0)
			data.append(values.get("technician_payment") if values.get("technician_payment") else 0)
			data.append(values.get("amt_paid") if values.get("amt_paid") else 0)
			data.append(values.get("purcese_product_amt") if values.get("purcese_product_amt") else 0)

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