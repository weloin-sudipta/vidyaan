<script setup>
import { ref, reactive } from 'vue';
import { useToast } from '~/composables/ui/useToast';

const { addToast } = useToast();

definePageMeta({
    layout: 'auth'
})

const step = ref(1);
const loading = ref(false);
const timer = ref(0);

const form = reactive({
    email: '',
    otp: '',
    newPassword: '',
});

const startTimer = () => {
    timer.value = 60;
    const interval = setInterval(() => {
        if (timer.value > 0) timer.value--;
        else clearInterval(interval);
    }, 1000);
};

const handleSendOTP = async () => {
    if (!form.email) return;
    loading.value = true;
    // Simulate API
    setTimeout(() => {
        loading.value = false;
        step.value = 2;
        addToast('Verification code sent!', 'success');
        startTimer();
    }, 1500);
};
</script>

<template>
    <main class="h-screen w-full flex justify-center items-center bg-[#F8FAFC] p-6">
        <div class="w-full max-w-md bg-white rounded-[3rem] shadow-2xl shadow-slate-200 border border-slate-100 overflow-hidden relative">
            
            <div class="bg-slate-900 p-10 text-white relative overflow-hidden">
                <div class="absolute -right-4 -top-4 w-24 h-24 bg-blue-600 rounded-full blur-3xl opacity-30 animate-pulse"></div>
                <div class="absolute -left-4 -bottom-4 w-24 h-24 bg-cyan-400 rounded-full blur-3xl opacity-20"></div>
                
                <div class="relative z-10">
                    <div class="h-12 w-12 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center mb-4 border border-white/10">
                        <i class="fa fa-shield text-cyan-400 text-xl"></i>
                    </div>
                    <h2 class="text-2xl font-black tracking-tight">Account Recovery</h2>
                    <p class="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em] mt-1">
                        {{ step === 1 ? 'Verification Required' : 'Secure OTP Entry' }}
                    </p>
                </div>
            </div>

            <div class="p-10">
                <div v-if="step === 1" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <p class="text-xs font-medium text-slate-500 leading-relaxed">
                        Enter your registered email address. We will send a <span class="text-slate-900 font-bold">6-digit security code</span> to verify your identity.
                    </p>

                    <div class="space-y-2">
                        <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">University Email</label>
                        <div class="relative group">
                            <i class="fa fa-envelope-o absolute left-5 top-1/2 -translate-y-1/2 text-slate-300 group-focus-within:text-blue-500 transition-colors"></i>
                            <input v-model="form.email" type="email" placeholder="student@edu.com" 
                                class="w-full bg-slate-50 border border-slate-100 rounded-2xl py-4 pl-14 pr-4 text-sm font-bold text-slate-700 outline-none focus:bg-white focus:ring-4 focus:ring-blue-500/5 focus:border-blue-500/20 transition-all">
                        </div>
                    </div>

                    <button @click="handleSendOTP" :disabled="loading" 
                        class="w-full bg-slate-900 text-white py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] hover:bg-blue-600 transition-all shadow-xl shadow-blue-100 active:scale-[0.98] flex justify-center items-center gap-3">
                        <i v-if="loading" class="fa fa-circle-o-notch animate-spin"></i>
                        <span>{{ loading ? 'Processing' : 'Request Security Code' }}</span>
                    </button>
                </div>

                <div v-else class="space-y-8 animate-in fade-in slide-in-from-right-8 duration-700">
                    <div class="flex items-center gap-4 p-4 bg-blue-50 rounded-2xl border border-blue-100">
                        <div class="h-10 w-10 bg-white rounded-xl flex items-center justify-center text-blue-600 shadow-sm shrink-0">
                            <i class="fa fa-unlock-alt animate-bounce"></i>
                        </div>
                        <p class="text-[10px] font-bold text-blue-700 leading-tight">
                            Verification code sent to <span class="block text-slate-900 font-black">{{ form.email }}</span>
                        </p>
                    </div>

                    <div class="space-y-4">
                        <div class="space-y-2 text-center">
                            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Enter 6-Digit Code</label>
                            <input v-model="form.otp" type="text" maxlength="6" placeholder="······" 
                                class="w-full bg-slate-50 border border-slate-200 rounded-2xl py-5 text-center text-3xl font-black tracking-[0.5em] text-blue-600 outline-none focus:bg-white focus:border-blue-400 transition-all shadow-inner">
                        </div>

                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">New Password</label>
                            <input v-model="form.newPassword" type="password" placeholder="••••••••"
                                class="w-full bg-slate-50 border border-slate-100 rounded-2xl py-4 px-6 text-sm font-bold text-slate-700 outline-none focus:bg-white focus:ring-4 focus:ring-blue-500/5 transition-all">
                        </div>
                    </div>

                    <button class="w-full py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] text-white shadow-lg shadow-blue-200 active:scale-[0.98] transition-all"
                        style="background: linear-gradient(to right, #2563eb, #06b6d4)">
                        Verify & Update Password
                    </button>

                    <div class="flex flex-col items-center gap-4">
                        <button :disabled="timer > 0" @click="startTimer" 
                            class="text-[10px] font-black uppercase tracking-widest transition-colors"
                            :class="timer > 0 ? 'text-slate-300' : 'text-blue-600 hover:text-cyan-500'">
                            Resend Code {{ timer > 0 ? `(${timer}s)` : '' }}
                        </button>
                        
                        <div class="h-[1px] w-12 bg-slate-100"></div>
                        
                        <button @click="step = 1" class="text-[10px] font-black text-slate-400 uppercase tracking-widest hover:text-slate-900 transition-colors">
                            <i class="fa fa-chevron-left mr-1"></i> Use different email
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </main>
</template>

<style scoped>
/* Cool Subtle Background Animation */
main {
    background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
    background-size: 32px 32px;
}

.animate-in {
    animation-fill-mode: both;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideRight {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

.slide-in-from-bottom-4 { animation: slideUp 0.7s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-in-from-right-8 { animation: slideRight 0.7s cubic-bezier(0.16, 1, 0.3, 1); }
</style>