import { ref } from "vue";
import { createResource } from "./useFrappeFetch";
import { useToast } from "./useToast";

export const useLibraryAdmin = () => {
  const { addToast } = useToast();
  const loading = ref(false);
  const error = ref(null);

  const stats = ref(null);
  const inventory = ref([]);
  const issues = ref([]);
  const requests = ref([]);
  const members = ref([]);

  const _fetch = async (url, params = {}) => {
    const resource = createResource({ url });
    return await resource.fetch(params);
  };

  const _submit = async (url, params = {}) => {
    const resource = createResource({ url });
    return await resource.submit(params);
  };

  // ─── Data fetchers ──────────────────────────────────────────────────────────

  const fetchStats = async () => {
    try {
      stats.value = await _fetch("vidyaan.library.api.get_library_stats");
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  };

  const fetchInventory = async () => {
    loading.value = true;
    try {
      inventory.value = await _fetch("vidyaan.library.api.get_inventory");
    } catch (err) {
      error.value = err.message || "Failed to load inventory";
    } finally {
      loading.value = false;
    }
  };

  const fetchIssues = async (status = null) => {
    loading.value = true;
    try {
      const params = status ? { status } : {};
      issues.value = await _fetch("vidyaan.library.api.get_all_issues", params);
    } catch (err) {
      error.value = err.message || "Failed to load issues";
    } finally {
      loading.value = false;
    }
  };

  const fetchRequests = async (status = null) => {
    loading.value = true;
    try {
      const params = status ? { status } : {};
      requests.value = await _fetch("vidyaan.library.api.get_all_requests", params);
    } catch (err) {
      error.value = err.message || "Failed to load requests";
    } finally {
      loading.value = false;
    }
  };

  const fetchMembers = async () => {
    loading.value = true;
    try {
      members.value = await _fetch("vidyaan.library.api.get_all_members");
    } catch (err) {
      error.value = err.message || "Failed to load members";
    } finally {
      loading.value = false;
    }
  };

  // ─── Actions ────────────────────────────────────────────────────────────────

  const returnBook = async (issueName) => {
    try {
      const res = await _submit("vidyaan.library.api.return_book", { issue_name: issueName });
      const fine = res?.fine_amount || 0;
      addToast(fine > 0 ? `Book returned. Fine: ₹${fine}` : "Book returned successfully.", "success");
      return res;
    } catch (err) {
      addToast(_parseError(err, "Failed to return book"), "error");
    }
  };

  const approveRequest = async (requestName) => {
    try {
      await _submit("vidyaan.library.api.approve_request", { request_name: requestName });
      addToast("Request approved.", "success");
    } catch (err) {
      addToast(_parseError(err, "Failed to approve request"), "error");
    }
  };

  const rejectRequest = async (requestName, remarks = "") => {
    try {
      await _submit("vidyaan.library.api.reject_request", { request_name: requestName, remarks });
      addToast("Request rejected.", "success");
    } catch (err) {
      addToast(_parseError(err, "Failed to reject request"), "error");
    }
  };

  const approveRenewal = async (issueName) => {
    try {
      const res = await _submit("vidyaan.library.api.approve_renewal", { issue_name: issueName });
      addToast(`Renewal approved. New due: ${res?.new_due_date || "extended"}`, "success");
      return res;
    } catch (err) {
      addToast(_parseError(err, "Failed to approve renewal"), "error");
    }
  };

  const issueFromRequest = async (requestName) => {
    try {
      const res = await _submit("vidyaan.library.api.issue_from_request", { request_name: requestName });
      addToast("Book issued successfully.", "success");
      return res;
    } catch (err) {
      addToast(_parseError(err, "Failed to issue book"), "error");
    }
  };

  return {
    loading, error, stats, inventory, issues, requests, members,
    fetchStats, fetchInventory, fetchIssues, fetchRequests, fetchMembers,
    returnBook, approveRequest, rejectRequest, approveRenewal, issueFromRequest,
  };
};

function _parseError(err, fallback) {
  if (err?.data?._server_messages) {
    try {
      const msgs = JSON.parse(err.data._server_messages);
      return JSON.parse(msgs[0]).message;
    } catch { /* ignore */ }
  }
  return err?.message || fallback;
}
