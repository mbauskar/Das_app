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
	return frappe.call({
		method: "das.custom_methods.is_pi_already_exsits",
		args: {
			sales_order:cur_frm.doc.name
		},
		callback: function(r){
			if(r.message == "no invoice")
				frappe.model.open_mapped_doc({
					method: "das.custom_methods.make_purchase_invoice",
					frm: cur_frm
				});
			else
				frappe.msgprint("Purchase Invoice : "+ r.message +" is already created");
		}
	});
}

is_pi_already_exsits = function(so_name){
	return frappe.call({
		method: "das.custom_methods.is_pi_already_exsits",
		args: {
			sales_order:so_name
		},
		callback: function(r){
			if(r.message == "no invoice")
				return true
			else
				return false
		}
	});
}