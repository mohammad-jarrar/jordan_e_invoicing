frappe.ui.form.on('Sales Invoice', {
    refresh: function (frm) {
        if (!frm.doc.__islocal && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Send to JoFotara'), function () {
                frappe.call({
                    method: "jordan_e_invoicing.utils.api_client.send_invoice",
                    args: {
                        invoice_name: frm.doc.name
                    },
                    callback: function (response) {
                        if (response.message) {
                            frappe.msgprint(response.message);
                        }
                    }
                });
            }).addClass('btn-primary');
        }
    }
});
