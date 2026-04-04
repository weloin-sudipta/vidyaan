<template>
<div class="bg-[#f8fafc] dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-100 transition-colors duration-300 min-h-screen">
  <slot />
</div>
</template>
<script setup>

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
    }]
})
</script>