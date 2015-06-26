import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	def postprocess(source, target):
		target.sales_order = source.name
		target.supplier = source.technician

	def update_item(source, target, source_parent):
		print target.name
		target.amount = flt(source.amount) - flt(source.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = target.amount / flt(source.rate) if (source.rate and source.billed_amt) else source.qty

	doclist = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Purchase Invoice",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Order Item": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"name": "po_detail",
				"parent": "sales_order",
			},
			"postprocess": update_item,
			"condition": lambda doc: frappe.db.get_value("Item",doc.item_code,"is_service_item") == "Yes"
		},
	}, target_doc, postprocess)

	return doclist

def is_service_item(doc):
	frappe.errprint(doc)
	return frappe.db.get_value("Item",doc.item_code,"is_service_item")