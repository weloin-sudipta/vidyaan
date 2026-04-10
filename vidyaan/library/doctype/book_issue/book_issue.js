frappe.ui.form.on('Book Issue', {
	setup: function(frm) {
		// Filter book copy dropdown to only show available copies for the selected book
		frm.set_query("book_copy", function() {
			if (!frm.doc.book) {
				frappe.msgprint(__("Please select a Book first to see its available copies."));
				return { filters: { name: ["=", ""] } }; // Return nothing
			}
			return {
				filters: {
					book: frm.doc.book,
					status: "Available"
				}
			};
		});
	},

	book: function(frm) {
		// Clear previously selected copy if the book changes
		if (frm.doc.book_copy) {
			frm.set_value("book_copy", "");
		}
	}
});
