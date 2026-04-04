/**
 * usePdf — Reusable composable for PDF generation via Vidyaan PDF Service
 *
 * Usage:
 *   const { generateAdmitCard, generateFromTemplate, generateFromHtml, loading, error } = usePdf()
 *
 *   // Admit card (high-level, uses server-side data)
 *   const result = await generateAdmitCard("Mid Term")
 *   window.open(result.file_url, "_blank")
 *
 *   // Template-based (notice, certificate etc)
 *   const result = await generateFromTemplate("certificate.html", { name: "John", course: "CS" }, "cert.pdf")
 *
 *   // Raw HTML (full control)
 *   const result = await generateFromHtml("<h1>Hello</h1>", "custom.pdf")
 */

import { ref } from "vue";

export const usePdf = () => {
  const loading = ref(false);
  const error = ref(null);

  // ── Internal fetch wrapper ────────────────────────────────────────────────
  const _call = async (method, params = {}) => {
    loading.value = true;
    error.value = null;

    try {
      const res = await $fetch("/api/method/" + method, {
        method: "POST",
        body: params,
      });

      // Frappe wraps response in { message: ... }
      return res?.message ?? res;
    } catch (err) {
      // Frappe error shape: err.data._server_messages (JSON array of message strings)
      //                  or err.data.message
      //                  or err.message
      let msg = "PDF generation failed";
      try {
        const serverMsgs = err?.data?._server_messages;
        if (serverMsgs) {
          // _server_messages is a JSON string containing array of JSON strings
          const parsed = JSON.parse(serverMsgs);
          const first = JSON.parse(parsed[0]);
          msg = first?.message || first || msg;
        } else {
          msg =
            err?.data?.message ||
            err?.data?.exc_type ||
            err?.message ||
            msg;
        }
      } catch (_) {
        msg = err?.message || msg;
      }

      error.value = msg;
      console.error(`[usePdf] ${method} failed:`, msg);
      return null;
    } finally {
      loading.value = false;
    }
  };

  // ── 1. Admit Card ──────────────────────────────────────────────────────────
  /**
   * Generate an admit card PDF for the logged-in student.
   * @param {string} examType - e.g. "Mid Term", "Final Exam"
   * @returns {{ file_url, student_name, exam_type } | null}
   */
  const generateAdmitCard = (examType = "") =>
    _call("vidyaan.api_folder.pdf.generate_admit_card_pdf", {
      exam_type: examType,
    });

  // ── 2. Template-based PDF ─────────────────────────────────────────────────
  /**
   * Render a named HTML template with data, produce a PDF.
   *
   * Available templates (in pdf-service/templates/):
   *   - admit_card.html
   *   - certificate.html
   *   - notice.html
   *
   * @param {string} templateName
   * @param {object} data          - key/value pairs for {{variable}} substitution
   * @param {string} filename      - output filename
   * @param {object} options       - { format, landscape }
   * @returns {{ file_url } | null}
   */
  const generateFromTemplate = (templateName, data = {}, filename = "document.pdf", options = {}) =>
    _call("vidyaan.api_folder.pdf.generate_pdf_from_template", {
      template_name: templateName,
      data: JSON.stringify(data),
      filename,
      options: JSON.stringify(options),
    });

  // ── 3. Raw HTML PDF ───────────────────────────────────────────────────────
  /**
   * Convert any raw HTML string to PDF.
   * @param {string} html
   * @param {string} filename
   * @param {object} options   - { format, landscape }
   * @returns {{ file_url } | null}
   */
  const generateFromHtml = (html, filename = "document.pdf", options = {}) =>
    _call("vidyaan.api_folder.pdf.generate_pdf_from_html", {
      html,
      filename,
      options: JSON.stringify(options),
    });

  // ── Helper: open PDF in new tab ────────────────────────────────────────────
  /**
   * Generate and immediately open the PDF in a new browser tab.
   * Pass any generator function and its args.
   *
   * @example
   *   await openPdf(() => generateAdmitCard("Mid Term"))
   */
  const openPdf = async (generatorFn) => {
    const result = await generatorFn();
    if (result?.file_url) {
      window.open(result.file_url, "_blank");
    }
    return result;
  };

  return {
    loading,
    error,
    generateAdmitCard,
    generateFromTemplate,
    generateFromHtml,
    openPdf,
  };
};
