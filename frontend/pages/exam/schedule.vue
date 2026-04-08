<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans text-slate-900 dark:text-slate-100 transition-colors">
    <div class="max-w-[1440px] mx-auto space-y-6">

      <HeroHeader
        title="Exam Roadmap"
        :subtitle="`Academic Session ${studentYear}`"
        icon="fa fa-calendar-check-o"
      />

      <div v-if="loading" class="space-y-4">
        <UiSkeleton height="h-24" v-for="i in 3" :key="i" class="rounded-[2rem]" />
      </div>

      <div v-else class="space-y-4 animate-in">

        <div v-for="(group, type) in groupedExams" :key="type">

          <!-- GROUP HEADER -->
          <div
            @click="toggleGroup(type)"
            class="cursor-pointer bg-white dark:bg-slate-900 rounded-[2rem] p-4 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none hover:border-rose-300 dark:hover:border-rose-500/50 transition-all flex items-center justify-between group"
          >

            <div class="flex items-center gap-4">

              <div
                class="w-12 h-12 bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 rounded-2xl flex items-center justify-center text-xl transition-colors group-hover:bg-rose-600 group-hover:text-white dark:group-hover:bg-rose-500"
              >
                <i :class="expandedGroups.includes(type) ? 'fa fa-folder-open' : 'fa fa-folder'"></i>
              </div>

              <div>
                <h2 class="text-xl font-black text-slate-800 dark:text-slate-200 tracking-tight transition-colors">
                  {{ type }} <span>{{ group.exams.length }} Subjects Scheduled</span>
                </h2>

                <p class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">
                  {{ group.start_date }} - {{ group.end_date }}
                </p>
              </div>

              <!-- <div>
                <button
                  @click.stop="downloadHallTicket(type)"
                  :disabled="pdfLoading"
                  class="hidden md:flex px-5 py-2.5 bg-slate-900 dark:bg-rose-600 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-rose-600 dark:hover:bg-rose-500 transition-all shadow-md dark:shadow-none items-center gap-2 disabled:opacity-60 disabled:cursor-wait"
                >
                  <i :class="pdfLoading ? 'fa fa-spinner fa-spin' : 'fa fa-download'"></i>
                  {{ pdfLoading ? 'Generating…' : 'Hall Ticket' }}
                </button>
              </div> -->

            </div>

            <div class="flex items-center gap-4">
              <div
                class="text-slate-300 dark:text-slate-600 transition-transform duration-300"
                :class="{ 'rotate-180': expandedGroups.includes(type) }"
              >
                <i class="fa fa-chevron-down"></i>
              </div>
            </div>

          </div>

          <!-- SUBJECT LIST -->
          <transition name="expand">
            <div v-if="expandedGroups.includes(type)" class="overflow-hidden">

              <div
                class="grid grid-cols-1 gap-3 mt-3 ml-4 md:ml-12 border-l-2 border-slate-100 dark:border-slate-800 pl-4 md:pl-8 pb-4 transition-colors"
              >

                <div
                  v-for="exam in group.exams"
                  :key="exam.id"
                  class="bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm rounded-[1.5rem] p-5 border border-slate-100 dark:border-slate-700/50 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:shadow-md dark:hover:shadow-none transition-all"
                >

                  <div class="flex items-center gap-4">

                    <div class="text-center min-w-[50px]">
                      <span class="block text-xs font-black text-rose-500 dark:text-rose-400 uppercase transition-colors">
                        {{ exam.month }}
                      </span>

                      <span class="text-2xl font-black text-slate-800 dark:text-slate-200 transition-colors">
                        {{ exam.day }}
                      </span>
                    </div>

                    <div>
                      <h4 class="font-black text-slate-700 dark:text-slate-300 text-base transition-colors">
                        {{ exam.subject }}
                      </h4>

                      <div class="flex gap-4 mt-1">
                        <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase transition-colors">
                          <i class="fa fa-clock-o mr-1"></i>{{ exam.time }}
                        </span>

                        <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase transition-colors">
                          <i class="fa fa-map-marker mr-1"></i>{{ exam.room }}
                        </span>
                      </div>
                    </div>

                  </div>

                  <span
                    class="text-[10px] font-black px-3 py-1 bg-slate-100 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 rounded-full uppercase self-start md:self-center transition-colors"
                  >
                    {{ exam.dayName }}
                  </span>

                </div>

              </div>

            </div>
          </transition>

        </div>

        <div
          v-if="Object.keys(groupedExams).length === 0"
          class="text-center py-20 text-slate-400 dark:text-slate-500 font-bold uppercase text-sm tracking-widest transition-colors"
        >
          No scheduled exams found.
        </div>

      </div>

    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════
       PDF PREVIEW MODAL
  ════════════════════════════════════════════════════════ -->
  <teleport to="body">
    <transition name="modal-fade">
      <div
        v-if="pdfModal.show"
        class="pdf-overlay"
        @click.self="closePdfModal"
      >
        <div class="pdf-panel">

          <!-- Modal header -->
          <div class="pdf-panel-header">
            <div class="pdf-panel-title">
              <i class="fa fa-file-pdf-o mr-2 text-rose-400"></i>
              <span>Hall Ticket</span>
              <span class="pdf-panel-subtitle">{{ pdfModal.examType }}</span>
            </div>

            <div class="pdf-panel-actions">
              <!-- Download button -->
              <a
                :href="pdfModal.blobUrl"
                :download="`HallTicket_${pdfModal.examType?.replace(/\s+/g,'_')}.pdf`"
                class="pdf-btn pdf-btn-download"
                title="Download PDF"
              >
                <i class="fa fa-download mr-1"></i> Download
              </a>

              <!-- Close button -->
              <button
                @click="closePdfModal"
                class="pdf-btn pdf-btn-close"
                title="Close"
              >
                <i class="fa fa-times"></i>
              </button>
            </div>
          </div>

          <!-- Embedded PDF viewer — uses blob URL to bypass X-Frame-Options -->
          <div class="pdf-viewer-wrap">
            <iframe
              v-if="pdfModal.blobUrl"
              :src="pdfModal.blobUrl"
              class="pdf-iframe"
              type="application/pdf"
              title="Hall Ticket Preview"
            ></iframe>
          </div>

        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import HeroHeader from "~/components/ui/HeroHeader.vue";
import { useExams } from "~/composables/useExaminations";
import { usePdf } from "~/composables/usePdf";
import { useToast } from "~/composables/useToast";

const { addToast } = useToast();
const { generateAdmitCard, loading: pdfLoading, error: pdfError } = usePdf();
const config = useRuntimeConfig();

useSeoMeta({
  title: `Exam Schedule - ${config.public.appName}`,
});

const studentYear = ref("2025-26");
const confirmedExams = ref([]);
const expandedGroups = ref([]);
const loading = ref(true);

/* PDF modal state */
const pdfModal = ref({ show: false, fileUrl: "", blobUrl: "", examType: "" });

const closePdfModal = () => {
  // Revoke the blob URL to free memory
  if (pdfModal.value.blobUrl) {
    URL.revokeObjectURL(pdfModal.value.blobUrl);
  }
  pdfModal.value = { show: false, fileUrl: "", blobUrl: "", examType: "" };
};

/* GROUP EXAMS BY TYPE */
const groupedExams = computed(() => {
  return confirmedExams.value.reduce((groups, exam) => {
    const type = exam.exam_group;

    if (!groups[type]) {
      groups[type] = {
        start_date: exam.start_date,
        end_date: exam.end_date,
        exams: [],
      };
    }

    groups[type].exams.push(exam);

    return groups;
  }, {});
});

/* TOGGLE GROUP */
const toggleGroup = (type) => {
  const index = expandedGroups.value.indexOf(type);

  if (index > -1) {
    expandedGroups.value.splice(index, 1);
  } else {
    expandedGroups.value.push(type);
  }
};

/* DOWNLOAD HALL TICKET — show inline modal, auto-download silently */
const downloadHallTicket = async (type) => {
  const result = await generateAdmitCard(type);

  if (!result?.file_url) {
    if (pdfError.value) addToast(`Failed to generate Hall Ticket: ${pdfError.value}`, 'error');
    return;
  }

  const fileUrl = result.file_url; // e.g. /files/admit_card_xxx.pdf

  // Fetch the PDF binary through our dev proxy (/files → Frappe).
  // Blob URLs bypass X-Frame-Options: deny — Frappe blocks direct iframes.
  let blobUrl = "";
  try {
    const resp = await fetch(fileUrl, { credentials: "include" });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const blob = await resp.blob();
    blobUrl = URL.createObjectURL(blob);
  } catch (e) {
    console.error("[PDF] Blob fetch failed:", e);
    // Fallback: at least open in new tab
    window.open(fileUrl, "_blank", "noopener");
    return;
  }

  // 1️⃣  Show embedded viewer (blob URL has no X-Frame-Options restriction)
  pdfModal.value = { show: true, fileUrl, blobUrl, examType: type };

  // 2️⃣  Auto-download silently — no new tab
  const a = document.createElement("a");
  a.href = blobUrl;
  a.download = `HallTicket_${type.replace(/\s+/g, "_")}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  // Do NOT revoke blobUrl here — the iframe still needs it (revoked on modal close)
};

/* FORMAT TIME */
const formatTime = (timeStr) => {
  if (!timeStr) return "";

  const [h, m] = timeStr.split(":");
  const hour = parseInt(h);

  const ampm = hour >= 12 ? "PM" : "AM";
  const displayHour = hour % 12 || 12;

  return `${displayHour}:${m} ${ampm}`;
};

onMounted(async () => {
  try {
    const data = await useExams();

    if (!Array.isArray(data) || !data.length) return;

    studentYear.value = data[0].academic_year;

    confirmedExams.value = data.map((item, index) => {
      const dateObj = new Date(item.date);

      return {
        id: item.exam_id || index,
        subject: item.subject,

        month: dateObj
          .toLocaleString("default", { month: "short" })
          .toUpperCase(),

        day: dateObj.getDate().toString().padStart(2, "0"),

        dayName: dateObj
          .toLocaleString("default", { weekday: "long" })
          .toUpperCase(),

        exam_group: item.exam_type,

        time: `${formatTime(item.start_time)} - ${formatTime(item.end_time)}`,

        room: item.room,

        start_date: new Date(item.exam_start_date).toLocaleDateString("en-IN", {
          day: "2-digit",
          month: "short",
        }),

        end_date: new Date(item.exam_end_date).toLocaleDateString("en-IN", {
          day: "2-digit",
          month: "short",
        }),
      };
    });

    /* AUTO EXPAND FIRST GROUP */
    const firstGroup = Object.keys(groupedExams.value)[0];

    if (firstGroup) expandedGroups.value.push(firstGroup);
  } catch (error) {
    console.error("Error loading exams:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
/* ── Exam list transitions ─────────────────────────────── */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease-in-out;
  max-height: 1000px;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

.animate-in {
  animation: slideUp 0.5s ease-out forwards;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── PDF Modal overlay ─────────────────────────────────── */
.pdf-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(2, 6, 23, 0.7);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* Modal panel */
.pdf-panel {
  @apply bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 shadow-2xl;
  border-radius: 20px;
  overflow: hidden;
  width: 100%;
  max-width: 860px;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

/* Panel top bar */
.pdf-panel-header {
  @apply bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-white/10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  flex-shrink: 0;
}

.pdf-panel-title {
  @apply text-slate-800 dark:text-slate-100;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 700;
}

.pdf-panel-subtitle {
  @apply text-slate-500 dark:text-slate-400 bg-slate-200/50 dark:bg-white/5;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  margin-left: 4px;
}

.pdf-panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pdf-btn {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  border: none;
  text-decoration: none;
  transition: all 0.15s;
}

.pdf-btn-download {
  background: linear-gradient(135deg, #1d4ed8, #4338ca);
  color: white;
}
.pdf-btn-download:hover {
  background: linear-gradient(135deg, #1e40af, #3730a3);
  transform: translateY(-1px);
}

.pdf-btn-close {
  @apply bg-slate-200 dark:bg-white/5 text-slate-500 dark:text-slate-400 hover:bg-rose-500 hover:text-white transition-colors;
  font-size: 14px;
  width: 32px;
  height: 32px;
  padding: 0;
  justify-content: center;
}

/* iframe fills the rest */
.pdf-viewer-wrap {
  @apply bg-slate-100 dark:bg-slate-800 border-none;
  flex: 1;
  overflow: hidden;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

/* ── Modal open/close animation ───────────────────────── */
.modal-fade-enter-active {
  animation: modalIn 0.25s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
.modal-fade-leave-active {
  animation: modalOut 0.2s ease forwards;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.94) translateY(16px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes modalOut {
  from { opacity: 1; transform: scale(1); }
  to   { opacity: 0; transform: scale(0.96) translateY(8px); }
}
</style>