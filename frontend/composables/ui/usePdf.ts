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

import { ref, type Ref } from 'vue'
import { parseFrappeError } from '~/composables/api/parseFrappeError'
import type { PdfGenerationResult } from '~/composables/api/types'

export interface PdfTemplateOptions {
  format?: string
  landscape?: string | boolean
  margin?: { top?: string; bottom?: string; left?: string; right?: string }
  [key: string]: unknown
}

export type PdfGeneratorFn = () => Promise<PdfGenerationResult | null>

export interface UsePdfReturn {
  loading: Ref<boolean>
  error: Ref<string | null>
  generateAdmitCard: (examType?: string) => Promise<PdfGenerationResult | null>
  generateFromTemplate: (
    templateName: string,
    data?: Record<string, unknown>,
    filename?: string,
    options?: PdfTemplateOptions
  ) => Promise<PdfGenerationResult | null>
  generateFromHtml: (
    html: string,
    filename?: string,
    options?: PdfTemplateOptions
  ) => Promise<PdfGenerationResult | null>
  openPdf: (generatorFn: PdfGeneratorFn) => Promise<PdfGenerationResult | null>
}

export const usePdf = (): UsePdfReturn => {
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  // ── Internal fetch wrapper ────────────────────────────────────────────────
  // Uses raw $fetch (not `call`) because it needs the custom error parser
  // that decodes Frappe's `_server_messages` JSON-string envelope.
  const _call = async (
    method: string,
    params: Record<string, unknown> = {}
  ): Promise<PdfGenerationResult | null> => {
    loading.value = true
    error.value = null

    try {
      const res = await $fetch<{ message?: PdfGenerationResult } & PdfGenerationResult>(
        '/api/method/' + method,
        {
          method: 'POST',
          body: params,
        }
      )

      // Frappe wraps response in { message: ... }
      return res?.message ?? res ?? null
    } catch (err) {
      const msg = parseFrappeError(err, 'PDF generation failed')
      error.value = msg
      console.error(`[usePdf] ${method} failed:`, msg)
      return null
    } finally {
      loading.value = false
    }
  }

  // ── 1. Admit Card ──────────────────────────────────────────────────────────
  /**
   * Generate an admit card PDF for the logged-in student.
   */
  const generateAdmitCard = (examType: string = ''): Promise<PdfGenerationResult | null> =>
    _call('vidyaan.api_folder.pdf.generate_admit_card_pdf', {
      exam_type: examType,
    })

  // ── 2. Template-based PDF ─────────────────────────────────────────────────
  /**
   * Render a named HTML template with data, produce a PDF.
   *
   * Available templates (in pdf-service/templates/):
   *   - admit_card.html
   *   - certificate.html
   *   - notice.html
   */
  const generateFromTemplate = (
    templateName: string,
    data: Record<string, unknown> = {},
    filename: string = 'document.pdf',
    options: PdfTemplateOptions = {}
  ): Promise<PdfGenerationResult | null> =>
    _call('vidyaan.api_folder.pdf.generate_pdf_from_template', {
      template_name: templateName,
      data: JSON.stringify(data),
      filename,
      options: JSON.stringify(options),
    })

  // ── 3. Raw HTML PDF ───────────────────────────────────────────────────────
  /**
   * Convert any raw HTML string to PDF.
   */
  const generateFromHtml = (
    html: string,
    filename: string = 'document.pdf',
    options: PdfTemplateOptions = {}
  ): Promise<PdfGenerationResult | null> =>
    _call('vidyaan.api_folder.pdf.generate_pdf_from_html', {
      html,
      filename,
      options: JSON.stringify(options),
    })

  // ── Helper: open PDF in new tab ────────────────────────────────────────────
  /**
   * Generate and immediately open the PDF in a new browser tab.
   * Pass any generator function and its args.
   *
   * @example
   *   await openPdf(() => generateAdmitCard("Mid Term"))
   */
  const openPdf = async (generatorFn: PdfGeneratorFn): Promise<PdfGenerationResult | null> => {
    const result = await generatorFn()
    if (result?.file_url) {
      window.open(result.file_url, '_blank')
    }
    return result
  }

  return {
    loading,
    error,
    generateAdmitCard,
    generateFromTemplate,
    generateFromHtml,
    openPdf,
  }
}
