frappe.views.calendar["Dispaching Dashboard"] = {
	field_map: {
		"start": "start_date",
		"end": "end_date",
		"id": "name",
		/*"title": "subject",
		"allDay": "allDay"*/
	},
	gantt: true,
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "delivery_note",
			"options": "Delivery Note",
			"label": __("Delivery Note")
		},
		{
			"fieldtype": "Link",
			"fieldname": "technician",
			"options": "Supplier",
			"label": __("Technician")
		},
		{
			"fieldtype": "Datetime",
			"fieldname": "start_date",
			"label": __("Start Date")
		},
		{
			"fieldtype": "Datetime",
			"fieldname": "end_date",
			"label": __("End Date")
		}
	],
	get_events_method: "das.pages.dispaching_dashboard.get_dispach_orders"
}