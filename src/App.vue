<template>
  <div id="app" class="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useAIStore } from '@/stores'

const aiStore = useAIStore()

onMounted(() => {
  // Start AI auto-suggestions
  aiStore.startAutoSuggestions()
  
  // Global keyboard shortcuts
  document.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  // Stop AI auto-suggestions
  aiStore.stopAutoSuggestions()
  
  // Remove global listeners
  document.removeEventListener('keydown', handleGlobalKeydown)
})

function handleGlobalKeydown(event: KeyboardEvent) {
  // Global shortcuts that work anywhere in the app
  if (event.ctrlKey || event.metaKey) {
    switch (event.key) {
      case 's':
        event.preventDefault()
        // Auto-save functionality would go here
        break
      case 'z':
        if (event.shiftKey) {
          event.preventDefault()
          // Redo
        } else {
          event.preventDefault()
          // Undo
        }
        break
    }
  }
}
</script>

<style>
.app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>