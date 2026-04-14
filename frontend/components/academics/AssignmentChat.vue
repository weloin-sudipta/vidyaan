<template>
  <div class="flex flex-col h-full bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/50">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
          <i class="fas fa-comments"></i>
        </div>
        <h3 class="text-xs font-black uppercase tracking-widest text-slate-700 dark:text-slate-200">Discussion</h3>
      </div>
      <div class="flex items-center gap-3">
        <button @click="$emit('refresh')" class="w-6 h-6 flex items-center justify-center rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-400 transition-colors">
          <i class="fas fa-sync-alt text-[10px]"></i>
        </button>
        <span class="px-2 py-0.5 rounded-md bg-slate-200 dark:bg-slate-700 text-[10px] font-bold text-slate-500 dark:text-slate-400">
          {{ messages.length }}
        </span>
      </div>
    </div>

    <!-- Message List -->
    <div ref="messageList" class="flex-1 overflow-y-auto p-6 space-y-6 no-scrollbar min-h-[300px]">
      <div v-for="msg in messages" :key="msg.id" 
           :class="['flex gap-4 group', msg.is_me ? 'flex-row-reverse' : 'flex-row']">
        
        <UiAvatar :name="msg.author" size="sm" class="mt-1" />

        <div :class="['flex flex-col max-w-[80%]', msg.is_me ? 'items-end' : 'items-start']">
          <div class="flex items-center gap-2 mb-1 px-1">
            <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500">{{ msg.author }}</span>
            <span class="text-[9px] text-slate-300 dark:text-slate-600">{{ formatTime(msg.creation) }}</span>
          </div>
          
          <div :class="[
            'px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm',
            msg.is_me 
              ? 'bg-indigo-600 text-white rounded-tr-none' 
              : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-tl-none border border-slate-200 dark:border-slate-700'
          ]">
            <div v-html="sanitize(msg.content)"></div>
          </div>
        </div>
      </div>

      <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center text-center opacity-40 py-10">
        <i class="fas fa-comment-dots text-4xl mb-4"></i>
        <p class="text-xs font-bold uppercase tracking-widest">No messages yet</p>
        <p class="text-[10px] mt-1">Start the conversation below</p>
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-4 bg-slate-50/50 dark:bg-slate-800/30 border-t border-slate-100 dark:border-slate-800">
      <div class="relative">
        <textarea
          v-model="newMessage"
          rows="1"
          @keydown.enter.prevent="handleSend"
          placeholder="Write a message..."
          class="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl pl-4 pr-12 py-3 text-sm focus:ring-2 focus:ring-indigo-500 outline-none transition-all resize-none dark:text-white"
        ></textarea>
        <button 
          @click="handleSend"
          :disabled="!newMessage.trim() || sending"
          class="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-30 disabled:scale-95 transition-all shadow-md active:scale-90"
        >
          <i v-if="sending" class="fa fa-spinner fa-spin text-xs"></i>
          <i v-else class="fas fa-paper-plane text-xs"></i>
        </button>
      </div>
      <p class="text-[9px] text-slate-400 mt-2 px-1">Press Enter to send</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import UiAvatar from '~/components/ui/UiAvatar.vue'

const props = defineProps<{
  messages: any[]
  sending?: boolean
}>()

const emit = defineEmits(['send', 'refresh'])

const newMessage = ref('')
const messageList = ref<HTMLElement | null>(null)

const handleSend = () => {
  if (!newMessage.value.trim() || props.sending) return
  emit('send', newMessage.value)
  newMessage.value = ''
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageList.value) {
    messageList.value.scrollTop = messageList.value.scrollHeight
  }
}

watch(() => props.messages.length, scrollToBottom)
onMounted(scrollToBottom)

const formatTime = (d: string) => {
  if (!d) return ''
  const date = new Date(d)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const sanitize = (content: any) => {
  if (!content || typeof content !== 'string') return ''
  // Very basic sanitize for demonstration, in real app use a library
  return content.replace(/<script.*?>.*?<\/script>/gi, '')
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
