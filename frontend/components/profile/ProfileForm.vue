<template>
  <div>
    <!-- Header -->
    <UiCard as="header" class="flex flex-col lg:flex-row justify-between items-center gap-6 mb-6">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-100">
          <i class="fa fa-pencil text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-black tracking-tight text-slate-800">Edit Student Profile</h1>
          <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mt-1">Updates will be synced across the academic portal</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button @click="$router.back()" class="btn-outline">Discard</button>
        <button @click="saveProfile" :disabled="saving" class="btn-primary">
          <span v-if="saving">Saving...</span>
          <span v-else>Save Changes</span>
        </button>
      </div>
    </UiCard>

    <!-- Form -->
    <form @submit.prevent="saveProfile" class="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      <!-- Left Column -->
      <div class="lg:col-span-4 space-y-6">
        <!-- Photo -->
        <UiCard class="text-center">
          <h4 class="label-tiny mb-6">Profile Photograph</h4>
          <div class="relative w-48 h-48 mx-auto mb-6 group">
            <div class="w-full h-full rounded-[2.5rem] overflow-hidden ring-8 ring-slate-50 shadow-inner bg-slate-100">
              <img v-if="photoPreview" :src="photoPreview" class="w-full h-full object-cover transition-opacity group-hover:opacity-50" @error="photoPreview = null" />
              <div v-else class="w-full h-full flex items-center justify-center">
                <span class="text-4xl font-black text-indigo-600">{{ initials }}</span>
              </div>
            </div>
            <label class="absolute inset-0 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer transition-opacity">
              <i class="fa fa-camera text-2xl text-indigo-600 mb-2"></i>
              <span class="text-[10px] font-black uppercase text-indigo-600">Change Photo</span>
              <input type="file" class="hidden" @change="handlePhotoUpload" accept="image/*" ref="fileInput" />
            </label>
          </div>
          <p v-if="uploadingPhoto" class="text-[10px] font-bold text-indigo-500 uppercase">Uploading...</p>
          <p v-else class="text-[9px] font-bold text-slate-400 uppercase">Allowed JPG, GIF or PNG. Max size 2MB</p>
        </UiCard>

        <!-- Core Identity -->
        <UiCard class="space-y-4">
          <h4 class="label-tiny mb-4">Core Identity</h4>
          <div>
            <label class="label-tiny ml-1">Full Student Name</label>
            <input v-model="form.name" type="text" class="input-modern" placeholder="Full Name">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label-tiny ml-1">Admission No</label>
              <input v-model="form.admNo" type="text" class="input-modern bg-slate-50 cursor-not-allowed" disabled>
            </div>
            <div>
              <label class="label-tiny ml-1">Roll No</label>
              <input v-model="form.rollNo" type="text" class="input-modern">
            </div>
          </div>
        </UiCard>
      </div>

      <!-- Right Column -->
      <div class="lg:col-span-8 space-y-6">

        <!-- Academic Details -->
        <UiCard>
          <div class="flex items-center gap-3 mb-8">
            <div class="w-1.5 h-6 bg-indigo-600 rounded-full"></div>
            <h3 class="text-lg font-black text-slate-800 tracking-tight">Academic Details</h3>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="(val, key) in form.academic" :key="key">
              <label class="label-tiny ml-1">{{ key }}</label>
              <select v-if="key === 'Religion'" v-model="form.academic[key]" class="input-modern">
                <option>Christianity</option>
                <option>Islam</option>
                <option>Hinduism</option>
                <option>Other</option>
              </select>
              <input v-else v-model="form.academic[key]" type="text" class="input-modern">
            </div>
          </div>
        </UiCard>

        <!-- Parental & Contact -->
        <UiCard>
          <div class="flex items-center gap-3 mb-8">
            <div class="w-1.5 h-6 bg-emerald-500 rounded-full"></div>
            <h3 class="text-lg font-black text-slate-800 tracking-tight">Parental & Contact Information</h3>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="label-tiny ml-1">Father's Name & Profession</label>
              <input v-model="form.secondary['Parental Records']['Father']" type="text" class="input-modern">
            </div>
            <div>
              <label class="label-tiny ml-1">Mother's Name & Profession</label>
              <input v-model="form.secondary['Parental Records']['Mother']" type="text" class="input-modern">
            </div>
            <div>
              <label class="label-tiny ml-1">Contact Mobile</label>
              <input v-model="form.secondary['Contact & Security']['Mobile']" type="tel" class="input-modern">
            </div>
            <div>
              <label class="label-tiny ml-1">Email Address</label>
              <input v-model="form.secondary['Contact & Security']['Email']" type="email" class="input-modern">
            </div>
          </div>
        </UiCard>

        <!-- Logistics & Address -->
        <UiCard>
          <div class="flex items-center gap-3 mb-8">
            <div class="w-1.5 h-6 bg-orange-500 rounded-full"></div>
            <h3 class="text-lg font-black text-slate-800 tracking-tight">Logistics & Address</h3>
          </div>
          <div class="space-y-6">
            <div>
              <label class="label-tiny ml-1">Current Address</label>
              <textarea v-model="form.logistics['Current Address']" rows="3" class="input-modern py-4"></textarea>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="label-tiny ml-1">Transport Route</label>
                <input v-model="form.logistics['Transport Route']" type="text" class="input-modern">
              </div>
              <div>
                <label class="label-tiny ml-1">Hostel Room</label>
                <input v-model="form.logistics['Hostel Facility']" type="text" class="input-modern">
              </div>
            </div>
          </div>
        </UiCard>

      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileLoader, updateProfile } from '~/composables/useProfile'
import { useToast } from '~/composables/useToast'

const { addToast } = useToast()

const $router = useRouter()

const photoPreview = ref(null)
const photoFile = ref(null)
const uploadingPhoto = ref(false)
const saving = ref(false)

const form = ref({
  name: "",
  admNo: "",
  rollNo: "",
  academic: {
    "Admission Date": "",
    "RTE Status": "",
    "Category": "",
    "Caste": "",
    "Religion": "",
    "Blood Group": "",
    "Student House": ""
  },
  secondary: {
    "Parental Records": { "Father": "", "Mother": "" },
    "Contact & Security": { "Mobile": "", "Email": "" }
  },
  logistics: {
    "Transport Route": "",
    "Hostel Facility": "",
    "Current Address": ""
  }
})

const initials = computed(() => {
  const name = form.value.name || ''
  return name.split(' ').filter(Boolean).map(w => w[0]?.toUpperCase()).slice(0, 2).join('')
})

const { profileData, loadProfile } = useProfileLoader()

onMounted(async () => {
  try {
    await loadProfile()
    const profile = profileData.value
    if (!profile) return

    form.value.name = profile.full_name || ""
    form.value.admNo = profile.student_id?.split('-').pop() || ""
    form.value.rollNo = profile.roll_number || ""

    form.value.academic["Admission Date"] = profile.joining_date || ""
    form.value.academic["Category"] = profile.category || ""
    form.value.academic["Caste"] = profile.caste || ""
    form.value.academic["Religion"] = profile.religion || ""
    form.value.academic["Blood Group"] = profile.blood_group || ""

    form.value.secondary["Contact & Security"]["Mobile"] = profile.mobile_number || ""
    form.value.secondary["Contact & Security"]["Email"] = profile.email || ""

    form.value.secondary["Parental Records"]["Father"] = profile.guardians?.[0]?.guardian_name || ""
    form.value.secondary["Parental Records"]["Mother"] = profile.guardians?.[1]?.guardian_name || ""

    form.value.logistics["Hostel Facility"] = profile.hostel_facility || ""
    form.value.logistics["Current Address"] = `${profile.address_line_1 || ""} ${profile.address_line_2 || ""}`.trim()

    if (profile.photo_url) {
      photoPreview.value = profile.photo_url
    }
  } catch (err) {
    console.error("Failed to load profile:", err)
  }
})

const handlePhotoUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 2 * 1024 * 1024) {
    addToast("Image must be under 2MB", 'error')
    return
  }

  photoFile.value = file
  photoPreview.value = URL.createObjectURL(file)

  uploadingPhoto.value = true
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
      photoPreview.value = fileUrl
      photoFile.value = null
    }
  } catch (err) {
    console.error("Photo upload failed:", err)
    addToast("Failed to upload photo. Please try again.", 'error')
  } finally {
    uploadingPhoto.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const nameParts = (form.value.name || '').split(' ').filter(Boolean)
    const payload = {
      firstName: nameParts[0] || '',
      middleName: nameParts.length > 2 ? nameParts.slice(1, -1).join(' ') : '',
      lastName: nameParts.length > 1 ? nameParts[nameParts.length - 1] : '',
      mobile: form.value.secondary["Contact & Security"]["Mobile"],
      language: 'en',
      timezone: 'Asia/Kolkata',
      user_image: photoPreview.value || undefined,
    }

    const res = await updateProfile(payload)

    if (res?.error) {
      addToast("Failed to update profile: " + res.error, 'error')
    } else {
      addToast("Profile Updated Successfully!", 'success')
    }
  } catch (err) {
    console.error("Error saving profile:", err)
    addToast("An unexpected error occurred while updating profile.", 'error')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.label-tiny {
  @apply text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2;
}
.input-modern {
  @apply w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-3 text-xs font-bold text-slate-700 outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500/50 transition-all;
}
.btn-primary {
  @apply px-8 py-3 bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-indigo-100 hover:bg-indigo-700 active:scale-95 transition-all disabled:opacity-50;
}
.btn-outline {
  @apply px-8 py-3 bg-white border border-slate-200 text-slate-400 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] hover:bg-slate-50 transition-all;
}
</style>
