frappe.provide("vidyaan.setup");

frappe.pages["setup-wizard"].on_page_load = function (wrapper) {
	if (frappe.sys_defaults.company) {
		frappe.set_route("desk");
		return;
	}
};

frappe.setup.on("before_load", function () {
	if (
		frappe.boot.setup_wizard_completed_apps?.length &&
		frappe.boot.setup_wizard_completed_apps.includes("vidyaan")
	) {
		return;
	}

	// Remove ERPNext's organization slide — Vidyaan replaces it
	frappe.setup.remove_slide("organization");

	// Remove Frappe's default user slide — Vidyaan's institute slide handles admin creation
	frappe.setup.remove_slide("user");

	// Add the Vidyaan institute setup slide
	vidyaan.setup.slides_settings.forEach(function (slide) {
		frappe.setup.add_slide(slide);
	});
});

vidyaan.setup.slides_settings = [
	{
		name: "vidyaan_institute",
		title: __("Setup Your Institute"),
		icon: "fa fa-university",
		fields: [
			{
				fieldname: "institute_name",
				label: __("Institute Name"),
				fieldtype: "Data",
				placeholder: __("e.g. Delhi Public School"),
				reqd: 1,
			},
			{
				fieldtype: "Section Break",
				label: __("Institute Administrator"),
				description: __(
					"This person will manage the institute. They will only have access to the Vidyaan module."
				),
			},
			{
				fieldname: "admin_name",
				label: __("Admin Full Name"),
				fieldtype: "Data",
				placeholder: __("e.g. Rajesh Kumar"),
				reqd: 1,
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "admin_email",
				label: __("Admin Email") + " (" + __("Login ID") + ")",
				fieldtype: "Data",
				options: "Email",
				placeholder: __("e.g. admin@school.edu"),
				reqd: 1,
			},
			{ fieldtype: "Section Break" },
			{
				fieldname: "admin_password",
				label: __("Admin Password"),
				fieldtype: "Password",
				length: 512,
				reqd: 1,
				description: __("Minimum 8 characters"),
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "confirm_password",
				label: __("Confirm Password"),
				fieldtype: "Password",
				length: 512,
				reqd: 1,
			},
		],

		validate: function () {
			let values = this.values;

			// Validate institute name
			if (!values.institute_name || !values.institute_name.trim()) {
				frappe.msgprint(__("Institute Name is required"));
				return false;
			}

			// Validate admin name
			if (!values.admin_name || !values.admin_name.trim()) {
				frappe.msgprint(__("Admin Full Name is required"));
				return false;
			}

			// Validate email format
			if (!values.admin_email || !validate_email(values.admin_email)) {
				frappe.msgprint(__("Please enter a valid email address"));
				return false;
			}

			// Validate password length
			if (!values.admin_password || values.admin_password.length < 8) {
				frappe.msgprint(__("Password must be at least 8 characters long"));
				return false;
			}

			// Validate password match
			if (values.admin_password !== values.confirm_password) {
				frappe.msgprint(__("Passwords do not match"));
				return false;
			}

			// Validate admin email is not Administrator or Guest
			let email_lower = values.admin_email.toLowerCase();
			if (email_lower === "administrator" || email_lower === "guest") {
				frappe.msgprint(
					__("Cannot use '{0}' as admin email", [values.admin_email])
				);
				return false;
			}

			return true;
		},
	},
];
