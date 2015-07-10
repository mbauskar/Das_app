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

def get_payment_report_data(filters):
	condition = get_conditions(filters)
	data = frappe.db.sql("""SELECT foo.*,ifnull(SUM(dnd.total_amount),0) FROM ( SELECT pi.sales_order AS parent,pi.customer,pi.so_amt,
			    ifnull(SUM(sid.si_amt),0),ifnull(SUM(sid.paid),0),pi.pi_amt,pi.pi_paid FROM `tabPayment Information` AS pi
			LEFT JOIN `tabSales Invoice Details` sid ON sid.parent=pi.name WHERE (pi.transaction_date between '%s' AND '%s') %s
			GROUP BY pi.name) AS foo LEFT JOIN `tabDelivery Note Details` dnd ON dnd.parent=foo.parent GROUP BY foo.parent"""%(filters.get("from"),
			filters.get("to") if filters.get("to") else filters.get("start"),condition),as_list=1)
	return data

def get_conditions(filters):
	conditions = []
	if filters.get("sales_order"):
		conditions.append("pi.name='%(sales_order)s'"%filters)
	if filters.get("technician"):
		conditions.append("pi.technician='%(technician)s'"%filters)

	return " and {}".format(" and ".join(conditions)) if conditions else ""
