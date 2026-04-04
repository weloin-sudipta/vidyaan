<template>
    <!-- simple overview/redirect page for academics section -->
    <div class="min-h-screen flex flex-col items-center justify-center bg-[#f8fafc] p-4">
        <h1 class="text-4xl font-black mb-6">Academics</h1>
        <p class="text-lg text-slate-700 mb-8">Select a module from the sidebar or below to continue.</p>
        <div class="space-x-4">
            <NuxtLink class="btn-outline" to="/academics/subjects">Subjects</NuxtLink>
            <NuxtLink class="btn-outline" to="/academics/studyMaterial">Study Materials</NuxtLink>
            <NuxtLink class="btn-outline" to="/academics/timeTable">Timetable</NuxtLink>
            <NuxtLink class="btn-outline" to="/academics/assignments">Assignments</NuxtLink>
        </div>
    </div>
</template>

<script setup>
// you could also perform an immediate redirect if preferred:
// const router = useRouter();
// router.replace('/academics/subjects');
</script>
