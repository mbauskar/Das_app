// *******************Get Technician*********************

// var field_name = cur_frm.doc.doctype == "Purchase Invoice"? "supplier": "technician";

cur_frm.fields_dict["technician"].get_query = function(doc) {
	return {
		filters: {
			'supplier_type': 'Technician'
		}
	}
}

cur_frm.cscript.make_purchase_invoice = function(doc){
	frappe.model.open_mapped_doc({
		method: "das.custom_methods.make_purchase_invoice",
		frm: cur_frm
	})
}