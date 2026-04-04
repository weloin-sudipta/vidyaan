<template>
    <main class="flex-1 overflow-y-auto p-6 lg:p-10 custom-scrollbar bg-transparent transition-colors duration-300">
        <!-- HERO -->
        <div
            class="relative bg-white dark:bg-slate-900 rounded-[2.5rem] overflow-hidden shadow-sm dark:shadow-none border border-slate-100 dark:border-slate-800 mb-10">
            <!-- BG BLOBS -->
            <div
                class="absolute -right-20 -top-20 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-3xl pointer-events-none">
            </div>
            <div
                class="absolute -left-10 -bottom-20 w-72 h-72 bg-purple-500/5 rounded-full blur-3xl pointer-events-none">
            </div>

            <div class="relative z-10 flex flex-col lg:flex-row justify-between items-center gap-8 p-8 lg:p-12">
                <div class="max-w-xl text-center lg:text-left">
                    <!-- EYEBROW -->
                    <div
                        class="inline-flex items-center gap-2 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 px-4 py-1.5 rounded-full mb-6">
                        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
                        <span class="text-indigo-500 text-[10px] font-black uppercase tracking-[0.25em]">Student
                            Overview</span>
                    </div>

                    <!-- HEADING -->
                    <h1
                        class="text-3xl lg:text-5xl font-black text-slate-900 dark:text-white leading-tight mb-4 tracking-tight">
                        Welcome back, <br />
                        <span
                            class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-400">
                            {{ dashboardData?.student_info?.name || "Scholar" }}!
                        </span>
                    </h1>

                    <p class="text-slate-400 text-sm font-medium leading-relaxed mb-8">
                        Your academic progress this week is looking excellent.
                    </p>

                    <!-- QUICK STAT CHIPS -->
                    <div class="flex flex-wrap justify-center lg:justify-start gap-3">
                        <div
                            class="flex items-center gap-2 bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 px-4 py-2 rounded-2xl">
                            <div
                                class="w-7 h-7 bg-indigo-100 dark:bg-indigo-500/20 rounded-xl flex items-center justify-center">
                                <i class="fa fa-graduation-cap text-indigo-500 text-[10px]"></i>
                            </div>
                            <div>
                                <p
                                    class="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none mb-0.5">
                                    Program
                                </p>
                                <p class="text-[11px] font-black text-slate-700 dark:text-slate-200 leading-none">
                                    {{ dashboardData?.student_info?.program || "N/A" }}
                                </p>
                            </div>
                        </div>

                        <div
                            class="flex items-center gap-2 bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 px-4 py-2 rounded-2xl">
                            <div
                                class="w-7 h-7 bg-purple-100 dark:bg-purple-500/20 rounded-xl flex items-center justify-center">
                                <i class="fa fa-book text-purple-500 text-[10px]"></i>
                            </div>
                            <div>
                                <p
                                    class="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none mb-0.5">
                                    Semester
                                </p>
                                <p class="text-[11px] font-black text-slate-700 dark:text-slate-200 leading-none">
                                    {{ dashboardData?.student_info?.semester || "N/A" }}
                                </p>
                            </div>
                        </div>

                        <div
                            class="flex items-center gap-2 bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 px-4 py-2 rounded-2xl">
                            <div
                                class="w-7 h-7 bg-green-100 dark:bg-green-500/20 rounded-xl flex items-center justify-center">
                                <i class="fa fa-id-badge text-green-500 text-[10px]"></i>
                            </div>
                            <div>
                                <p
                                    class="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none mb-0.5">
                                    Student ID
                                </p>
                                <p class="text-[11px] font-black text-slate-700 dark:text-slate-200 leading-none">
                                    {{ dashboardData?.student_info?.studentId || "N/A" }}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- IMAGE WITH GLOW -->
                <div class="relative flex-shrink-0">
                    <div
                        class="absolute inset-0 bg-gradient-to-t from-indigo-100/60 dark:from-indigo-500/10 to-transparent rounded-[2rem] blur-xl scale-90 translate-y-4">
                    </div>
                    <img :src="walkingStudent" alt="Student"
                        class="relative w-64 lg:w-[380px] object-contain drop-shadow-xl" />
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <!-- LEFT SIDE -->
            <div class="lg:col-span-8 space-y-8">
                <template v-if="loading">
                    <UiSkeleton height="h-32" class="rounded-[2.5rem]" />
                    <UiSkeleton height="h-64" class="rounded-[2.5rem]" />
                    <UiSkeleton height="h-48" class="rounded-[2.5rem]" />
                </template>
                <template v-else>
                    <CurrentProgram v-if="programData.name && programData.name !== 'N/A'" :program-data="programData" @click="showModal = true" />
                    <TodayClass v-if="todayClasses && todayClasses.length > 0" :todayClasses="todayClasses" />
                    <UpcomingExams v-if="upcomingExams && upcomingExams.length > 0" :upcomingExams="upcomingExams" />
                    <Assignment v-if="assignments && assignments.length > 0" :assignments="assignments" />
                    <PaymentHistory v-if="dashboardData?.fees && dashboardData.fees.length > 0" :fees="dashboardData?.fees.slice(0, 2)" />
                </template>
            </div>

            <!-- RIGHT SIDE -->
            <div class="lg:col-span-4 space-y-8">
                <template v-if="loading">
                    <UiSkeleton height="h-48" class="rounded-[2.5rem]" />
                    <UiSkeleton height="h-64" class="rounded-[2.5rem]" />
                </template>
                <template v-else>
                    <!-- ATTENDANCE -->
                    <Attendance v-if="attendanceData && attendanceData.total_days > 0" :attendance="attendanceData" />
                    <StopWatch />
                    <!-- <BookRecommendetion :recommendedBooks="recommendedBooks" /> -->
                    <CampusNotice v-if="notices && notices.length > 0" :notices="notices" />
                    <AcademicCalendar />
                    <!-- <Event /> -->
                </template>
            </div>
        </div>
    </main>

    <!-- CURRICULUM MODAL -->

    <div v-if="showModal"
        class="fixed inset-0 bg-black/40 dark:bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 transition-colors">
        <div
            class="bg-white dark:bg-slate-900 w-full max-w-3xl rounded-[2rem] shadow-2xl dark:shadow-none p-8 relative border border-transparent dark:border-slate-800">
            <!-- CLOSE -->

            <button @click="showModal = false"
                class="absolute top-5 right-5 text-slate-400 hover:text-black dark:hover:text-white transition-colors">
                <i class="fa fa-times"></i>
            </button>

            <!-- HEADER -->

            <h2 class="text-2xl font-black text-slate-800 dark:text-white mb-2">
                {{ programData.name }}
            </h2>

            <p class="text-xs text-slate-400 mb-6">
                Semester {{ programData.semester }}
            </p>

            <!-- PROGRAM DESCRIPTION -->

            <div class="mb-6">
                <h3 class="text-xs font-black uppercase text-slate-400 mb-2">
                    Program Overview
                </h3>

                <p class="text-sm text-slate-600">
                    {{ programData.description }}
                </p>
            </div>

            <!-- SUBJECTS -->

            <div>
                <h3 class="text-xs font-black uppercase text-slate-400 mb-4">
                    Curriculum Subjects
                </h3>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div v-for="subject in programData.subjects" :key="subject.name"
                        class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-700/50 flex justify-between">
                        <span class="font-bold text-slate-700 dark:text-slate-200 text-sm">
                            {{ subject.name }}
                        </span>

                        <span class="text-xs text-indigo-500 font-bold">
                            {{ subject.credits }} Credits
                        </span>
                    </div>
                </div>
            </div>

            <!-- FOOTER -->

            <div class="mt-8 flex justify-end">
                <button @click="showModal = false"
                    class="px-6 py-2 bg-indigo-600 text-white rounded-xl text-xs font-bold">
                    Close
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import walkingStudent from "~/assets/images/student-walking-nobg.gif";
import CurrentProgram from "~/components/dashbaord/currentProgram.vue";
import { useStudentDashboard } from "~/composable/userDashboard";
import Assignment from "~/components/dashbaord/assignment.vue";
import UpcomingExams from "~/components/dashbaord/upcomingExams.vue";
import TodayClass from "~/components/dashbaord/todayClass.vue";
import StopWatch from "~/components/dashbaord/stopWatch.vue";
import AcademicCalendar from "~/components/dashbaord/academicCalendar.vue";
import PaymentHistory from "~/components/dashbaord/paymentHistory.vue";
import Attendance from "~/components/dashbaord/attendance.vue";
import BookRecommendetion from "~/components/dashbaord/bookRecommendetion.vue";
import CampusNotice from "~/components/dashbaord/campusNotice.vue";
import Event from "~/components/dashbaord/event.vue";
import { useAssignments } from "~/composable/useAssignments";
import { useTimetable } from "~/composable/useTimetable";
import { useNotices } from "~/composable/useNotices";

const { dashboardData, loading, error, loadDashboard } = useStudentDashboard();
const { assignments: allAssignments, fetchAssignments } = useAssignments();
const assignments = computed(() => allAssignments.value.slice(0, 2));
const showModal = ref(false);

// class schedule data
const {
    activeDay,
    weekDays,
    currentDaySchedule: todayClasses,
    fetchSchedule,
} = useTimetable();
const today = new Date().toLocaleDateString("en-US", { weekday: "long" });
if (weekDays.includes(today)) activeDay.value = today;

// notice data
const { notices: allNotices, fetchNotices } = useNotices();
const notices = computed(() => allNotices.value.slice(0, 2));

/* PROGRAM DATA */
const programData = computed(() => {
    const studentInfo = dashboardData.value?.student_info;
    const courses = dashboardData.value?.courses || [];

    if (!studentInfo) return {};

    return {
        name: studentInfo.program || "N/A",
        semester: studentInfo.semester || "N/A",
        endDate: "June 24, 2026",
        daysRemaining: 112,
        description: `A comprehensive program for ${studentInfo.program || "your studies"}, focusing on your academic growth.`,
        subjects: courses.map((c) => ({
            name: c.name || c.code || "Unnamed Subject",
            code: c.code || c.id || "",
            credits: 1,
            teacher: c.teacher || "TBD",
            grade: c.grade || "N/A",
            next_class: c.next_class || null,
        })),
    };
});

/* UPCOMING EXAMS DATA */
const upcomingExams = computed(() => {
    const today = new Date();
    const upcommingExamination = dashboardData.value?.assessments || [];

    return upcommingExamination
        .map((a) => ({
            id: a.id,
            subject: a.title,
            date: a.date,
            description: a.description,
            day: a.day,
            month: a.month,
        }))
        .filter((a) => new Date(a.date) >= today)
        .sort((a, b) => new Date(a.date) - new Date(b.date));
});

/* BOOKS */
const recommendedBooks = ref([
    {
        title: "Atomic Habits",
        author: "James Clear",
        cover: "https://m.media-amazon.com/images/I/513Y5o-DYtL.jpg",
    },
    {
        title: "Deep Work",
        author: "Cal Newport",
        cover: "https://m.media-amazon.com/images/I/41f4oFz3u-L.jpg",
    },
]);

// attendance data
const attendanceData = computed(() => {
    const att = dashboardData.value?.attendance;
    if (!att)
        return {
            present_days: 0,
            absent_days: 0,
            leave_days: 0,
            total_days: 0,
        };

    return {
        present_days: att.present_days,
        absent_days: att.absent_days,
        leave_days: att.leave_days,
        total_days: att.total_days,
    };
});

onMounted(() => {
    loadDashboard();
    fetchAssignments();
    fetchSchedule();
    fetchNotices();
});
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 5px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
}

.transition-all {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
