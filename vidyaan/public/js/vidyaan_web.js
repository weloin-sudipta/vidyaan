// Vidyaan web admin – sidebar toggle + user dropdown
(function () {
	function ready(fn) {
		if (document.readyState !== "loading") fn();
		else document.addEventListener("DOMContentLoaded", fn);
	}

	ready(function () {
		var shell = document.querySelector(".vidyaan-shell");
		if (!shell) return;

		// Sidebar toggle (mobile)
		var toggle = shell.querySelector(".vd-sidebar-toggle");
		var backdrop = shell.querySelector(".vidyaan-backdrop");
		if (toggle) {
			toggle.addEventListener("click", function () {
				shell.classList.toggle("is-sidebar-open");
			});
		}
		if (backdrop) {
			backdrop.addEventListener("click", function () {
				shell.classList.remove("is-sidebar-open");
			});
		}

		// User dropdown
		var userMenu = shell.querySelector(".vd-user-menu");
		if (userMenu) {
			var btn = userMenu.querySelector(".vd-user-btn");
			btn.addEventListener("click", function (e) {
				e.stopPropagation();
				userMenu.classList.toggle("is-open");
			});
			document.addEventListener("click", function (e) {
				if (!userMenu.contains(e.target)) userMenu.classList.remove("is-open");
			});
		}
	});
})();
