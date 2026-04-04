<template>

    <div class="bg-indigo-900 p-5 rounded-xl shadow-sm text-white relative overflow-hidden">
        <div class="relative z-10">
            <h6 class="font-bold mb-1">Annual Tech Fest</h6>
            <p class="text-xs opacity-70 mb-4">Join the biggest event of the year.</p>
            <div class="flex -space-x-2">
                <img v-for="i in 4" :key="i" :src="`https://i.pravatar.cc/100?img=${i + 10}`"
                    class="w-8 h-8 rounded-full border-2 border-indigo-900" />
                <div
                    class="w-8 h-8 rounded-full bg-indigo-700 border-2 border-indigo-900 flex items-center justify-center text-[10px] font-bold">
                    +12</div>
            </div>
        </div>
        <i class="fa fa-calendar absolute -right-4 -bottom-4 text-8xl text-white opacity-10"></i>
    </div>
</template>
<script setup>
</script>