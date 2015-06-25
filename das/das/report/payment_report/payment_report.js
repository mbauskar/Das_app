// Copyright (c) 2013, Rohit Waghchaure and contributors
// For license information, please see license.txt

frappe.query_reports["Payment Report"] = {
	"filters": [
		{
			"fieldname":"from",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -1),
			"reqd":1
		},
		{
			"fieldname":"to",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"sales_order",
			"label": __("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order"
		},
		{
			"fieldname":"technician",
			"label": __("Technician"),
			"fieldtype": "Link",
			"options": "Supplier",
			"get_query": {
				filters:{
					"supplier_type":"Technician"
				}
			}
		}
	]
}