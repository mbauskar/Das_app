import frappe, json

@frappe.whitelist()
def get_dispach_orders(start, end, filters=None):
	from frappe.desk.reportview import build_match_conditions
	if not frappe.has_permission("Delivery Note"):
		frappe.msgprint(_("No Permission"), raise_exception=1)

	# conditions = build_match_conditions("Delivery Note")
	# conditions = conditions and (" and " + conditions) or ""

	conditions = "dn.docstatus<>2 and (dn.start_date between '%s 00:00:00' and '%s 23:59:59' or dn.end_date between '%s' and '%s')"%(start,end,start,end)

	if filters:
		filters = json.loads(filters)
		for key in filters:
			if filters[key]:
				conditions += " and " + key + ' = "' + filters[key].replace('"', '\"') + '"'

	data = frappe.db.sql("""select dn.name, dn.customer_name,dn.technician, dn.start_date, dn.end_date, dn.status from `tabDelivery Note` as dn,
		`tabSupplier` as sup where sup.name=dn.technician and sup.supplier_type='Technician' and {conditions} order by technician asc
		""".format(conditions=conditions), as_dict=True)

	technicians = list(set([i.technician for i in data]))

	dataset = []
	for technician in technicians:
		dataset.append({
			"name": technician,
			"values": get_order_details(technician, data)
		})

	return dataset

def get_order_details(technician, orders):
	from datetime import datetime as dt
	values = []
	for order in orders:
		if technician == order.technician:
			start = int(order.start_date.strftime("%s")) * 1000
			end = int(order.end_date.strftime("%s")) * 1000

			values.append({
				"name": order.name,
				# "desc": "<div class='row'><div class='col-xs-6'>Delivery Note</div><div class='col-xs-6'>%s</div></div><div class='row'><div class='col-xs-6'>Customer</div><div class='col-xs-6'>%s</div></div><div class='row'><div class='col-xs-6'>Technician</div><div class='col-xs-6'>%s</div></div><div class='row'><div class='col-xs-6'>Start Date</div><div class='col-xs-6'>%s</div></div><div class='row'><div class='col-xs-6'>End Date</div><div class='col-xs-6'>%s</div></div>"%(order.name, order.customer_name,order.technician, order.start_date, order.end_date),
				"from": order.start_date,
				"to": order.end_date,
				"status": order.status,
				"technician": order.technician,
				"customer": order.customer_name
			})

	return values
