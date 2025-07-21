frappe.ui.form.on('Credit Note', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Send to JoFotara'), function() {
                frappe.call({
                    method: 'jo_fotara.api.send_to_jofotara.send_to_jofotara',
                    args: { doc_type: "Credit Note", doc_name: frm.doc.name },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.msgprint(__('Successfully sent to JoFotara!'));
                            frm.reload_doc();
                        } else {
                            frappe.msgprint(__('Failed to send. ' + (r.message.message || 'Check logs.')));
                        }
                    }
                });
            });
        }
    }
});