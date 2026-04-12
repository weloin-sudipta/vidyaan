// Vidyaan custom setup wizard is disabled — using the default Frappe/ERPNext setup wizard.
// This file is retained for the real-time update prompt below.

// Real-time update prompt
frappe.realtime.on('server_restart', function() {
    frappe.msgprint({
        title: __('Update Available'),
        message: __('A new update has been installed! Please refresh the page to apply the latest features and fixes.'),
        indicator: 'blue',
        primary_action: {
            label: __('Refresh Now'),
            action: () => window.location.reload()
        }
    });
});

