<template>
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-rose-500 relative overflow-hidden">

  <!-- Animated Background Blobs -->
  <div class="absolute -top-32 -left-32 w-96 h-96 bg-white/20 rounded-full blur-3xl animate-pulse"></div>
  <div class="absolute -bottom-32 -right-32 w-96 h-96 bg-white/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>

  <!-- Login Card -->
  <div class="relative z-10 w-full max-w-xl p-10 pb-5">

    <div class="bg-white/20 backdrop-blur-xl border border-white/30 shadow-2xl rounded-[2.5rem] p-10">

      <!-- Logo -->
      <div class="text-center mb-5">
        <div class="w-16 h-16 mx-auto bg-white/30 rounded-3xl flex items-center justify-center shadow-lg backdrop-blur-md">
          <i class="fa fa-graduation-cap text-3xl text-indigo-600"></i>
        </div>
        <!-- <h1 class="mt-6 text-3xl font-black text-indigo-600 tracking-tight">
          {{ config.public.appName }} ERP
        </h1> -->
        <p class="text-white/70 text-xs uppercase tracking-[0.3em] mt-2">
          Academic Management System
        </p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handlelogin" class="space-y-6">

        <!-- Email -->
        <div>
          <label class="text-[10px] font-black text-white/70 uppercase tracking-widest">
            Email Address
          </label>
          <input
          v-model="email"
            type="email"
            placeholder="Enter your email"
            class="w-full mt-2 px-5 py-3 rounded-2xl bg-white/30 border border-white/40 text-white placeholder-white/60 text-sm font-semibold outline-none focus:ring-4 focus:ring-white/30 transition-all"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="text-[10px] font-black text-white/70 uppercase tracking-widest">
            Password
          </label>
          <input
            v-model="password"
            type="password"
            placeholder="Enter your password"
            class="w-full mt-2 px-5 py-3 rounded-2xl bg-white/30 border border-white/40 text-white placeholder-white/60 text-sm font-semibold outline-none focus:ring-4 focus:ring-white/30 transition-all"
          />
        </div>

        <!-- Remember + Forgot -->
        <div class="flex items-center justify-between text-xs text-white/70">
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" class="accent-white w-4 h-4">
            Remember me
          </label>
          <a href="#" class="hover:text-white transition">
            Forgot password?
          </a>
        </div>

        <!-- Button -->
        <button
          type="submit"
          class="w-full py-3.5 rounded-2xl bg-white text-indigo-600 font-black uppercase tracking-widest text-xs shadow-xl hover:scale-[1.02] hover:shadow-2xl transition-all duration-300 active:scale-95"
        >
          Sign In
        </button>

      </form>

      <!-- Divider -->
      <!-- <div class="flex items-center gap-4 my-8">
        <div class="flex-1 h-px bg-white/30"></div>
        <span class="text-white/60 text-xs uppercase tracking-widest">or</span>
        <div class="flex-1 h-px bg-white/30"></div>
      </div> -->

      <!-- Social Login -->
      <!-- <div class="flex gap-4">
        <button class="flex-1 py-3 rounded-2xl bg-white/30 text-white font-bold text-xs hover:bg-white/40 transition">
          Google
        </button>
        <button class="flex-1 py-3 rounded-2xl bg-white/30 text-white font-bold text-xs hover:bg-white/40 transition">
          Microsoft
        </button>
      </div> -->

    </div>

    <!-- Footer -->
    <p class="text-center text-white/60 text-[10px] font-bold uppercase tracking-widest mt-8">
      © 2026 Vidyaan ERP — Empowering Digital Education
    </p>

  </div>

</div>
</template>

<script setup>
definePageMeta({
    layout: 'auth'
})

import {login} from '~/composables/auth/useAuth'
import { useRouter } from 'vue-router'
import { useToast } from '~/composables/ui/useToast'

const router = useRouter()
const { addToast } = useToast()

const email = ref('')
const password = ref('')

const handlelogin=async()=>{
  try {
    console.log(email.value, password.value);
    await login(email.value, password.value)
    addToast('Welcome back!', 'success')
    router.push('/')
  } catch (error) {
    addToast('Invalid login credentials', 'error')
    console.log(error);
    
    throw error
  }
}

const config = useRuntimeConfig()
useSeoMeta({
    title: `Login - ${config.public.appName}`,
    description: `Access your Vidyaan ERP account to manage your academic journey. Our secure login portal ensures your data is protected while providing seamless access to your personalized dashboard, course materials, and performance insights.`,
    keywords: 'login, authentication, secure access, user account, Vidyaan ERP'
})
</script>