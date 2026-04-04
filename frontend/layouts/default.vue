<script setup>
import AppSideBar from '~/components/ui/AppSideBar.vue'
import AppNavBar from '~/components/ui/AppNavBar.vue'

const config = useRuntimeConfig()
const firstLetter = config.public.appName.charAt(0).toUpperCase()

// Create SVG favicon dynamically
const svgIcon = `
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2563eb;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e40af;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="14" fill="url(#grad)" />
  <text x="50%" y="50%" dy=".35em" text-anchor="middle"
        fill="white"
        font-family="Arial, sans-serif"
        font-size="36"
        font-weight="bold">
    ${firstLetter}
  </text>
</svg>
`

useHead({
  link: [
    {
      rel: 'icon',
      type: 'image/svg+xml',
      href: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgIcon)
    },
    {
      rel: 'stylesheet',
      href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
    }
  ]
})
</script>

<template>
  <div class="flex h-screen w-full overflow-hidden bg-[#f5f5f9] dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-100 transition-colors duration-300">

    <!-- Sidebar -->
    <AppSideBar />

    <!-- Main Area -->
    <div class="flex flex-col flex-1 min-w-0 h-full overflow-hidden">

      <!-- Navbar -->
      <AppNavBar />

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto p-6 pt-2 custom-scrollbar">
        <slot />
      </main>

    </div>
  </div>
</template>