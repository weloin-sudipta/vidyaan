<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  columns: {
    type: Array,
    required: true
  },
  statusStyles: {
    type: Object,
    default: () => ({})
  }
})

const searchQuery = ref('')
const itemsPerPage = ref(10)
const currentPage = ref(1)

/* 🔎 Search */
const filteredItems = computed(() => {
  if (!searchQuery.value) return props.items

  return props.items.filter(item =>
    Object.values(item).some(val =>
      String(val).toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  )
})

/* 📄 Pagination */
const totalPages = computed(() =>
  Math.ceil(filteredItems.value.length / itemsPerPage.value)
)

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredItems.value.slice(start, start + itemsPerPage.value)
})

watch([searchQuery, itemsPerPage], () => {
  currentPage.value = 1
})
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-center p-6 gap-4">
      <select v-model="itemsPerPage"
              class="border border-gray-300 rounded-md px-3 py-1.5 text-sm outline-none">
        <option :value="10">10</option>
        <option :value="25">25</option>
        <option :value="50">50</option>
      </select>

      <input
        v-model="searchQuery"
        type="search"
        placeholder="Search..."
        class="w-full md:w-64 border border-gray-300 rounded-md px-4 py-2 text-sm outline-none"
      />
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-y border-gray-100 bg-gray-50/50">
            <th v-for="col in columns"
                :key="col.key"
                class="px-6 py-4 text-xs font-semibold uppercase text-gray-500 tracking-wider">
              {{ col.label }}
            </th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-100">
          <tr v-for="item in paginatedItems"
              :key="item.id"
              class="hover:bg-gray-50 transition">

            <td v-for="col in columns"
                :key="col.key"
                class="px-6 py-4 text-sm text-gray-600">

              <!-- Status badge -->
              <template v-if="col.type === 'status'">
                <span
                  :class="[
                    'px-2.5 py-1 rounded-md text-xs font-medium uppercase',
                    statusStyles[item[col.key]]
                  ]">
                  {{ item[col.key] }}
                </span>
              </template>

              <!-- Default -->
              <template v-else>
                {{ item[col.key] }}
              </template>

            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer -->
    <div class="flex justify-between items-center p-6 border-t border-gray-100">
      <span class="text-sm text-gray-500">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }}
        to {{ Math.min(currentPage * itemsPerPage, filteredItems.length) }}
        of {{ filteredItems.length }} entries
      </span>

      <div class="flex gap-1">
        <button
          @click="currentPage--"
          :disabled="currentPage === 1"
          class="px-3 py-1 border rounded disabled:opacity-50">
          Prev
        </button>

        <button
          v-for="page in totalPages"
          :key="page"
          @click="currentPage = page"
          :class="[
            'px-3 py-1 rounded',
            currentPage === page
              ? 'bg-indigo-600 text-white'
              : 'border'
          ]">
          {{ page }}
        </button>

        <button
          @click="currentPage++"
          :disabled="currentPage === totalPages"
          class="px-3 py-1 border rounded disabled:opacity-50">
          Next
        </button>
      </div>
    </div>

  </div>
</template>