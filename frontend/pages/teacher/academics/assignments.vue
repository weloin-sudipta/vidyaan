<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
    <div class="p-6 lg:p-10 max-w-7xl mx-auto space-y-8">

      <!-- Hero Header -->
      <HeroHeader title="Assignment Hub" subtitle="Create, Manage & Grade Student Assignments" icon="fa fa-layer-group">
        <div class="flex flex-wrap items-center gap-3">
          <div class="relative">
            <i class="fa fa-filter absolute left-4 top-1/2 -translate-y-1/2 text-indigo-500 text-xs"></i>
            <select v-model="selectedCourse" @change="loadTemplates"
              class="pl-10 pr-8 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold uppercase tracking-wider focus:ring-2 focus:ring-indigo-500 appearance-none outline-none cursor-pointer transition-all hover:border-indigo-300 dark:hover:border-indigo-500">
              <option value="">All My Courses</option>
              <option v-for="course in courses" :key="course.name" :value="course.name">{{ course.course_name }}
              </option>
            </select>
            <i
              class="fa fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-xs"></i>
          </div>

          <button @click="openCreateModal"
            class="group bg-gradient-to-r from-indigo-600 to-blue-600 dark:from-indigo-500 dark:to-blue-500 text-white px-6 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest hover:shadow-lg hover:shadow-indigo-300 dark:hover:shadow-indigo-900 transition-all duration-200 flex items-center gap-2 whitespace-nowrap">
            <i class="fa fa-plus group-hover:rotate-90 transition-transform"></i>
            <span class="hidden sm:inline">New Assignment</span>
            <span class="sm:hidden">New</span>
          </button>
        </div>
      </HeroHeader>

      <!-- Skeleton Loading -->
      <div v-if="loading" class="grid grid-cols-1 gap-8">
        <UiSkeleton v-for="i in 2" :key="i" height="h-80" class="rounded-[3.5rem]" />
      </div>

      <div v-else class="grid grid-cols-1 gap-10">
        <div v-for="template in templates" :key="template.name" :class="[
          'relative bg-white dark:bg-slate-900 rounded-[3.5rem] border border-slate-100 dark:border-slate-800 p-2 shadow-sm hover:shadow-xl transition-all duration-500',
          expandedCard === template.name ? 'shadow-2xl' : ''
        ]">

          <div class="p-8 lg:p-12">
            <div class="flex flex-col xl:flex-row justify-between gap-10">
              <div class="flex-1 space-y-6">
                <div class="flex flex-wrap items-center gap-4">
                  <span
                    class="px-4 py-1.5 bg-indigo-50 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full text-[10px] font-black uppercase tracking-tighter border border-indigo-100 dark:border-indigo-800/50">
                    {{ template.course_name || template.course }}
                  </span>
                  <span
                    :class="['px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-tighter border', template.status === 'Published' ? 'bg-green-50 text-green-600 border-green-100' : 'bg-amber-50 text-amber-600 border-amber-100']">
                    {{ template.status }}
                  </span>
                  <span
                    class="text-slate-400 text-[10px] font-bold uppercase tracking-widest flex items-center gap-1.5">
                    <i class="fa fa-calendar-check-o text-indigo-400"></i> Due: {{ formatDate(template.due_date) }}
                  </span>
                </div>

                <div>
                  <h2 class="text-3xl font-black text-slate-800 dark:text-white mb-4 tracking-tight leading-tight">{{
                    template.title }}</h2>

                  <!-- Description with See More functionality -->
                  <div class="text-slate-500 text-sm leading-relaxed max-w-3xl font-medium">
                    <div v-if="!isDescriptionExpanded(template.name)"
                      v-html="getShortDescription(template.description)"></div>
                    <div v-else v-html="template.description"></div>

                    <button v-if="isDescriptionLong(template.description)" @click="toggleDescription(template.name)"
                      class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 text-xs font-bold uppercase tracking-wider mt-2 inline-flex items-center gap-1 transition-colors">
                      {{ isDescriptionExpanded(template.name) ? 'See Less' : 'See More' }}
                      <i :class="isDescriptionExpanded(template.name) ? 'fa fa-chevron-up' : 'fa fa-chevron-down'"
                        class="text-[10px]"></i>
                    </button>
                  </div>
                </div>

                <div class="flex flex-wrap gap-4 pt-4">
                  <a v-if="template.assignment_file" :href="template.assignment_file" target="_blank"
                    class="flex items-center gap-3 px-5 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:bg-white dark:hover:bg-slate-700 hover:border-indigo-200 dark:hover:border-indigo-800 shadow-sm hover:shadow-md transition-all group/btn">
                    <div
                      class="w-8 h-8 bg-rose-50 dark:bg-rose-900/30 rounded-lg flex items-center justify-center text-rose-500 group-hover/btn:scale-110 transition-transform">
                      <i class="fa fa-file-pdf-o"></i>
                    </div>
                    <span
                      class="text-[10px] font-black uppercase text-slate-600 dark:text-slate-300 tracking-widest">Master
                      File</span>
                  </a>

                  <button v-if="template.status === 'Draft'" @click="handlePublish(template)"
                    class="flex items-center gap-3 px-6 py-3 bg-indigo-600 text-white rounded-2xl hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all font-black text-[10px] uppercase tracking-widest">
                    <i class="fa fa-paper-plane"></i> Publish to Students
                  </button>

                  <button @click="toggleSubmissions(template)"
                    class="flex items-center gap-3 px-6 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:border-indigo-500 transition-all font-black text-[10px] uppercase tracking-widest text-slate-600 dark:text-slate-300">
                    <i :class="['fa', expandedTemplate === template.name ? 'fa-chevron-up' : 'fa-list-ul']"></i>
                    {{ expandedTemplate === template.name ? 'Hide Submissions' : 'Review Submissions' }}
                  </button>
                </div>
              </div>

              <!-- Stats Card -->
              <div
                class="xl:w-80 bg-slate-50 dark:bg-slate-800/40 rounded-[2.5rem] p-10 flex flex-col justify-center items-center text-center border border-white dark:border-slate-700/50 shadow-inner">
                <div class="relative w-24 h-24 mb-6">
                  <svg class="w-full h-full transform -rotate-90">
                    <circle cx="48" cy="48" r="40" stroke="currentColor" stroke-width="8" fill="transparent"
                      class="text-slate-200 dark:text-slate-700" />
                    <circle cx="48" cy="48" r="40" stroke="currentColor" stroke-width="8" fill="transparent"
                      class="text-indigo-500 transition-all duration-1000" :stroke-dasharray="2 * Math.PI * 40"
                      :stroke-dashoffset="2 * Math.PI * 40 * (template.stats?.total ? (1 - (template.stats.submitted + template.stats.evaluated) / template.stats.total) : 1)" />
                  </svg>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <span class="text-3xl font-black text-indigo-600 dark:text-indigo-400">{{ template.stats?.submitted
                      + template.stats?.evaluated || 0 }}</span>
                  </div>
                </div>
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Total: {{
                  template.stats?.total || 0 }} Submissions</p>
                <div class="mt-4 flex gap-4">
                  <span class="text-[9px] font-bold text-green-500 uppercase tracking-tighter">{{
                    template.stats?.evaluated || 0 }} Graded</span>
                  <span class="text-[9px] font-bold text-amber-500 uppercase tracking-tighter">{{
                    template.stats?.submitted || 0 }} Pending</span>
                </div>
              </div>
            </div>

            <!-- Submissions Table -->
            <div v-if="expandedTemplate === template.name"
              class="mt-12 overflow-x-auto custom-scrollbar -mx-2 px-2 animate-in slide-in-from-top-4 duration-500">
              <div v-if="submissionsLoading" class="py-10 text-center">
                <i class="fa fa-spinner fa-spin text-indigo-500 text-2xl"></i>
              </div>
              <table v-else class="w-full border-separate border-spacing-y-4 min-w-[700px]">
                <thead>
                  <tr class="text-[10px] font-black uppercase tracking-widest text-slate-400">
                    <th class="text-left px-8 py-2">Student</th>
                    <th class="text-left px-8 py-2">Submission</th>
                    <th class="text-left px-8 py-2">Status</th>
                    <th class="text-right px-8 py-2">Grade Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="sub in submissions" :key="sub.name"
                    class="bg-slate-50/50 dark:bg-slate-800/30 group/row hover:bg-white dark:hover:bg-slate-800 border border-transparent hover:border-indigo-100 dark:hover:border-indigo-900/50 transition-all rounded-[2rem] shadow-sm hover:shadow-lg">
                    <td class="px-8 py-5 rounded-l-[2rem]">
                      <div class="flex items-center gap-4">
                        <div
                          class="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center font-black text-xs text-indigo-700 shadow-inner overflow-hidden">
                          {{ sub.student_name.charAt(0) }}
                        </div>
                        <span class="text-xs font-black text-slate-700 dark:text-slate-200">{{ sub.student_name
                          }}</span>
                      </div>
                    </td>
                    <td class="px-8 py-5">
                      <a v-if="sub.submission_file" :href="sub.submission_file" target="_blank"
                        class="flex items-center gap-2 text-indigo-500 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors group/link">
                        <i class="fa fa-file-text-o group-hover/link:translate-y-[-1px]"></i>
                        <span class="text-[10px] font-bold tracking-wide">View Work</span>
                      </a>
                      <span v-else class="text-[10px] text-slate-400 uppercase font-black">No File</span>
                    </td>
                    <td class="px-8 py-5">
                      <span v-if="sub.status === 'Evaluated'"
                        class="inline-flex items-center px-4 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-xl text-[10px] font-black uppercase gap-2">
                        <i class="fa fa-check-circle"></i> Scored: {{ sub.evaluated_score }}
                      </span>
                      <span v-else-if="sub.status === 'Submitted'"
                        class="inline-flex items-center px-4 py-1.5 bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-xl text-[10px] font-black uppercase gap-2">
                        <i class="fa fa-clock-o"></i> Needs Review
                      </span>
                      <span v-else
                        class="inline-flex items-center px-4 py-1.5 bg-slate-100 dark:bg-slate-800 text-slate-400 rounded-xl text-[10px] font-black uppercase gap-2">
                        {{ sub.status }}
                      </span>
                    </td>
                    <td class="px-8 py-5 rounded-r-[2rem] text-right">
                      <button @click="openGradingModal(sub)" :disabled="sub.status === 'Active'"
                        class="bg-slate-900 dark:bg-indigo-600 text-white px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-md disabled:opacity-30 disabled:hover:scale-100 h-10">
                        {{ sub.status === 'Evaluated' ? 'Update Grade' : 'Grade Work' }}
                      </button>
                    </td>
                  </tr>
                  <tr v-if="submissions.length === 0">
                    <td colspan="4"
                      class="text-center py-10 text-xs font-bold text-slate-400 uppercase tracking-widest">
                      No students have been assigned yet (Publish first)
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal 1: Create Assignment Template -->
      <AppModal v-model="showCreateModal" title="Create Assignment" maxWidth="max-w-2xl">
        <form @submit.prevent="handleCreate" class="space-y-6">

          <!-- Section 1: Basic Information -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-pencil mr-2 text-indigo-500"></i>Assignment Details
            </h4>

            <!-- Assignment Title -->
            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Title <span class="text-red-500">*</span>
              </label>
              <input v-model="newTemplate.title" type="text" required
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
                placeholder="e.g. Mid-term Research Project" />
            </div>

            <!-- Course && Due Date Row -->
            <div class="grid grid-cols-2 gap-4">
              <!-- Course -->
              <div>
                <label
                  class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                  Course <span class="text-red-500">*</span>
                </label>
                <select v-model="newTemplate.course" @change="loadGroups" required
                  class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all">
                  <option value="" disabled>Select Course</option>
                  <option v-for="c in courses" :key="c.name" :value="c.name">{{ c.course_name }}</option>
                </select>
              </div>

              <!-- Due Date -->
              <div>
                <label
                  class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                  Due Date <span class="text-red-500">*</span>
                </label>
                <input v-model="newTemplate.due_date" type="date" required
                  class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all" />
              </div>
            </div>
          </div>

          <!-- Section 2: Content -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-file-text mr-2 text-blue-500"></i>Instructions & Resources
            </h4>

            <!-- Instructions / Description -->
            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Instructions <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
              </label>
              <textarea v-model="newTemplate.description" rows="4"
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all resize-none"
                placeholder="Enter detailed assignment instructions and requirements..."></textarea>
            </div>

            <!-- Reference Document -->
            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Reference Document <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
              </label>
              <input v-model="newTemplate.assignment_file" type="text"
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
                placeholder="/files/assignment.pdf" />
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Link to reference materials or assignment file
              </p>
            </div>
          </div>

          <!-- Section 3: Assignment Distribution -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-share-alt mr-2 text-green-500"></i>Distribution
            </h4>

            <!-- Assign To -->
            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Assign To <span class="text-red-500">*</span>
              </label>
              <select v-model="newTemplate.assign_to"
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all">
                <option value="All Enrolled">All Enrolled Students</option>
                <option value="Student Group">Selected Student Group</option>
              </select>
            </div>

            <!-- Student Group (Conditional) -->
            <div v-if="newTemplate.assign_to === 'Student Group'">
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Student Group <span class="text-red-500">*</span>
              </label>
              <select v-model="newTemplate.student_group"
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all">
                <option value="" disabled>Select Group</option>
                <option v-for="g in studentGroups" :key="g.name" :value="g.name">{{ g.student_group_name }}</option>
              </select>
            </div>
          </div>
        </form>

        <!-- Footer Actions -->
        <template #footer>
          <button @click="showCreateModal = false" type="button"
            class="flex-1 px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            Cancel
          </button>
          <button @click="handleCreate" :disabled="creating" type="button"
            class="flex-1 px-6 py-3 rounded-xl bg-indigo-600 dark:bg-indigo-500 text-white text-sm font-bold hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
            <i v-if="creating" class="fa fa-spinner fa-spin"></i>
            {{ creating ? 'Creating...' : 'Create Template' }}
          </button>
        </template>
      </AppModal>

      <!-- Modal 2: Grading Modal -->
      <AppModal v-model="showGradeModal" title="Grade Student Work" maxWidth="max-w-lg">
        <div class="space-y-6" v-if="gradingSubmission">

          <!-- Student Info Card -->
          <div
            class="flex items-center gap-4 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 p-5 rounded-2xl border border-indigo-200 dark:border-indigo-900/30">
            <div
              class="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-600 to-blue-600 flex items-center justify-center text-white font-black text-xl shadow-lg">
              {{ gradingSubmission.student_name.charAt(0) }}
            </div>
            <div>
              <h4 class="font-black text-slate-900 dark:text-white text-base">{{ gradingSubmission.student_name }}</h4>
              <p class="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                <i class="fa fa-file-o mr-1 text-indigo-500"></i>
                <span class="font-bold">Submission ID:</span> {{ gradingSubmission.name }}
              </p>
            </div>
          </div>

          <!-- Scoring Section -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-star mr-2 text-yellow-500"></i>Score Evaluation
            </h4>

            <!-- Score Input with Visual Feedback -->
            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400">Score
                  (0-100)</label>
                <div class="text-right">
                  <span class="text-3xl font-black text-indigo-600 dark:text-indigo-400">{{ gradeInput || '0' }}</span>
                  <span class="text-xs text-slate-500 dark:text-slate-400 ml-2">/ 100</span>
                </div>
              </div>

              <input v-model="gradeInput" type="number" min="0" max="100"
                class="w-full bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-xl px-6 py-4 text-2xl font-black text-indigo-600 dark:text-indigo-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all text-center shadow-sm hover:border-indigo-300 dark:hover:border-indigo-600" />

              <!-- Score Guide -->
              <div class="mt-4 grid grid-cols-4 gap-2 text-[10px] font-bold text-center">
                <div class="p-2 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400">0-40<br>Poor
                </div>
                <div class="p-2 rounded-lg bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400">
                  41-70<br>Average</div>
                <div class="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400">
                  71-85<br>Good
                </div>
                <div class="p-2 rounded-lg bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400">
                  86-100<br>Excellent</div>
              </div>
            </div>
          </div>

          <!-- Feedback Section -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-comments mr-2 text-green-500"></i>Feedback & Remarks
            </h4>

            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Teacher Remarks <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
              </label>
              <textarea v-model="remarksInput" rows="4"
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all resize-none placeholder-slate-400 dark:placeholder-slate-500"
                placeholder="Provide constructive feedback for the student..."></textarea>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-2">Be specific and helpful to improve future
                submissions
              </p>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <template #footer>
          <button @click="showGradeModal = false"
            class="flex-1 px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            Cancel
          </button>
          <button @click="handleGrade" :disabled="grading"
            class="flex-1 px-6 py-3 rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 dark:from-green-500 dark:to-emerald-500 text-white text-sm font-bold hover:shadow-lg hover:shadow-green-300 dark:hover:shadow-green-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
            <i v-if="grading" class="fa fa-spinner fa-spin"></i>
            <i v-else class="fa fa-check-circle"></i>
            {{ grading ? 'Submitting...' : 'Submit Grade' }}
          </button>
        </template>
      </AppModal>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTeacherAssignments } from '~/composable/useTeacherAssignments'
import AppModal from '~/components/ui/AppModal.vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import UiSkeleton from '~/components/ui/UiSkeleton.vue'

const {
  courses, templates, submissions, studentGroups, loading,
  fetchCourses, fetchStudentGroups, fetchTemplates,
  createTemplate, publishTemplate, fetchSubmissions, gradeAssignment
} = useTeacherAssignments()

const selectedCourse = ref('')
const expandedTemplate = ref(null)
const submissionsLoading = ref(false)
const expandedCard = ref(null)
const expandedDescription = ref({})

// Modals
const showCreateModal = ref(false)
const showGradeModal = ref(false)
const creating = ref(false)
const grading = ref(false)

const newTemplate = ref({
  title: '', course: '', due_date: '', assign_to: 'All Enrolled',
  student_group: '', description: '', assignment_file: ''
})

const gradingSubmission = ref(null)
const gradeInput = ref(0)
const remarksInput = ref('')

onMounted(async () => {
  await fetchCourses()
  await loadTemplates()
})

const loadTemplates = async () => {
  await fetchTemplates(selectedCourse.value)
}

const loadGroups = async () => {
  if (newTemplate.value.course) {
    await fetchStudentGroups(newTemplate.value.course)
  }
}

const openCreateModal = () => {
  newTemplate.value = {
    title: '', course: '', due_date: '', assign_to: 'All Enrolled',
    student_group: '', description: '', assignment_file: ''
  }
  showCreateModal.value = true
}

const handleCreate = async () => {
  if (!newTemplate.value.title || !newTemplate.value.course || !newTemplate.value.due_date) {
    return alert('Please fill in title, course and due date')
  }
  creating.value = true
  const res = await createTemplate(newTemplate.value)
  creating.value = false
  if (res?.error) {
    alert(res.error)
  } else {
    showCreateModal.value = false
    await loadTemplates()
  }
}

const handlePublish = async (template) => {
  if (!confirm(`Publish "${template.title}" to students? This will create assignment records immediately.`)) return

  const res = await publishTemplate(template.name)
  if (res?.error) {
    alert(res.error)
  } else {
    alert(res.message || 'Published successfully')
    await loadTemplates()
  }
}

const toggleSubmissions = async (template) => {
  if (expandedTemplate.value === template.name) {
    expandedTemplate.value = null
  } else {
    expandedTemplate.value = template.name
    submissionsLoading.value = true
    await fetchSubmissions(template.name)
    submissionsLoading.value = false
  }
}

const openGradingModal = (sub) => {
  gradingSubmission.value = sub
  gradeInput.value = sub.evaluated_score || 0
  remarksInput.value = sub.remarks || ''
  showGradeModal.value = true
}

const handleGrade = async () => {
  grading.value = true
  const res = await gradeAssignment(gradingSubmission.value.name, gradeInput.value, remarksInput.value)
  grading.value = false

  if (res?.error) {
    alert(res.error)
  } else {
    showGradeModal.value = false
    await fetchSubmissions(expandedTemplate.value)
    await loadTemplates() // Update stats
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// Helper functions for description management
const stripHtmlTags = (html) => {
  if (!html) return ''
  const temp = document.createElement('div')
  temp.innerHTML = html
  return temp.textContent || temp.innerText || ''
}

const isDescriptionLong = (description) => {
  if (!description) return false
  const plainText = stripHtmlTags(description)
  return plainText.length > 150
}

const getShortDescription = (description) => {
  if (!description) return ''
  const plainText = stripHtmlTags(description)
  if (plainText.length <= 150) return description
  const truncated = plainText.substring(0, 150) + '...'
  return truncated
}

const isDescriptionExpanded = (templateName) => {
  return expandedDescription.value[templateName] || false
}

const toggleDescription = (templateName) => {
  expandedDescription.value = {
    ...expandedDescription.value,
    [templateName]: !expandedDescription.value[templateName]
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 99px;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155;
}
</style>