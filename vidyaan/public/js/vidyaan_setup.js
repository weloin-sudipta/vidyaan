// Vidyaan Institute Setup — Full-page wizard (replaces ERPNext setup wizard)
$(document).on('app_ready', function () {
    if (frappe.session.user !== 'Guest' && parseInt(frappe.boot.vidyaan_setup_complete) === 0) {
        show_vidyaan_setup_wizard();
    }
});

function show_vidyaan_setup_wizard() {
    // Hide the desk entirely and show our full-page wizard
    $('#body, #page-container, .page-container').hide();
    $('header.navbar').hide();

    let wrapper = $(`
        <div id="vidyaan-setup-wizard" style="
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            z-index: 10000;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex; align-items: center; justify-content: center;
            font-family: var(--font-stack);
        ">
            <div style="
                background: white;
                border-radius: 16px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.25);
                padding: 48px;
                width: 100%;
                max-width: 520px;
                margin: 20px;
            ">
                <div style="text-align: center; margin-bottom: 32px;">
                    <h1 style="
                        font-size: 28px;
                        font-weight: 700;
                        color: #1a1a2e;
                        margin: 0 0 8px 0;
                    ">Welcome to Vidyaan</h1>
                    <p style="
                        color: #6b7280;
                        font-size: 15px;
                        margin: 0;
                    ">Enter your institute name to get started</p>
                </div>

                <div id="vidyaan-setup-form"></div>

                <div id="vidyaan-setup-error" style="
                    display: none;
                    background: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    padding: 12px 16px;
                    margin-top: 16px;
                    color: #dc2626;
                    font-size: 13px;
                "></div>

                <button id="vidyaan-setup-btn" style="
                    width: 100%;
                    margin-top: 24px;
                    padding: 14px 24px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: opacity 0.2s;
                " onmouseover="this.style.opacity='0.9'"
                   onmouseout="this.style.opacity='1'"
                >Complete Setup</button>

                <p style="
                    text-align: center;
                    margin-top: 16px;
                    color: #9ca3af;
                    font-size: 12px;
                ">Default currency: INR &bull; Country: India</p>
            </div>
        </div>
    `).appendTo('body');

    // Render the Frappe form field inside the form container
    let form_area = wrapper.find('#vidyaan-setup-form');
    let institute_field = frappe.ui.form.make_control({
        df: {
            fieldtype: 'Data',
            fieldname: 'institute_name',
            label: 'Institute Name',
            placeholder: 'e.g. Delhi Public School',
            reqd: 1,
        },
        parent: form_area,
        render_input: true,
    });
    institute_field.refresh();

    // Style the rendered field
    form_area.find('.form-group').css('margin-bottom', '0');
    form_area.find('.control-input input').css({
        'padding': '12px 14px',
        'font-size': '15px',
        'border-radius': '8px',
        'border': '1.5px solid #d1d5db',
    });

    let error_div = wrapper.find('#vidyaan-setup-error');
    let btn = wrapper.find('#vidyaan-setup-btn');

    btn.on('click', function () {
        let institute_name = (institute_field.get_value() || '').trim();

        error_div.hide();

        if (!institute_name) {
            error_div.text('Please enter your institute name.').show();
            return;
        }

        btn.prop('disabled', true).text('Setting up...');

        frappe.call({
            method: 'vidyaan.setup.wizard.complete_setup',
            args: { institute_name: institute_name },
            callback: function (r) {
                if (!r.exc) {
                    btn.text('Setup Complete!').css('background', '#16a34a');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    let msg = (r._server_messages || '');
                    try {
                        msg = JSON.parse(msg);
                        if (Array.isArray(msg)) msg = msg.map(m => {
                            try { return JSON.parse(m).message; } catch(e) { return m; }
                        }).join('. ');
                    } catch(e) {}
                    error_div.text(msg || 'Setup failed. Please check the error log or try again.').show();
                    btn.prop('disabled', false).text('Complete Setup');
                }
            },
            error: function () {
                error_div.text('Setup failed. Please check the error log or try again.').show();
                btn.prop('disabled', false).text('Complete Setup');
            }
        });
    });

    // Allow Enter key to submit
    form_area.on('keypress', function (e) {
        if (e.which === 13) {
            btn.trigger('click');
        }
    });

    // Prevent navigation away
    frappe.router.on('change', function () {
        if (parseInt(frappe.boot.vidyaan_setup_complete) === 0) {
            return false;
        }
    });
}

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
