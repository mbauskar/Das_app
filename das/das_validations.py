import frappe
from datetime import datetime as dt

def delivery_note_validations(doc, method):
	# start date end end date
	start = dt.strptime(doc.start_date, "%Y-%m-%d %H:%M:%S")
	end  = dt.strptime(doc.end_date, "%Y-%m-%d %H:%M:%S")

	if start > end:
		frappe.throw("End Date should be greater than Start Date")

def validations_against_batch_nubmer(doc, method):
	err_items = []
	for item in doc.items:
		if frappe.db.get_value("Item",item.item_code,"has_batch_no") == "Yes" and not item.batch_no:
			err_items.append(item.item_code)

	if err_items:
		frappe.throw("Item Batch Number is mandatory for item(s) {err_items}".format(err_items = ",".join(err_items)))
