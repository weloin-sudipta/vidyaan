frappe.ui.form.on('Routine Generation', {
    refresh: function(frm) {
        // Set company from user defaults
        if (frm.is_new() && !frm.doc.company) {
            frm.set_value('company', frappe.defaults.get_user_default('Company'));
        }

        // Filter programs by company
        frm.set_query('program', 'programs', function() {
            return {
                filters: { company: frm.doc.company }
            };
        });

        // Add Generate button (only in Draft and before submit)
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Check Readiness'), function() {
                run_readiness_check(frm);
            }, __('Actions'));

            frm.add_custom_button(__('Generate Routine'), function() {
                generate_routine(frm);
            }, __('Actions'));

            frm.change_custom_button_type(__('Generate Routine'), __('Actions'), 'primary');
        }
    },

    company: function(frm) {
        // Re-filter programs when company changes
        frm.set_query('program', 'programs', function() {
            return {
                filters: { company: frm.doc.company }
            };
        });
    }
});

function run_readiness_check(frm) {
    if (!frm.doc.company) {
        frappe.msgprint(__('Please select an Institute first.'));
        return;
    }
    if (!frm.doc.programs || frm.doc.programs.length === 0) {
        frappe.msgprint(__('Please add at least one Program.'));
        return;
    }

    frm.call({
        doc: frm.doc,
        method: 'check_readiness',
        freeze: true,
        freeze_message: __('Running readiness check...'),
        callback: function(r) {
            if (r.message) {
                let data = r.message;
                let html = '<div style="padding: 10px;">';
                html += '<h5 style="margin-bottom: 10px;">Readiness Report</h5>';

                data.results.forEach(function(item) {
                    let color = item.status === 'ok' ? '#28a745' :
                               item.status === 'warning' ? '#ffc107' : '#dc3545';
                    html += `<p style="color: ${color}; margin: 5px 0;">${item.msg}</p>`;
                });

                if (data.sections) {
                    html += `<hr><p><strong>Total sections discovered: ${data.sections}</strong></p>`;
                }

                if (data.ok) {
                    html += '<p style="color: #28a745; font-weight: bold; margin-top: 10px;">🚀 Ready to generate!</p>';
                } else {
                    html += '<p style="color: #dc3545; font-weight: bold; margin-top: 10px;">⛔ Fix the issues above before generating.</p>';
                }

                html += '</div>';

                frm.fields_dict.readiness_html.$wrapper.html(html);
            }
        }
    });
}

function generate_routine(frm) {
    if (!frm.doc.name || frm.is_new()) {
        frappe.msgprint(__('Please save the document first.'));
        return;
    }

    frappe.confirm(
        __('This will generate a new routine and replace any existing slots. Continue?'),
        function() {
            frm.call({
                doc: frm.doc,
                method: 'generate_routine',
                freeze: true,
                freeze_message: __('Generating routine using AI solver... This may take up to {0} seconds.', [frm.doc.solver_timeout || 30]),
                callback: function(r) {
                    frm.reload_doc();
                }
            });
        }
    );
}
