frappe.ui.form.on('Publication', {
    refresh: function(frm) {
        // Dynamic field styling or actions could go here
        if (frm.doc.docstatus === 1 && frm.doc.status === "Pending") {
            frm.add_custom_button(__('Approve'), () => {
                frm.set_value('status', 'Approved');
                frm.save('Submit');
            }, __("Actions"));
            
            frm.add_custom_button(__('Reject'), () => {
                frm.set_value('status', 'Rejected');
                frm.save('Save');
            }, __("Actions"));
        }
    },
    type: function(frm) {
        // Triggered when type changes
        if(frm.doc.type === 'Notice') {
            frm.set_value('target_type', 'Student Group');
        } else {
            frm.set_value('target_type', '');
            frm.set_value('target_student_group', '');
        }
    }
});
