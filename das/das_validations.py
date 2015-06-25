import frappe
from datetime import datetime as dt

def delivery_note_validations(doc, method):
	# start date end end date
	frappe.errprint(type(doc.start_date))
	start = dt.strptime(doc.start_date, "%Y-%m-%d %H:%M:%S")
	end  = dt.strptime(doc.end_date, "%Y-%m-%d %H:%M:%S")

	if start > end:
		frappe.throw("End Date should be greater than Start Date")

