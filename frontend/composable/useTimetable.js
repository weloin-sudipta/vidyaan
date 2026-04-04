// composables/useTimetable.js
import { ref, computed } from 'vue';
import { call } from '~/composable/useFrappeFetch';

export function useTimetable() {
  const activeDay = ref('');
    const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

    const categoryStyles = {
        'Lecture': 'bg-indigo-50 text-indigo-600 border-indigo-100',
        'Lab': 'bg-green-50 text-green-600 border-green-100',
        'Break': 'bg-slate-50 text-slate-400 border-slate-100',
        'Activity': 'bg-amber-50 text-amber-600 border-amber-100'
    };

  function setToday() {
    const today = new Date().getDay();
    const index = today === 0 ? 6 : today - 1;
    activeDay.value = weekDays[index];
  }
  onMounted(() => {
    setToday();
  });

    const timetableData = ref({});
    const isLoading = ref(true);
    const studentGroup = ref('Academic Timetable');

    const showPdfModal = ref(false);
    const isDownloading = ref(false);
    const pdfContentRef = ref(null);

    // ── Computed ────────────────────────────────────────────────────────────────

    const currentDaySchedule = computed(() => {
        return timetableData.value[activeDay.value] || [];
    });

    const uniqueTimeSlots = computed(() => {
        const times = new Set();
        Object.values(timetableData.value).forEach(daySlots => {
            daySlots.forEach(slot => times.add(`${slot.startTime} - ${slot.endTime}`));
        });
        return Array.from(times).sort();
    });

    // ── Helpers ─────────────────────────────────────────────────────────────────

    const getSlot = (day, timeRange) => {
        const daySlots = timetableData.value[day] || [];
        return daySlots.find(s => `${s.startTime} - ${s.endTime}` === timeRange);
    };

    // ── API ──────────────────────────────────────────────────────────────────────

    const fetchSchedule = async () => {
        try {
            const res = await call('vidyaan.api.get_student_schedule');
            if (res?.success) {
                timetableData.value = res.timetable || {};
                if (res.student_group) {
                    studentGroup.value = `Academic Timetable • ${res.student_group}`;
                }
                // If current day has no classes, default to first day that does
                if (!timetableData.value[activeDay.value] || timetableData.value[activeDay.value].length === 0) {
                    const firstDayWithClasses = weekDays.find(d => timetableData.value[d] && timetableData.value[d].length > 0);
                    if (firstDayWithClasses) {
                        activeDay.value = firstDayWithClasses;
                    }
                }
            }
        } catch (err) {
            console.error('Failed to load schedule', err);
        } finally {
            isLoading.value = false;
        }
    };

    // ── PDF ──────────────────────────────────────────────────────────────────────

    const downloadPdf = async () => {
        isDownloading.value = true;
        try {
            const tableHtml = pdfContentRef.value.innerHTML;

            const htmlContent = `
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
              <p class="subtitle">${studentGroup.value}</p>
            </div>
            ${tableHtml}
          </body>
        </html>
      `;

            const res = await call('vidyaan.api_folder.pdf.generate_pdf_from_html', {
                html: htmlContent,
                filename: 'Academic_Timetable.pdf',
                options: JSON.stringify({
                    format: 'A4',
                    landscape: 'True',
                    margin: { top: '15mm', bottom: '15mm', left: '15mm', right: '15mm' }
                })
            });

            if (res?.file_url) {
                window.open(res.file_url, '_blank');
                showPdfModal.value = false;
            }
        } catch (e) {
            console.error('PDF Generate Error', e);
        } finally {
            isDownloading.value = false;
        }
    };

    return {
        // State
        activeDay,
        weekDays,
        categoryStyles,
        timetableData,
        isLoading,
        studentGroup,
        showPdfModal,
        isDownloading,
        pdfContentRef,
        // Computed
        currentDaySchedule,
        uniqueTimeSlots,
        // Methods
        getSlot,
        fetchSchedule,
        downloadPdf,
    };
}