<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
    <div class="p-6 lg:p-10 max-w-7xl mx-auto space-y-8">

      <!-- Hero Header -->
      <HeroHeader title="Assignment Hub" subtitle="Create, Manage & Grade Student Assignments" icon="fa fa-layer-group">
        <div class="flex flex-wrap items-center gap-3">
          <div class="relative">
            <i class="fa fa-filter absolute left-4 top-1/2 -translate-y-1/2 text-indigo-500 text-xs"></i>
            <select v-model="selectedCourse" @change="loadAssignments"
              class="pl-10 pr-8 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold uppercase tracking-wider focus:ring-2 focus:ring-indigo-500 appearance-none outline-none cursor-pointer transition-all hover:border-indigo-300 dark:hover:border-indigo-500">
              <option value="">All My Courses</option>
              <option v-for="course in courses" :key="course.name" :value="course.name">{{ course.course_name }}</option>
            </select>
            <i class="fa fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-xs"></i>
          </div>

          <button @click="openCreateModal"
            :disabled="courses.length === 0"
            class="group bg-gradient-to-r from-indigo-600 to-blue-600 dark:from-indigo-500 dark:to-blue-500 text-white px-6 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest hover:shadow-lg hover:shadow-indigo-300 dark:hover:shadow-indigo-900 transition-all duration-200 flex items-center gap-2 whitespace-nowrap disabled:opacity-40 disabled:cursor-not-allowed">
            <i class="fa fa-plus group-hover:rotate-90 transition-transform"></i>
            <span class="hidden sm:inline">New Assignment</span>
            <span class="sm:hidden">New</span>
          </button>
        </div>
      </HeroHeader>

      <!-- No courses warning -->
      <div v-if="!loading && courses.length === 0"
        class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40 rounded-2xl p-6 text-center">
        <i class="fa fa-exclamation-triangle text-amber-500 text-2xl mb-3"></i>
        <p class="text-sm font-bold text-amber-700 dark:text-amber-400">No courses found. Set up your courses before creating assignments.</p>
      </div>

      <!-- Skeleton Loading -->
      <div v-if="loading" class="grid grid-cols-1 gap-8">
        <UiSkeleton v-for="i in 2" :key="i" height="h-80" class="rounded-[3.5rem]" />
      </div>

      <!-- Error banner -->
      <div v-else-if="error"
        class="bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800/40 rounded-2xl p-5 text-sm font-bold text-rose-600 dark:text-rose-400 flex items-center gap-3">
        <i class="fa fa-exclamation-circle"></i>
        {{ error }}
      </div>

      <div v-else class="grid grid-cols-1 gap-10">

        <!-- Empty state -->
        <div v-if="assignments.length === 0 && courses.length > 0"
          class="flex flex-col items-center justify-center py-24 bg-white dark:bg-slate-900 rounded-3xl border-2 border-dashed border-slate-200 dark:border-slate-800">
          <i class="fa fa-folder-open-o text-4xl text-slate-200 dark:text-slate-800 mb-4"></i>
          <p class="text-slate-500 dark:text-slate-400 font-bold tracking-tight">No assignments yet. Create your first one.</p>
        </div>

        <div v-for="assignment in assignments" :key="assignment.name" :class="[
          'relative bg-white dark:bg-slate-900 rounded-[3.5rem] border border-slate-100 dark:border-slate-800 p-2 shadow-sm hover:shadow-xl transition-all duration-500',
          expandedCard === assignment.name ? 'shadow-2xl' : ''
        ]">

          <div class="p-8 lg:p-12">
            <div class="flex flex-col xl:flex-row justify-between gap-10">
              <div class="flex-1 space-y-6">

                <!-- Tags row -->
                <div class="flex flex-wrap items-center gap-4">
                  <span
                    class="px-4 py-1.5 bg-indigo-50 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full text-[10px] font-black uppercase tracking-tighter border border-indigo-100 dark:border-indigo-800/50">
                    {{ assignment.course_name || assignment.course }}
                  </span>

                  <!-- Status badge -->
                  <span :class="statusBadgeClass(assignment.status)"
                    class="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-tighter border">
                    {{ assignment.status }}
                  </span>

                  <span class="text-slate-400 text-[10px] font-bold uppercase tracking-widest flex items-center gap-1.5">
                    <i class="fa fa-calendar-check-o text-indigo-400"></i> Due: {{ formatDate(assignment.due_date) }}
                  </span>
                </div>

                <div>
                  <h2 class="text-3xl font-black text-slate-800 dark:text-white mb-4 tracking-tight leading-tight">
                    {{ assignment.title }}
                  </h2>

                  <div class="text-slate-500 text-sm leading-relaxed max-w-3xl font-medium">
                    <div v-if="!isDescriptionExpanded(assignment.name)"
                      v-html="getShortDescription(assignment.description)"></div>
                    <div v-else v-html="assignment.description"></div>

                    <button v-if="isDescriptionLong(assignment.description)" @click="toggleDescription(assignment.name)"
                      class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 text-xs font-bold uppercase tracking-wider mt-2 inline-flex items-center gap-1 transition-colors">
                      {{ isDescriptionExpanded(assignment.name) ? 'See Less' : 'See More' }}
                      <i :class="isDescriptionExpanded(assignment.name) ? 'fa fa-chevron-up' : 'fa fa-chevron-down'"
                        class="text-[10px]"></i>
                    </button>
                  </div>
                </div>

                <!-- Action buttons -->
                <div class="flex flex-wrap gap-4 pt-4">
                  <a v-if="assignment.assignment_file" :href="getFileUrl(assignment.assignment_file)" target="_blank"
                    class="flex items-center gap-3 px-5 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:bg-white dark:hover:bg-slate-700 hover:border-indigo-200 dark:hover:border-indigo-800 shadow-sm hover:shadow-md transition-all group/btn">
                    <div
                      class="w-8 h-8 bg-rose-50 dark:bg-rose-900/30 rounded-lg flex items-center justify-center text-rose-500 group-hover/btn:scale-110 transition-transform">
                      <i class="fa fa-file-pdf-o"></i>
                    </div>
                    <span class="text-[10px] font-black uppercase text-slate-600 dark:text-slate-300 tracking-widest">Master File</span>
                  </a>

                  <!-- Publish — Draft only -->
                  <button v-if="assignment.status === 'Draft'"
                    @click="handlePublish(assignment)"
                    :disabled="publishingName === assignment.name"
                    class="flex items-center gap-3 px-6 py-3 bg-indigo-600 text-white rounded-2xl hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all font-black text-[10px] uppercase tracking-widest disabled:opacity-50">
                    <i :class="publishingName === assignment.name ? 'fa fa-spinner fa-spin' : 'fa fa-paper-plane'"></i>
                    {{ publishingName === assignment.name ? 'Publishing...' : 'Publish to Students' }}
                  </button>

                  <!-- View Submissions — Published or Closed -->
                  <button v-if="['Published', 'Closed'].includes(assignment.status)"
                    @click="handleViewSubmissions(assignment)"
                    class="flex items-center gap-3 px-6 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:border-indigo-500 transition-all font-black text-[10px] uppercase tracking-widest text-slate-600 dark:text-slate-300">
                    <i class="fa fa-list-ul"></i>
                    View Submissions
                  </button>

                  <!-- Close — Published only -->
                  <button v-if="assignment.status === 'Published'"
                    @click="handleClose(assignment)"
                    class="flex items-center gap-3 px-5 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:border-rose-400 dark:hover:border-rose-600 transition-all font-black text-[10px] uppercase tracking-widest text-slate-500 dark:text-slate-400">
                    <i class="fa fa-lock"></i>
                    Close
                  </button>

                  <!-- Edit — Draft only -->
                  <button v-if="assignment.status === 'Draft'"
                    @click="openEditModal(assignment)"
                    class="flex items-center gap-3 px-5 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:border-indigo-400 dark:hover:border-indigo-600 transition-all font-black text-[10px] uppercase tracking-widest text-slate-500 dark:text-slate-400">
                    <i class="fa fa-pencil"></i>
                    Edit
                  </button>

                  <!-- Delete — Draft only -->
                  <button v-if="assignment.status === 'Draft'"
                    @click="handleDelete(assignment)"
                    class="flex items-center gap-3 px-5 py-3 bg-slate-50 dark:bg-slate-800 border border-rose-100 dark:border-rose-900/30 rounded-2xl hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-all font-black text-[10px] uppercase tracking-widest text-rose-400">
                    <i class="fa fa-trash-o"></i>
                    Delete
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
                      class="text-indigo-500 transition-all duration-1000"
                      :stroke-dasharray="2 * Math.PI * 40"
                      :stroke-dashoffset="progressOffset(assignment)" />
                  </svg>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <span class="text-3xl font-black text-indigo-600 dark:text-indigo-400">
                      {{ assignment.submission_count || 0 }}
                    </span>
                  </div>
                </div>
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
                  Total: {{ assignment.submission_count || 0 }} Submissions
                </p>
                <div class="mt-4 flex gap-4">
                  <span class="text-[9px] font-bold text-green-500 uppercase tracking-tighter">
                    {{ assignment.graded_count || 0 }} Graded
                  </span>
                  <span class="text-[9px] font-bold text-amber-500 uppercase tracking-tighter">
                    {{ assignment.pending_count || 0 }} Pending
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Create / Edit Modal ─── -->
      <AppModal v-model="showCreateModal"
        :title="editingAssignment ? 'Edit Assignment' : 'Create Assignment'"
        maxWidth="max-w-2xl">
        <form @submit.prevent="handleSave" class="space-y-6">

          <!-- Basic Information -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-pencil mr-2 text-indigo-500"></i>Assignment Details
            </h4>

            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Title <span class="text-red-500">*</span>
              </label>
              <input v-model="form.title" type="text" required
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all dark:text-white"
                placeholder="e.g. Mid-term Research Project" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                  Course <span class="text-red-500">*</span>
                </label>
                <select v-model="form.course" @change="loadGroups" required
                  class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all dark:text-white">
                  <option value="" disabled>Select Course</option>
                  <option v-for="c in courses" :key="c.name" :value="c.name">{{ c.course_name }}</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                  Due Date <span class="text-red-500">*</span>
                </label>
                <input v-model="form.due_date" type="date" required
                  class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all dark:text-white" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                  Topic <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
                </label>
                <input v-model="form.topic" type="text"
                  class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all dark:text-white"
                  placeholder="e.g. Chapter 3 — Arrays" />
              </div>

              <div>
                <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                  Max Score <span class="text-red-500">*</span>
                </label>
                <input v-model.number="form.max_score" type="number" min="1" required
                  class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all dark:text-white"
                  placeholder="100" />
              </div>
            </div>
          </div>

          <!-- Content -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-file-text mr-2 text-blue-500"></i>Instructions & Resources
            </h4>

            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Instructions <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
              </label>
              <textarea v-model="form.description" rows="4"
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all resize-none dark:text-white"
                placeholder="Enter detailed assignment instructions and requirements..."></textarea>
            </div>

            <!-- File upload -->
            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Reference Document <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
              </label>
              <div v-if="!form.assignment_file" class="relative group">
                <input type="file" @change="onAssignmentFileChange"
                  class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" />
                <div
                  class="border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl p-6 text-center group-hover:border-indigo-400 dark:group-hover:border-indigo-600 transition-all">
                  <i class="fa fa-cloud-upload text-2xl text-slate-300 dark:text-slate-600 mb-2 group-hover:text-indigo-500"></i>
                  <p class="text-xs font-bold text-slate-500 dark:text-slate-400">
                    {{ assignmentFileUploading ? 'Uploading...' : (selectedAssignmentFile ? selectedAssignmentFile.name : 'Choose a file') }}
                  </p>
                  <p class="text-[10px] text-slate-400 mt-1">PDF, DOCX, ZIP (Max 20MB)</p>
                </div>
              </div>
              <div v-else
                class="flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl">
                <div class="flex items-center gap-3">
                  <i class="fa fa-file-pdf-o text-rose-500"></i>
                  <span class="text-xs font-bold text-slate-600 dark:text-slate-300 truncate max-w-[200px]">{{ form.assignment_file }}</span>
                </div>
                <button @click="form.assignment_file = ''" type="button"
                  class="text-slate-400 hover:text-rose-500 transition-colors text-sm">
                  <i class="fa fa-times"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Distribution -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-share-alt mr-2 text-green-500"></i>Distribution
            </h4>

            <div>
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Assign To <span class="text-red-500">*</span>
              </label>
              <select v-model="form.assign_to"
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all dark:text-white">
                <option value="All Enrolled">All Enrolled Students</option>
                <option value="Specific Groups">Specific Groups</option>
              </select>
              <p v-if="form.course && form.assign_to === 'All Enrolled' && studentGroups.length === 0"
                class="mt-2 text-[11px] font-bold text-rose-500">
                No student groups found for this course. Either map yourself to a Student Group as instructor, or switch to "Specific Groups".
              </p>
              <p v-else-if="form.course && form.assign_to === 'All Enrolled' && studentGroups.length > 0"
                class="mt-2 text-[11px] font-bold text-slate-400">
                Will create the assignment for {{ studentGroups.length }} student group{{ studentGroups.length === 1 ? '' : 's' }}.
              </p>
            </div>

            <!-- Multi-select student groups -->
            <div v-if="form.assign_to === 'Specific Groups'">
              <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Student Groups <span class="text-red-500">*</span>
              </label>
              <div v-if="studentGroups.length === 0"
                class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-400 font-bold">
                Select a course first to load student groups.
              </div>
              <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-1">
                <label v-for="g in studentGroups" :key="g.name"
                  class="flex items-center gap-3 px-4 py-3 rounded-xl border cursor-pointer transition-all"
                  :class="form.student_groups.includes(g.name)
                    ? 'bg-indigo-50 dark:bg-indigo-900/30 border-indigo-200 dark:border-indigo-800/50'
                    : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-700'">
                  <input type="checkbox" :value="g.name" v-model="form.student_groups"
                    class="rounded accent-indigo-600" />
                  <span class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ g.student_group_name }}</span>
                </label>
              </div>
              <p v-if="form.student_groups.length === 0"
                class="text-[10px] text-rose-500 font-bold mt-2">Select at least one group.</p>
            </div>
          </div>
        </form>

        <template #footer>
          <button @click="showCreateModal = false" type="button"
            class="flex-1 px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            Cancel
          </button>
          <button @click="handleSave"
            :disabled="saving || assignmentFileUploading
              || (form.assign_to === 'Specific Groups' && form.student_groups.length === 0)
              || (form.assign_to === 'All Enrolled' && form.course && studentGroups.length === 0)"
            type="button"
            class="flex-1 px-6 py-3 rounded-xl bg-indigo-600 dark:bg-indigo-500 text-white text-sm font-bold hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
            <i v-if="saving" class="fa fa-spinner fa-spin"></i>
            {{ saving ? (editingAssignment ? 'Saving...' : 'Creating...') : (editingAssignment ? 'Save Changes' : 'Create Assignment') }}
          </button>
        </template>
      </AppModal>

      <!-- ─── Submissions Modal ─── -->
      <AppModal v-model="showSubmissionsModal" title="Submissions" maxWidth="max-w-4xl">
        <div v-if="currentAssignment">
          <!-- Assignment summary -->
          <div class="mb-6 flex flex-wrap gap-3 items-center">
            <span class="text-base font-black text-slate-800 dark:text-white">{{ currentAssignment.title }}</span>
            <span :class="statusBadgeClass(currentAssignment.status)"
              class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter border">
              {{ currentAssignment.status }}
            </span>
            <span class="text-xs text-slate-400 font-bold">Max: {{ currentAssignment.max_score }} pts</span>
          </div>

          <div v-if="detailLoading" class="py-12 flex justify-center">
            <i class="fa fa-spinner fa-spin text-indigo-500 text-2xl"></i>
          </div>

          <div v-else-if="currentAssignment.submissions && currentAssignment.submissions.length === 0"
            class="py-12 text-center text-xs font-bold text-slate-400 uppercase tracking-widest">
            No submissions yet.
          </div>

          <div v-else class="overflow-x-auto -mx-2 px-2">
            <table class="w-full border-separate border-spacing-y-3 min-w-[640px]">
              <thead>
                <tr class="text-[10px] font-black uppercase tracking-widest text-slate-400">
                  <th class="text-left px-6 py-2">Student</th>
                  <th class="text-left px-6 py-2">Submitted</th>
                  <th class="text-left px-6 py-2">File</th>
                  <th class="text-left px-6 py-2">Status</th>
                  <th class="text-right px-6 py-2">Grade</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sub in currentAssignment.submissions" :key="sub.student"
                  class="bg-slate-50/50 dark:bg-slate-800/30 hover:bg-white dark:hover:bg-slate-800 border border-transparent hover:border-indigo-100 dark:hover:border-indigo-900/50 transition-all rounded-2xl shadow-sm">
                  <td class="px-6 py-4 rounded-l-2xl">
                    <div class="flex items-center gap-3">
                      <div
                        class="w-9 h-9 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center font-black text-xs text-indigo-700 dark:text-indigo-400">
                        {{ (sub.student_name || sub.student).charAt(0) }}
                      </div>
                      <span class="text-xs font-black text-slate-700 dark:text-slate-200">{{ sub.student_name || sub.student }}</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 text-[10px] text-slate-400 font-bold">
                    {{ sub.submitted_on ? formatDate(sub.submitted_on) : '—' }}
                  </td>
                  <td class="px-6 py-4">
                    <a v-if="sub.submission_file" :href="getFileUrl(sub.submission_file)" target="_blank"
                      class="flex items-center gap-1.5 text-indigo-500 dark:text-indigo-400 hover:text-indigo-700 text-[10px] font-bold">
                      <i class="fa fa-file-text-o"></i> View Work
                    </a>
                    <span v-else class="text-[10px] text-slate-400 font-black uppercase">No File</span>
                  </td>
                  <td class="px-6 py-4">
                    <span v-if="sub.status === 'Graded'"
                      class="inline-flex items-center px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-xl text-[10px] font-black uppercase gap-1.5">
                      <i class="fa fa-check-circle"></i> {{ sub.score }} pts
                    </span>
                    <span v-else-if="sub.status === 'Submitted'"
                      class="inline-flex items-center px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 rounded-xl text-[10px] font-black uppercase gap-1.5">
                      <i class="fa fa-clock-o"></i> Needs Review
                    </span>
                    <span v-else
                      class="inline-flex items-center px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-400 rounded-xl text-[10px] font-black uppercase">
                      {{ sub.status || 'Pending' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 rounded-r-2xl text-right">
                    <button v-if="sub.submitted_on" @click="openGradingModal(sub)"
                      class="bg-slate-900 dark:bg-indigo-600 text-white px-5 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-md">
                      {{ sub.status === 'Graded' ? 'Update Grade' : 'Grade Work' }}
                    </button>
                    <span v-else class="text-[10px] text-slate-300 dark:text-slate-600 font-bold uppercase">Not submitted</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <template #footer>
          <button @click="showSubmissionsModal = false"
            class="w-full px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            Close
          </button>
        </template>
      </AppModal>

      <!-- ─── Grading Modal ─── -->
      <AppModal v-model="showGradeModal" title="Grade Student Work" maxWidth="max-w-lg">
        <div class="space-y-6" v-if="gradingSubmission">

          <!-- Student Info -->
          <div
            class="flex items-center gap-4 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 p-5 rounded-2xl border border-indigo-200 dark:border-indigo-900/30">
            <div
              class="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-600 to-blue-600 flex items-center justify-center text-white font-black text-xl shadow-lg">
              {{ (gradingSubmission.student_name || gradingSubmission.student).charAt(0) }}
            </div>
            <div>
              <h4 class="font-black text-slate-900 dark:text-white text-base">{{ gradingSubmission.student_name || gradingSubmission.student }}</h4>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
                Max score: <span class="font-black text-indigo-500">{{ currentAssignment?.max_score || 100 }} pts</span>
              </p>
            </div>
          </div>

          <!-- Score -->
          <div class="space-y-4">
            <h4
              class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
              <i class="fa fa-star mr-2 text-yellow-500"></i>Score Evaluation
            </h4>

            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400">
                  Score (0–{{ currentAssignment?.max_score || 100 }})
                </label>
                <div class="text-right">
                  <span class="text-3xl font-black text-indigo-600 dark:text-indigo-400">{{ gradeInput }}</span>
                  <span class="text-xs text-slate-500 dark:text-slate-400 ml-2">/ {{ currentAssignment?.max_score || 100 }}</span>
                </div>
              </div>

              <input v-model.number="gradeInput" type="number" min="0" :max="currentAssignment?.max_score || 100"
                @input="clampScore"
                class="w-full bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-xl px-6 py-4 text-2xl font-black text-indigo-600 dark:text-indigo-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all text-center shadow-sm hover:border-indigo-300 dark:hover:border-indigo-600" />

              <p v-if="gradeInput < 0 || gradeInput > (currentAssignment?.max_score || 100)"
                class="text-xs text-rose-500 font-bold mt-2">
                Score must be between 0 and {{ currentAssignment?.max_score || 100 }}.
              </p>
            </div>
          </div>

          <!-- Remarks -->
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
                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all resize-none dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
                placeholder="Provide constructive feedback for the student..."></textarea>
            </div>
          </div>
        </div>

        <template #footer>
          <button @click="showGradeModal = false"
            class="flex-1 px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            Cancel
          </button>
          <button @click="handleGrade"
            :disabled="grading || gradeInput < 0 || gradeInput > (currentAssignment?.max_score || 100)"
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
import { useTeacherAssignments } from '~/composables/teacher/useTeacherAssignments'
import { useToast } from '~/composables/ui/useToast'
import { useConfirm } from '~/composables/ui/useConfirm'
import AppModal from '~/components/ui/AppModal.vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import UiSkeleton from '~/components/ui/UiSkeleton.vue'
import { call } from '~/composables/api/useFrappeFetch'

const config = useRuntimeConfig()

const { addToast } = useToast()
const { confirm, setLoading: setConfirmLoading } = useConfirm()

const {
  courses,
  studentGroups,
  assignments,
  currentAssignment,
  loading,
  error,
  fetchCourses,
  fetchStudentGroups,
  fetchAssignments,
  fetchAssignmentDetail,
  createAssignment,
  updateAssignment,
  publishAssignment,
  deleteAssignment,
  closeAssignment,
  gradeSubmission,
} = useTeacherAssignments()

const selectedCourse = ref('')
const expandedCard = ref(null)
const expandedDescription = ref({})

// Modal state
const showCreateModal = ref(false)
const showSubmissionsModal = ref(false)
const showGradeModal = ref(false)

// Operation loading flags
const saving = ref(false)
const grading = ref(false)
const detailLoading = ref(false)
const publishingName = ref(null)
const assignmentFileUploading = ref(false)
const selectedAssignmentFile = ref(null)

// Edit tracking
const editingAssignment = ref(null)

// Form
const form = ref({
  title: '',
  course: '',
  topic: '',
  due_date: '',
  max_score: 100,
  assign_to: 'All Enrolled',
  student_groups: [],
  description: '',
  assignment_file: '',
})

// Grading
const gradingSubmission = ref(null)
const gradeInput = ref(0)
const remarksInput = ref('')

onMounted(async () => {
  await fetchCourses()
  await loadAssignments()
})

const loadAssignments = async () => {
  await fetchAssignments(selectedCourse.value || null)
}

const loadGroups = async () => {
  if (form.value.course) {
    await fetchStudentGroups(form.value.course)
    form.value.student_groups = []
  }
}

// ─── Create / Edit ────────────────────────────────────────────────────────

const resetForm = () => {
  form.value = {
    title: '',
    course: '',
    topic: '',
    due_date: '',
    max_score: 100,
    assign_to: 'All Enrolled',
    student_groups: [],
    description: '',
    assignment_file: '',
  }
  editingAssignment.value = null
  selectedAssignmentFile.value = null
}

const openCreateModal = async () => {
  resetForm()
  showCreateModal.value = true
  // Reset cached student groups so a stale list doesn't bleed into the new modal
  studentGroups.value = []
}

const openEditModal = async (assignment) => {
  resetForm()
  editingAssignment.value = assignment.name

  // Pre-fill from the list item (full detail has target_groups)
  form.value.title = assignment.title
  form.value.course = assignment.course
  form.value.topic = assignment.topic || ''
  form.value.due_date = assignment.due_date
  form.value.max_score = assignment.max_score
  form.value.assign_to = assignment.assign_to || 'All Enrolled'
  form.value.description = assignment.description || ''
  form.value.assignment_file = assignment.assignment_file || ''
  form.value.student_groups = (assignment.target_groups || []).map(g => g.student_group)

  if (form.value.course) {
    await fetchStudentGroups(form.value.course)
  }

  showCreateModal.value = true
}

const onAssignmentFileChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  selectedAssignmentFile.value = file
  assignmentFileUploading.value = true

  const formData = new FormData()
  formData.append('file', file)
  formData.append('is_private', 0)

  try {
    const res = await $fetch('/api/method/upload_file', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })
    form.value.assignment_file = res.message?.file_url || ''
  } catch (err) {
    addToast('File upload failed: ' + (err.message || 'Unknown error'), 'error')
  } finally {
    assignmentFileUploading.value = false
  }
}

const handleSave = async () => {
  if (!form.value.title || !form.value.course || !form.value.due_date || !form.value.max_score) {
    addToast('Please fill in title, course, due date and max score.', 'warning')
    return
  }

  // Past-date guard: backend (Assignment._validate_due_date) rejects past
  // dates only when CREATING. For edits we leave the due date alone.
  if (!editingAssignment.value) {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const picked = new Date(form.value.due_date)
    picked.setHours(0, 0, 0, 0)
    if (picked < today) {
      addToast('Due date cannot be in the past. Pick today or a future date.', 'warning')
      return
    }
  }

  if (form.value.assign_to === 'Specific Groups' && form.value.student_groups.length === 0) {
    addToast('Select at least one student group.', 'warning')
    return
  }

  const payload = {
    title: form.value.title,
    course: form.value.course,
    topic: form.value.topic,
    due_date: form.value.due_date,
    max_score: form.value.max_score,
    assign_to: form.value.assign_to,
    student_groups: form.value.assign_to === 'All Enrolled' ? [] : form.value.student_groups,
    description: form.value.description,
    assignment_file: form.value.assignment_file,
  }

  saving.value = true
  let res

  if (editingAssignment.value) {
    res = await updateAssignment(editingAssignment.value, payload)
  } else {
    res = await createAssignment(payload)
  }

  saving.value = false

  if (res?.error) {
    addToast(res.error, 'error')
  } else {
    addToast(
      editingAssignment.value ? 'Assignment updated.' : 'Assignment created.',
      'success'
    )
    showCreateModal.value = false
    await loadAssignments()
  }
}

// ─── Publish ──────────────────────────────────────────────────────────────

const handlePublish = async (assignment) => {
  const ok = await confirm({
    title: 'Publish Assignment',
    message: `Publish "${assignment.title}" to students now? Submission rows will be generated for every active member of the target groups.`,
    hint: 'This action makes the assignment visible to students immediately.',
    variant: 'publish',
    confirmText: 'Publish Now',
    cancelText: 'Not Yet',
    loadingText: 'Publishing…',
    confirmIcon: 'fa-paper-plane',
  })
  if (!ok) return
  setConfirmLoading(true)
  publishingName.value = assignment.name
  const res = await publishAssignment(assignment.name)
  publishingName.value = null
  setConfirmLoading(false)
  if (res?.error) {
    addToast(res.error, 'error')
  } else {
    addToast(`Published "${assignment.title}".`, 'success')
    await loadAssignments()
  }
}

// ─── Close ────────────────────────────────────────────────────────────────

const handleClose = async (assignment) => {
  const ok = await confirm({
    title: 'Close Assignment',
    message: `Close "${assignment.title}"? Students will no longer be able to submit, but existing submissions and grades will be preserved.`,
    hint: 'You can still view and grade pending submissions.',
    variant: 'warning',
    confirmText: 'Close Assignment',
    cancelText: 'Keep Open',
    loadingText: 'Closing…',
    confirmIcon: 'fa-lock',
  })
  if (!ok) return
  setConfirmLoading(true)
  const res = await closeAssignment(assignment.name)
  setConfirmLoading(false)
  if (res?.error) {
    addToast(res.error, 'error')
  } else {
    addToast(`Closed "${assignment.title}".`, 'success')
    await loadAssignments()
  }
}

// ─── Delete ───────────────────────────────────────────────────────────────

const handleDelete = async (assignment) => {
  const ok = await confirm({
    title: 'Delete Assignment',
    message: `Delete "${assignment.title}" permanently? This cannot be undone.`,
    hint: 'Graded submissions will block deletion. Close the assignment instead.',
    variant: 'danger',
    confirmText: 'Delete Forever',
    cancelText: 'Keep It',
    loadingText: 'Deleting…',
    confirmIcon: 'fa-trash',
  })
  if (!ok) return
  setConfirmLoading(true)
  const res = await deleteAssignment(assignment.name)
  setConfirmLoading(false)
  if (res?.error) {
    addToast(res.error, 'error')
  } else {
    addToast(`Deleted "${assignment.title}".`, 'success')
    await loadAssignments()
  }
}

// ─── Submissions ──────────────────────────────────────────────────────────

const handleViewSubmissions = async (assignment) => {
  showSubmissionsModal.value = true
  detailLoading.value = true
  await fetchAssignmentDetail(assignment.name)
  detailLoading.value = false
}

// ─── Grading ──────────────────────────────────────────────────────────────

const openGradingModal = (sub) => {
  gradingSubmission.value = sub
  gradeInput.value = sub.score ?? 0
  remarksInput.value = sub.remarks || ''
  showGradeModal.value = true
}

const clampScore = () => {
  const max = currentAssignment.value?.max_score || 100
  if (gradeInput.value < 0) gradeInput.value = 0
  if (gradeInput.value > max) gradeInput.value = max
}

const handleGrade = async () => {
  const max = currentAssignment.value?.max_score || 100
  if (gradeInput.value < 0 || gradeInput.value > max) return

  grading.value = true
  const res = await gradeSubmission(
    currentAssignment.value.name,
    gradingSubmission.value.student,
    gradeInput.value,
    remarksInput.value
  )
  grading.value = false

  if (res?.error) {
    addToast(res.error, 'error')
  } else {
    addToast('Grade saved.', 'success')
    showGradeModal.value = false
    // Refresh detail in the background
    await fetchAssignmentDetail(currentAssignment.value.name)
    await loadAssignments()
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────

const progressOffset = (assignment) => {
  const total = assignment.submission_count || 0
  const done = (assignment.graded_count || 0) + (assignment.pending_count || 0)
  if (total === 0) return 2 * Math.PI * 40
  return 2 * Math.PI * 40 * (1 - done / total)
}

const statusBadgeClass = (status) => {
  switch (status) {
    case 'Published': return 'bg-green-50 text-green-600 border-green-100 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800/40'
    case 'Draft':     return 'bg-amber-50 text-amber-600 border-amber-100 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800/40'
    case 'Closed':    return 'bg-slate-100 text-slate-500 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
    default:          return 'bg-slate-100 text-slate-500 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const stripHtmlTags = (html) => {
  if (!html) return ''
  const temp = document.createElement('div')
  temp.innerHTML = html
  return temp.textContent || temp.innerText || ''
}

const isDescriptionLong = (description) => {
  if (!description) return false
  return stripHtmlTags(description).length > 150
}

const getShortDescription = (desc) => {
  if (!desc) return ''
  const striped = desc.replace(/<[^>]*>?/gm, '')
  if (striped.length <= 180) return desc
  return striped.substring(0, 180) + '...'
}

const getFileUrl = (filePath, isDownload = false) => {
  if (!filePath) return ''
  if (filePath.startsWith('http')) return filePath

  if (isDownload) {
    return `${config.public.apiBaseUrl}/api/method/frappe.utils.file_manager.download_file?file_url=${encodeURIComponent(filePath)}`
  }

  return `${config.public.apiBaseUrl}${filePath}`
}

const isDescriptionExpanded = (name) => expandedDescription.value[name] || false

const toggleDescription = (name) => {
  expandedDescription.value = { ...expandedDescription.value, [name]: !expandedDescription.value[name] }
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
