<template>
  <div class="book-card">
    <!-- Book details -->
    <div class="book-info">
      <h3>{{ book.title }}</h3>
      <p class="author">{{ book.author }}</p>
      <p class="isbn" v-if="book.isbn">ISBN: {{ book.isbn }}</p>
    </div>

    <!-- Success and Error messages -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Request/Cancel Button with state change -->
    <button
      @click="handleRequestClick"
      :disabled="loading"
      :class="['request-btn', getButtonStatus(book.name || book.id)]"
    >
      <span v-if="loading" class="spinner"></span>
      {{ getButtonText(book.name || book.id) }}
    </button>
  </div>
</template>

<script setup>
import { useBookRequest } from '../composable/useBookRequest'

const props = defineProps({
  book: {
    type: Object,
    required: true,
    // book should have: id, name, title, author, isbn
  },
})

const {
  loading,
  error,
  successMessage,
  isBookRequested,
  getButtonText,
  getButtonStatus,
  toggleBookRequest,
} = useBookRequest()

const handleRequestClick = async () => {
  await toggleBookRequest(props.book)
}
</script>

<style scoped>
.book-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background-color: #f9f9f9;
}

.book-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.author {
  margin: 0 0 4px 0;
  color: #666;
  font-size: 14px;
}

.isbn {
  margin: 0;
  color: #999;
  font-size: 12px;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 14px;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 14px;
}

.request-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.request-btn.request {
  background-color: #007bff;
  color: white;
}

.request-btn.request:hover:not(:disabled) {
  background-color: #0056b3;
}

.request-btn.cancel {
  background-color: #dc3545;
  color: white;
}

.request-btn.cancel:hover:not(:disabled) {
  background-color: #c82333;
}

.request-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
