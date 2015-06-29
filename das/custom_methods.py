import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	def postprocess(source, target):
		target.sales_order = source.name
		target.supplier = source.technician
		target.credit_to = frappe.db.get_value("Company", frappe.db.get_default("company"), "default_payable_account")

	def update_item(source, target, source_parent):
		target.amount = flt(source.amount) - flt(source.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = source.qty

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
				# "name": "pr_detail",
				"parent": "purchase_invoice"
			},
			"postprocess": update_item,
			"condition": lambda doc: frappe.db.get_value("Item",doc.item_code,"is_service_item") == "Yes"
		},
	}, target_doc, postprocess)

	return doclist