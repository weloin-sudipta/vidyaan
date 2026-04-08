<script setup>
import { ref, computed, onMounted } from 'vue'
import feesTab from './tabs/feesTab.vue'
import examTab from './tabs/examTab.vue'
import attendanceTab from './tabs/attendanceTab.vue'
import { useProfile, updateProfile } from '~/composables/useProfile'
import { useAttendanceSummary } from '~/composables/useAttendance'
const config = useRuntimeConfig()
useSeoMeta({
    title: config.public.appName + " | Academics - Profile"
})
const photoPreview = ref(null)
const loading = ref(true)

const { summary: attSummary, fetchSummary: fetchAttSummary } = useAttendanceSummary()

const attendanceRate = computed(() => attSummary.value?.rate ?? '--')
const attendanceBehavior = computed(() => {
    const rate = attSummary.value?.rate
    if (!rate) return '--'
    if (rate >= 90) return 'Excellent'
    if (rate >= 75) return 'Good'
    if (rate >= 60) return 'Average'
    return 'Needs Improvement'
})

const studentInitials = computed(() => {
    const name = student.value?.name || ''
    return name
        .split(' ')
        .filter(Boolean)
        .map(word => word[0].toUpperCase())
        .slice(0, 2)
        .join('')
})

const showEditModal = ref(false)
const editSaving = ref(false)
const editUploadingPhoto = ref(false)
const editPhotoPreview = ref(null)

const editForm = ref({
    firstName: '',
    middleName: '',
    lastName: '',
    phone: '',
    mobile: '',
    language: 'en',
    timezone: 'Asia/Kolkata',
    profilePicture: null,
    uploadedPhotoUrl: null
})
// Reactive tab state
const activeTab = ref('profile')
const tabs = [
    { id: 'profile', name: 'Profile' },
    { id: 'fees', name: 'Fees' },
    { id: 'exam', name: 'Exam' },
    { id: 'attendance', name: 'Attendance' },
]
const tabComponents = {
    fees: feesTab,
    exam: examTab,
    attendance: attendanceTab,
}

// Reactive student data (to replace static object)
const student = ref({
    name: '',
    admNo: '',
    rollNo: '',
    class: '',
    localId: '',
    academic: {},
    secondary: {},
    logistics: {},
})

// Download student resume as PDF
const downloadResumePDF = async () => {
    // Dynamically load jsPDF from CDN
    if (!window.jspdf) {
        await new Promise((resolve, reject) => {
            const script = document.createElement('script')
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
            script.onload = resolve
            script.onerror = reject
            document.head.appendChild(script)
        })
    }

    const { jsPDF } = window.jspdf
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })

    const pageW = 210
    const pageH = 297
    const margin = 20
    const contentW = pageW - margin * 2

    // ── Indigo sidebar ──────────────────────────────────────────────
    doc.setFillColor(79, 70, 229)
    doc.rect(0, 0, 60, pageH, 'F')

    // ── Avatar circle on sidebar ────────────────────────────────────
    doc.setFillColor(255, 255, 255, 0.15)
    doc.circle(30, 48, 22, 'F')

    // Initials inside circle
    const initials = studentInitials.value || '??'
    doc.setTextColor(79, 70, 229)
    doc.setFontSize(18)
    doc.setFont('helvetica', 'bold')
    doc.text(initials, 30, 53, { align: 'center' })

    // Try to draw actual photo if available
    if (photoPreview.value) {
        try {
            const img = new Image()
            img.crossOrigin = 'anonymous'
            await new Promise((res) => {
                img.onload = res
                img.onerror = res
                img.src = photoPreview.value
            })
            if (img.naturalWidth > 0) {
                const canvas = document.createElement('canvas')
                canvas.width = 200
                canvas.height = 200
                const ctx = canvas.getContext('2d')
                ctx.beginPath()
                ctx.arc(100, 100, 100, 0, Math.PI * 2)
                ctx.clip()
                ctx.drawImage(img, 0, 0, 200, 200)
                const dataUrl = canvas.toDataURL('image/jpeg')
                doc.addImage(dataUrl, 'JPEG', 8, 26, 44, 44)
            }
        } catch (_) { /* fallback to initials */ }
    }

    // ── Student name on sidebar ─────────────────────────────────────
    doc.setTextColor(255, 255, 255)
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    const fullName = student.value.name || 'Student Name'
    doc.text(fullName, 30, 82, { align: 'center', maxWidth: 52 })

    doc.setFontSize(7)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(199, 195, 255)
    doc.text(student.value.class || '—', 30, 92, { align: 'center' })

    // ── Sidebar section: IDs ────────────────────────────────────────
    const sidebarSection = (label, value, y) => {
        doc.setFontSize(6)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(199, 195, 255)
        doc.text(label.toUpperCase(), 10, y)
        doc.setFontSize(8)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(255, 255, 255)
        doc.text(String(value || '—'), 10, y + 5, { maxWidth: 42 })
    }

    sidebarSection('Student ID', `#${student.value.admNo}`, 106)
    sidebarSection('Roll No', student.value.rollNo, 120)
    sidebarSection('Session', student.value.academic?.Session, 134)
    sidebarSection('Blood Group', student.value.academic?.['Blood Group'], 148)
    sidebarSection('Gender', student.value.academic?.Gender, 162)
    sidebarSection('Date of Birth', student.value.academic?.['Date of Birth'], 176)
    sidebarSection('Nationality', student.value.secondary?.['Contact & Security']?.Nationality, 190)
    sidebarSection('Religion', student.value.academic?.Religion, 204)

    // Contact on sidebar
    doc.setFontSize(6)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(199, 195, 255)
    doc.text('CONTACT', 10, 222)
    doc.setDrawColor(255, 255, 255, 0.2)
    doc.setLineWidth(0.3)
    doc.line(10, 224, 52, 224)

    sidebarSection('Mobile', student.value.secondary?.['Contact & Security']?.Mobile, 228)
    sidebarSection('Email', student.value.secondary?.['Contact & Security']?.Email, 242)

    // ── Right content area ──────────────────────────────────────────
    const rx = 70  // right content start x
    const rw = pageW - rx - 10

    // Top accent bar
    doc.setFillColor(79, 70, 229)
    doc.rect(rx, 0, rw, 8, 'F')

    // Header area
    doc.setFillColor(248, 250, 252)
    doc.rect(rx, 8, rw, 40, 'F')

    doc.setTextColor(30, 41, 59)
    doc.setFontSize(20)
    doc.setFont('helvetica', 'bold')
    doc.text('Student Profile', rx, 26)

    doc.setFontSize(8)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(100, 116, 139)
    doc.text('Academic Year ' + (student.value.academic?.Session || '—'), rx, 35)

    doc.setDrawColor(226, 232, 240)
    doc.setLineWidth(0.5)
    doc.line(rx, 48, pageW - 10, 48)

    // Section renderer
    const drawSection = (title, fields, startY) => {
        // Section title
        doc.setFillColor(238, 242, 255)
        doc.roundedRect(rx, startY, rw, 8, 1, 1, 'F')
        doc.setTextColor(79, 70, 229)
        doc.setFontSize(7)
        doc.setFont('helvetica', 'bold')
        doc.text(title.toUpperCase(), rx + 4, startY + 5.5)

        let y = startY + 14
        const colW = rw / 2
        let col = 0

        for (const [label, value] of Object.entries(fields)) {
            const x = rx + col * colW
            doc.setFontSize(6)
            doc.setFont('helvetica', 'normal')
            doc.setTextColor(148, 163, 184)
            doc.text(label.toUpperCase(), x, y)

            doc.setFontSize(8)
            doc.setFont('helvetica', 'bold')
            doc.setTextColor(30, 41, 59)
            doc.text(String(value || '—'), x, y + 5, { maxWidth: colW - 4 })

            col++
            if (col >= 2) {
                col = 0
                y += 14
            }
        }

        // Return next Y position
        return y + (col > 0 ? 14 : 4)
    }

    let currentY = 54

    currentY = drawSection('Academic Information', {
        'Admission Date': student.value.academic?.['Admission Date'],
        'Category': student.value.academic?.Category,
        'Caste': student.value.academic?.Caste,
        'Class': student.value.class,
    }, currentY)

    currentY += 4
    currentY = drawSection('Parental Records', {
        'Father': student.value.secondary?.['Parental Records']?.Father,
        'Mother': student.value.secondary?.['Parental Records']?.Mother,
        'Guardian': student.value.secondary?.['Parental Records']?.Guardian,
        'Guardian Relation': student.value.secondary?.['Parental Records']?.['Guardian Relation'],
    }, currentY)

    currentY += 4
    currentY = drawSection('Address & Logistics', {
        'Country': student.value.logistics?.Country,
        'State': student.value.logistics?.State,
        'Pincode': student.value.logistics?.Pincode,
        'Hostel': student.value.logistics?.['Hostel Facility'],
        'Current Address': student.value.logistics?.['Current Address'],
        'Permanent Address': student.value.logistics?.['Permanent Address'],
    }, currentY)

    // ── Footer ──────────────────────────────────────────────────────
    doc.setFillColor(248, 250, 252)
    doc.rect(rx, pageH - 14, rw, 14, 'F')
    doc.setFontSize(6)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(148, 163, 184)
    doc.text(`Generated on ${new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })}`, rx, pageH - 6)
    doc.text('Confidential — For Internal Use Only', pageW - 10, pageH - 6, { align: 'right' })

    // ── Save ────────────────────────────────────────────────────────
    const fileName = `${(student.value.name || 'student').replace(/\s+/g, '_')}_profile.pdf`
    doc.save(fileName)
}

// Fetch profile from backend
onMounted(async () => {
    fetchAttSummary()
    const profile = await useProfile()

    if (profile && !profile.error) {
        photoPreview.value = profile.photo_url || null

        // Map API response to the same structure your template expects
        student.value = {
            name: profile.student_name || `${profile.first_name || ''} ${profile.last_name || ''}`,
            admNo: profile.admNo || profile.student_id || '—',
            rollNo: profile.rollNo || profile.student_id?.split('-').pop() || '—',
            class: profile.program_name || '—',
            localId: profile.localId || '—',

            academic: {
                "Admission Date": profile.program_enrollment_date || '—',
                "Session": profile.program_session || '—',
                "Gender": profile.gender || '—',
                "Category": profile.category || '—',
                "Caste": profile.caste || '—',
                "Religion": profile.religion || '—',
                "Blood Group": profile.blood_group || '—',
                "Date of Birth": profile.date_of_birth || '—'
            },

            secondary: {
                "Parental Records": {
                    "Father": profile.guardians?.[0]?.guardian_name || '—',
                    "Mother": profile.mother_name || '—',
                    "Guardian": profile.guardians?.[0]?.guardian_name || '—',
                    "Guardian Relation": profile.guardians?.[0]?.relation || '—'
                },
                "Contact & Security": {
                    "Mobile": profile.mobile_number || '—',
                    "Email": profile.email || '—',
                    "Nationality": profile.nationality || '—',
                    "Parent Mobile": profile.parent_mobile_number || '—'
                }
            },

            logistics: {
                "Country": profile.country || '—',
                "State": profile.state || '—',
                "Pincode": profile.pincode || '—',
                "Hostel Facility": profile.hostel_facility || '—',
                "Current Address": profile.address_line_1 || '—',
                "Permanent Address": profile.address_line_2 || '—'
            }
        }
    }
    loading.value = false
})

// Handle photo upload in edit modal
const handleEditPhotoUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    if (file.size > 2 * 1024 * 1024) {
        alert("Image must be under 2MB")
        return
    }

    editPhotoPreview.value = URL.createObjectURL(file)
    editUploadingPhoto.value = true

    try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('is_private', '0')
        formData.append('doctype', 'User')
        formData.append('fieldname', 'user_image')

        const response = await $fetch('/api/method/upload_file', {
            method: 'POST',
            body: formData,
            credentials: 'include',
        })

        const fileUrl = response?.message?.file_url
        if (fileUrl) {
            editForm.value.uploadedPhotoUrl = fileUrl
            editPhotoPreview.value = fileUrl
        }
    } catch (err) {
        console.error("Photo upload failed:", err)
        alert("Failed to upload photo.")
    } finally {
        editUploadingPhoto.value = false
    }
}

// Save edit modal changes
const saveEditModal = async () => {
    editSaving.value = true
    try {
        const payload = {
            firstName: editForm.value.firstName,
            middleName: editForm.value.middleName,
            lastName: editForm.value.lastName,
            phone: editForm.value.phone,
            mobile: editForm.value.mobile,
            language: editForm.value.language,
            timezone: editForm.value.timezone,
        }
        if (editForm.value.uploadedPhotoUrl) {
            payload.user_image = editForm.value.uploadedPhotoUrl
        }

        const res = await updateProfile(payload)
        if (res?.error) {
            alert("Failed: " + res.error)
        } else {
            if (editForm.value.uploadedPhotoUrl) {
                photoPreview.value = editForm.value.uploadedPhotoUrl
            }
            student.value.name = `${editForm.value.firstName} ${editForm.value.middleName ? editForm.value.middleName + ' ' : ''}${editForm.value.lastName}`.trim()
            showEditModal.value = false
            alert("Profile Updated Successfully!")
        }
    } catch (err) {
        console.error("Error saving:", err)
        alert("An unexpected error occurred.")
    } finally {
        editSaving.value = false
    }
}
</script>

<template>
    <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans text-slate-900">
        <div class="max-w-[1440px] mx-auto">

            <!-- SKELETON LOADING -->
            <div v-if="loading" class="animate-in">
                <header class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 p-6 mb-6 transition-colors">
                    <div class="flex flex-col md:flex-row items-center gap-8">
                        <UiSkeleton height="h-32" width="w-32" class="rounded-[2rem] shrink-0" />
                        <div class="flex-1 space-y-4 w-full">
                            <UiSkeleton height="h-8" width="w-64" />
                            <div class="flex gap-6 mt-4">
                                <UiSkeleton height="h-10" width="w-24" />
                                <UiSkeleton height="h-10" width="w-24" />
                                <UiSkeleton height="h-10" width="w-32" />
                            </div>
                        </div>
                    </div>
                </header>
                <div class="flex flex-col lg:flex-row gap-6">
                    <div class="w-full lg:w-64 shrink-0 space-y-2">
                        <UiSkeleton height="h-12" v-for="i in 4" :key="i" class="rounded-2xl" />
                    </div>
                    <div class="flex-1">
                        <UiSkeleton height="h-[500px]" class="rounded-[2.5rem]" />
                    </div>
                </div>
            </div>

            <!-- CONTENT -->
            <div v-else class="animate-in">
                <header class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 p-6 mb-6 transition-colors">
                    <div class="flex flex-col md:flex-row items-center gap-8">
                        <div class="relative group cursor-pointer" @click="showEditModal = true">
                            <div class="w-32 h-32 rounded-[2rem] overflow-hidden ring-4 ring-slate-50 dark:ring-slate-800 shadow-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center transition-colors">
                                <img
                                    v-if="photoPreview"
                                    :src="photoPreview"
                                    alt="Student Photo"
                                    class="w-full h-full object-cover"
                                    @error="photoPreview = null"
                                />
                                <span v-else class="text-3xl font-black text-indigo-600 dark:text-indigo-400 select-none tracking-tight transition-colors">
                                    {{ studentInitials }}
                                </span>
                            </div>

                            <div class="absolute inset-0 rounded-[2rem] bg-slate-900/50 dark:bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <div class="bg-white dark:bg-slate-800 rounded-xl w-10 h-10 flex items-center justify-center shadow-lg transition-colors">
                                    <i class="fa fa-pencil text-indigo-600 dark:text-indigo-400 text-sm"></i>
                                </div>
                            </div>

                            <div class="absolute -bottom-2 -right-2 bg-indigo-600 w-8 h-8 rounded-xl flex items-center justify-center text-white border-4 border-white dark:border-slate-900 shadow-md transition-colors">
                                <i class="fa fa-graduation-cap text-[10px]"></i>
                            </div>
                        </div>

                        <div class="flex-1 text-center md:text-left">
                            <div class="flex flex-col md:flex-row md:items-center gap-3 mb-2">
                                <h1 class="text-3xl font-black tracking-tight text-slate-800 dark:text-white transition-colors">
                                    {{ student.name }} {{ student.lastName }}
                                </h1>
                                <span class="px-3 py-1 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 text-[10px] font-black uppercase tracking-widest rounded-lg border border-green-100 dark:border-green-800/50 transition-colors">
                                    Active Session: {{ student.academic.Session }}
                                </span>
                            </div>

                            <div class="flex flex-wrap justify-center md:justify-start gap-6 mt-4">
                                <div class="flex flex-col">
                                    <span class="label-tiny">Student ID</span>
                                    <span class="value-bold text-indigo-600 dark:text-indigo-400 transition-colors">#{{ student.admNo }}</span>
                                </div>
                                <div class="w-px h-8 bg-slate-100 dark:bg-slate-800 hidden md:block transition-colors"></div>
                                <div class="flex flex-col">
                                    <span class="label-tiny">Roll Number</span>
                                    <span class="value-bold">{{ student.rollNo }}</span>
                                </div>
                                <div class="w-px h-8 bg-slate-100 dark:bg-slate-800 hidden md:block transition-colors"></div>
                                <div class="flex flex-col">
                                    <span class="label-tiny">Class & Section</span>
                                    <span class="value-bold">{{ student.class }}</span>
                                </div>
                            </div>
                        </div>

                        <div class="flex gap-2">
                            <button class="btn-icon" title="Print Profile" @click="downloadResumePDF">
                                <i class="fa fa-print"></i>
                            </button>
                            <!-- <button class="btn-primary" @click="showEditModal = true">Edit Information</button> -->
                        </div>
                    </div>

                    <nav class="flex items-center gap-2 mt-8 border-t border-slate-50 dark:border-slate-800/50 pt-6 overflow-x-auto no-scrollbar transition-colors">
                        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" :class="[
                            activeTab === tab.id
                                ? 'bg-slate-900 dark:bg-slate-700 text-white shadow-xl shadow-slate-200 dark:shadow-none'
                                : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200',
                            'px-6 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all whitespace-nowrap'
                        ]">
                            {{ tab.name }}
                        </button>
                    </nav>
                </header>

                <!-- PROFILE TAB -->
                <main v-if="activeTab === 'profile'" class="space-y-6 animate-in fade-in duration-500">

                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none transition-colors">
                            <div class="flex items-center gap-3 mb-8">
                                <div class="w-1.5 h-6 bg-indigo-600 dark:bg-indigo-400 rounded-full transition-colors"></div>
                                <h3 class="text-lg font-black text-slate-800 dark:text-white tracking-tight transition-colors">Academic Profile</h3>
                            </div>
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-y-10 gap-x-6">
                                <div v-for="(val, label) in student.academic" :key="label">
                                    <p class="label-tiny mb-1">{{ label }}</p>
                                    <p class="text-sm font-bold text-slate-700 dark:text-slate-200 transition-colors">{{ val }}</p>
                                </div>
                            </div>
                        </div>

                        <div class="bg-indigo-600 dark:bg-indigo-700/80 rounded-[2.5rem] p-8 text-white shadow-xl shadow-indigo-100 dark:shadow-none flex flex-col justify-between transition-colors">
                            <div>
                                <p class="text-[10px] font-black uppercase tracking-[0.2em] opacity-60 mb-1">Attendance Performance</p>
                                <h4 class="text-4xl font-black">{{ attendanceRate }}<span class="text-lg opacity-50">%</span></h4>
                            </div>
                            <div class="space-y-4">
                                <div class="flex justify-between items-center text-sm font-bold">
                                    <span class="opacity-70 text-xs">Behavior Score</span>
                                    <span>{{ attendanceBehavior }}</span>
                                </div>
                                <div class="w-full bg-indigo-500 rounded-full h-1.5">
                                    <div class="bg-white h-1.5 rounded-full" :style="{ width: (attSummary?.rate || 0) + '%' }"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div v-for="(section, title) in student.secondary" :key="title"
                            class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none transition-colors">
                            <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-8 border-b border-slate-50 dark:border-slate-800/50 pb-4 transition-colors">
                                {{ title }}
                            </h3>
                            <div class="grid grid-cols-2 gap-y-8 gap-x-6">
                                <div v-for="(val, label) in section" :key="label">
                                    <p class="label-tiny mb-1">{{ label }}</p>
                                    <p class="text-sm font-bold text-slate-700 dark:text-slate-200 transition-colors">{{ val || '—' }}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none transition-colors">
                        <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-8 transition-colors">
                            Logistics & Residential Details
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div v-for="(val, label) in student.logistics" :key="label"
                                class="p-6 bg-slate-50/50 dark:bg-slate-800/30 rounded-2xl border border-slate-100 dark:border-slate-800/50 transition-colors">
                                <p class="label-tiny mb-2">{{ label }}</p>
                                <p class="text-xs font-bold text-slate-600 dark:text-slate-300 leading-relaxed transition-colors">{{ val }}</p>
                            </div>
                        </div>
                    </div>
                </main>

                <!-- DYNAMIC TAB -->
                <component v-else-if="tabComponents[activeTab]" :is="tabComponents[activeTab]"
                    class="animate-in fade-in duration-500" />

                <!-- FALLBACK -->
                <div v-else class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-24 border border-dashed border-slate-200 dark:border-slate-800 text-center transition-colors">
                    <div class="w-20 h-20 bg-slate-50 dark:bg-slate-800/50 rounded-3xl flex items-center justify-center mx-auto mb-6 transition-colors">
                        <i class="fa fa-folder-open text-slate-200 dark:text-slate-600 text-3xl transition-colors"></i>
                    </div>
                    <h2 class="text-xl font-black text-slate-800 dark:text-white uppercase tracking-tighter transition-colors">
                        Section Under Development
                    </h2>
                    <p class="text-sm text-slate-400 dark:text-slate-500 mt-2 transition-colors">
                        The {{ activeTab }} module is being synced with the database.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <!-- EDIT MODAL -->
    <div v-if="showEditModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/60 dark:bg-black/70 backdrop-blur-sm transition-colors" @click="showEditModal = false"></div>

        <div class="relative bg-white dark:bg-slate-900 w-full max-w-2xl rounded-[2.5rem] shadow-2xl flex flex-col max-h-[90vh] overflow-hidden animate-modal transition-colors">

            <div class="p-8 border-b border-slate-100 dark:border-slate-800/50 flex justify-between items-center transition-colors">
                <h3 class="text-xl font-black text-slate-800 dark:text-white transition-colors">Edit Basic Information</h3>
                <button @click="showEditModal = false"
                    class="w-10 h-10 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 rounded-xl flex items-center justify-center transition-colors">
                    <i class="fa fa-times text-slate-500 dark:text-slate-400 transition-colors"></i>
                </button>
            </div>

            <div class="p-8 overflow-y-auto space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

                    <div>
                        <label class="label-tiny mb-2 block">First Name</label>
                        <input v-model="editForm.firstName" class="input-field" />
                    </div>

                    <div>
                        <label class="label-tiny mb-2 block">Middle Name (Optional)</label>
                        <input v-model="editForm.middleName" class="input-field" />
                    </div>

                    <div>
                        <label class="label-tiny mb-2 block">Last Name</label>
                        <input v-model="editForm.lastName" class="input-field" />
                    </div>

                    <div>
                        <label class="label-tiny mb-2 block">Phone</label>
                        <input v-model="editForm.phone" class="input-field" />
                    </div>

                    <div>
                        <label class="label-tiny mb-2 block">Mobile Number</label>
                        <input v-model="editForm.mobile" class="input-field" />
                    </div>

                    <div>
                        <label class="label-tiny mb-2 block">Language</label>
                        <input v-model="editForm.language" class="input-field" />
                    </div>

                    <div>
                        <label class="label-tiny mb-2 block">Time Zone</label>
                        <input v-model="editForm.timezone" class="input-field" />
                    </div>

                    <div class="md:col-span-2">
                        <label class="label-tiny mb-2 block">Profile Picture</label>
                        <div class="flex items-center gap-4">
                            <div v-if="editPhotoPreview" class="w-16 h-16 rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-800 transition-colors">
                                <img :src="editPhotoPreview" class="w-full h-full object-cover" />
                            </div>
                            <input type="file" accept="image/*" @change="handleEditPhotoUpload"
                                class="text-slate-700 dark:text-slate-300 text-sm transition-colors file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-black file:uppercase file:tracking-widest file:bg-indigo-50 file:text-indigo-600 dark:file:bg-indigo-900/30 dark:file:text-indigo-400 hover:file:bg-indigo-100 transition-colors" />
                            <span v-if="editUploadingPhoto" class="text-xs text-indigo-600 dark:text-indigo-400 font-bold transition-colors">Uploading...</span>
                        </div>
                    </div>

                </div>
            </div>

            <div class="p-6 border-t border-slate-100 dark:border-slate-800/50 flex justify-end gap-3 transition-colors">
                <button @click="showEditModal = false"
                    class="px-6 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl text-xs font-black uppercase tracking-widest transition-colors">
                    Cancel
                </button>
                <button @click="saveEditModal" :disabled="editSaving" class="btn-primary">
                    {{ editSaving ? 'Saving...' : 'Save Changes' }}
                </button>
            </div>

        </div>
    </div>
</template>

<style scoped>
.label-tiny {
  @apply text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 transition-colors;
}

.value-bold {
  @apply text-sm font-black text-slate-800 dark:text-slate-100 transition-colors;
}

.input-field {
  @apply w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors placeholder:text-slate-300 dark:placeholder:text-slate-600;
}

.btn-primary {
  @apply px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-all active:scale-95 shadow-lg shadow-indigo-100 dark:shadow-none;
}

.btn-icon {
  @apply w-10 h-10 flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-xl transition-colors;
}

.no-scrollbar::-webkit-scrollbar { display: none; }

@keyframes modalIn {
  from { opacity: 0; transform: translateY(20px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.animate-modal {
  animation: modalIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>

<!-- <style scoped>
/* Utility Components */
.label-tiny {
    @apply text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors;
}

.value-bold {
    @apply text-sm font-bold text-slate-700 dark:text-slate-200 transition-colors;
}

.btn-primary {
    @apply px-8 py-3 bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-indigo-100 dark:shadow-none hover:bg-indigo-700 active:scale-95 transition-all;
}

.btn-icon {
    @apply w-12 h-12 flex items-center justify-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-500 rounded-2xl hover:text-indigo-600 dark:hover:text-indigo-400 hover:border-indigo-100 dark:hover:border-indigo-800 transition-all;
}
.input-field{
@apply w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold text-slate-700 dark:text-slate-200 transition-colors;
}
/* Hide scrollbars but allow scrolling */
.no-scrollbar::-webkit-scrollbar {
    display: none;
}

.no-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
</style> -->