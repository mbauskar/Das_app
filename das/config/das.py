from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Features"),
			"icon": "icon-star",
			"items": [
				{
					"type": "page",
					"name": "dispatching-dashboar",
					"icon": "icon-sitemap",
					"label": _("Dispatching Dashboard"),
					"description": _("Gantt Chart"),
					"doctype": "Delivery Note",
				},
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-wrench",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Payment Report",
					"doctype": "Sales Order"
				},
			]
		}
	]
