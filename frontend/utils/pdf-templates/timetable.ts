/**
 * Standalone HTML template renderer for the academic timetable PDF.
 *
 * Extracted verbatim from `composable/useTimetable.ts` so the composable can
 * stay focused on data and request orchestration. This is a pure function:
 * given the table HTML and the student-group label, it returns a
 * fully-formed HTML document string ready for the Frappe PDF service.
 */
export interface TimetableHtmlInput {
  /** Inner HTML of the rendered timetable grid (the table element). */
  tableHtml: string
  /** Subtitle line shown under the document header. */
  studentGroup: string
}

export function renderTimetableHtml({ tableHtml, studentGroup }: TimetableHtmlInput): string {
  return `
        <html>
          <head>
            <style>
              @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
              body {
                font-family: 'Inter', sans-serif;
                color: #1e293b;
                padding: 20px;
                background: #ffffff;
              }
              .header-wrapper {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #f1f5f9;
              }
              h1 {
                text-align: center;
                color: #0f172a;
                margin-bottom: 5px;
                font-weight: 800;
                font-size: 24px;
                letter-spacing: -0.5px;
              }
              p.subtitle {
                text-align: center;
                color: #64748b;
                font-size: 11px;
                margin-top: 0;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 2px;
              }
              table {
                width: 100%;
                border-collapse: collapse;
                font-size: 11px;
                border: 1px solid #e2e8f0;
              }
              th, td {
                border: 1px solid #e2e8f0;
                padding: 12px 6px;
                text-align: center;
                vertical-align: middle;
              }
              th {
                background-color: #f8fafc;
                color: #475569;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 800;
                font-size: 9px;
              }
              td:first-child {
                font-weight: 800;
                color: #334155;
                background-color: #f8fafc;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-size: 10px;
              }
              .cell-sub {
                font-weight: 800;
                color: #3730a3;
                display: block;
                margin-bottom: 4px;
                font-size: 12px;
              }
              .cell-tea {
                color: #6366f1;
                font-size: 10px;
                display: block;
                margin-bottom: 3px;
                font-weight: 600;
              }
              .cell-room {
                color: #64748b;
                font-size: 8px;
                text-transform: uppercase;
                font-weight: 800;
                letter-spacing: 1px;
                display: inline-block;
                padding: 2px 4px;
                background: #f1f5f9;
                border-radius: 4px;
              }
              .fa-user { display: none; }
              .flex { display: block !important; }
              .p-5, .p-3, .p-4 { padding: 12px 6px !important; }
              .bg-indigo-50\\/80 { background: #e0e7ff !important; padding: 10px !important; border-radius: 8px; }
            </style>
          </head>
          <body>
            <div class="header-wrapper">
              <h1>Vidyaan Academic Routine</h1>
              <p class="subtitle">${studentGroup}</p>
            </div>
            ${tableHtml}
          </body>
        </html>
      `
}
