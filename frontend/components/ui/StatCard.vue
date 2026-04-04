<template>
  <div
    class="bg-white border border-gray-100 shadow-sm rounded-2xl p-6 hover:shadow-md transition duration-300"
  >
    <!-- Icon -->
    <div
      :class="[
        'w-12 h-12 rounded-xl mb-4 flex items-center justify-center text-white text-xl shadow-md',
        color
      ]"
    >
      <i :class="icon"></i>
    </div>

    <!-- Label -->
    <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider">
      {{ label }}
    </p>

    <!-- Value -->
    <h3 class="text-2xl font-bold text-gray-800 mt-1">
      {{ value }}
    </h3>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'bg-indigo-500'
  }
})
</script>