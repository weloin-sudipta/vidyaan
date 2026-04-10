frappe.ui.form.on('Publication', {

    refresh: function(frm) {

        // Show buttons only if submitted + pending
        if (frm.doc.docstatus === 1 && frm.doc.status === "Pending") {

            frm.add_custom_button(__('Approve'), async () => {
                await frm.set_value('status', 'Approved');
                await frm.save('Update');
                frappe.msgprint("✅ Publication Approved");
            }, __("Actions"));

            frm.add_custom_button(__('Reject'), async () => {
                await frm.set_value('status', 'Rejected');
                await frm.save('Update');
                frappe.msgprint("❌ Publication Rejected");
            }, __("Actions"));
        }
    },

    type: function(frm) {

        // Auto-set targeting for Notice
        if (frm.doc.type === 'Notice') {
            frm.set_value('target_type', 'Student Group');
        } else {
            frm.set_value('target_type', null);
            frm.set_value('target_student_group', null);
        }
    }

});