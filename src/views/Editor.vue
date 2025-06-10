<template>
  <div class="editor">
    <!-- Header Toolbar -->
    <header class="editor-header">
      <div class="header-left">
        <div class="logo">
          <span class="logo-icon">🎯</span>
          <span class="logo-text">AI-PPT</span>
        </div>
        <div class="presentation-title">
          <input 
            v-model="presentationStore.presentation.title"
            class="title-input"
            placeholder="Presentation Title"
          />
        </div>
      </div>
      
      <div class="header-center">
        <ToolbarMain />
      </div>
      
      <div class="header-right">
        <AIPanel />
        <button class="btn btn-primary" @click="startPresentation">
          <span>▶</span>
          Present
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <div class="editor-content">
      <!-- Left Sidebar -->
      <aside class="sidebar-left">
        <SlideThumbnails />
      </aside>

      <!-- Canvas Area -->
      <main class="canvas-area">
        <div class="canvas-container">
          <CanvasEditor />
        </div>
        
        <!-- Zoom Controls -->
        <div class="zoom-controls">
          <button class="btn btn-sm" @click="zoomOut">-</button>
          <span class="zoom-level">{{ Math.round(presentationStore.canvas.zoom * 100) }}%</span>
          <button class="btn btn-sm" @click="zoomIn">+</button>
          <button class="btn btn-sm" @click="resetZoom">Fit</button>
        </div>
      </main>

      <!-- Right Sidebar -->
      <aside class="sidebar-right">
        <PropertyPanel />
      </aside>
    </div>

    <!-- Status Bar -->
    <footer class="status-bar">
      <div class="status-left">
        <span class="status-item">
          Slide {{ presentationStore.canvas.activeSlide + 1 }} of {{ presentationStore.totalSlides }}
        </span>
        <span class="status-item" v-if="aiStore.isAIReady">
          🤖 AI Ready
        </span>
        <span class="status-item" v-if="aiStore.suggestionCount > 0">
          💡 {{ aiStore.suggestionCount }} suggestions
        </span>
      </div>
      
      <div class="status-right">
        <span class="status-item">
          {{ presentationStore.getPerformanceMetrics().totalOperations || 0 }} operations
        </span>
        <span class="status-item">
          {{ presentationStore.presentation.settings.width }}×{{ presentationStore.presentation.settings.height }}
        </span>
      </div>
    </footer>

    <!-- AI Suggestions Overlay -->
    <AISuggestions v-if="aiStore.suggestionCount > 0" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { usePresentationStore, useAIStore } from '@/stores'
import ToolbarMain from '@/components/Toolbar/ToolbarMain.vue'
import AIPanel from '@/components/AI/AIPanel.vue'
import SlideThumbnails from '@/components/Sidebar/SlideThumbnails.vue'
import CanvasEditor from '@/components/Canvas/CanvasEditor.vue'
import PropertyPanel from '@/components/Sidebar/PropertyPanel.vue'
import AISuggestions from '@/components/AI/AISuggestions.vue'

const presentationStore = usePresentationStore()
const aiStore = useAIStore()

onMounted(() => {
  // Initialize keyboard shortcuts
  document.addEventListener('keydown', handleKeydown)
  
  // Load presentation if ID provided
  const presentationId = (window as any).location.pathname.split('/')[2]
  if (presentationId) {
    loadPresentation(presentationId)
  }
  
  // Auto-save setup
  setInterval(autoSave, 30000) // Auto-save every 30 seconds
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

function handleKeydown(event: KeyboardEvent) {
  const isCtrlOrCmd = event.ctrlKey || event.metaKey
  
  if (isCtrlOrCmd) {
    switch (event.key) {
      case 'z':
        event.preventDefault()
        if (event.shiftKey) {
          presentationStore.redo()
        } else {
          presentationStore.undo()
        }
        break
      case 'c':
        event.preventDefault()
        if (presentationStore.selectedElements.length > 0) {
          presentationStore.copyElements(presentationStore.selectedElements)
        }
        break
      case 'v':
        event.preventDefault()
        presentationStore.pasteElements()
        break
      case 's':
        event.preventDefault()
        autoSave()
        break
      case 'n':
        event.preventDefault()
        presentationStore.createSlide()
        break
    }
  }
  
  // Navigation shortcuts
  switch (event.key) {
    case 'Delete':
    case 'Backspace':
      if (presentationStore.selectedElements.length > 0) {
        event.preventDefault()
        presentationStore.selectedElements.forEach(id => {
          presentationStore.removeElement(id)
        })
        presentationStore.clearSelection()
      }
      break
    case 'ArrowLeft':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        previousSlide()
      }
      break
    case 'ArrowRight':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        nextSlide()
      }
      break
    case 'Escape':
      presentationStore.clearSelection()
      break
  }
}

function zoomIn() {
  presentationStore.setZoom(presentationStore.canvas.zoom * 1.2)
}

function zoomOut() {
  presentationStore.setZoom(presentationStore.canvas.zoom / 1.2)
}

function resetZoom() {
  presentationStore.setZoom(1)
  presentationStore.setCanvasOffset(0, 0)
}

function previousSlide() {
  const newIndex = Math.max(0, presentationStore.canvas.activeSlide - 1)
  presentationStore.setActiveSlide(newIndex)
}

function nextSlide() {
  const newIndex = Math.min(
    presentationStore.totalSlides - 1, 
    presentationStore.canvas.activeSlide + 1
  )
  presentationStore.setActiveSlide(newIndex)
}

function startPresentation() {
  // This would open the presentation in fullscreen mode
  console.log('Starting presentation...')
}

async function loadPresentation(id: string) {
  try {
    const response = await fetch(`/api/presentations/${id}`)
    if (response.ok) {
      const presentationData = await response.json()
      presentationStore.loadPresentation(presentationData)
    }
  } catch (error) {
    console.error('Failed to load presentation:', error)
  }
}

async function autoSave() {
  try {
    const presentationData = presentationStore.exportPresentation()
    const response = await fetch(`/api/presentations/${presentationData.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(presentationData)
    })
    
    if (response.ok) {
      console.log('✅ Auto-saved presentation')
    }
  } catch (error) {
    console.warn('Auto-save failed:', error)
  }
}
</script>

<style scoped>
.editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--background);
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--surface);
  border-bottom: 1px solid var(--border);
  height: 60px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  flex: 1;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 600;
  color: var(--primary);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: var(--font-size-lg);
}

.presentation-title {
  flex: 1;
  max-width: 300px;
}

.title-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: var(--font-size-lg);
  font-weight: 500;
  padding: var(--spacing-xs);
  border-radius: var(--border-radius);
}

.title-input:hover,
.title-input:focus {
  background-color: var(--border-light);
}

.header-center {
  flex: 2;
  display: flex;
  justify-content: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex: 1;
  justify-content: flex-end;
}

.editor-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar-left {
  width: 240px;
  background-color: var(--surface);
  border-right: 1px solid var(--border);
  flex-shrink: 0;
}

.canvas-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background-color: var(--background);
}

.canvas-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.zoom-controls {
  position: absolute;
  bottom: var(--spacing-md);
  right: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background-color: var(--surface);
  padding: var(--spacing-xs);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.zoom-level {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  min-width: 40px;
  text-align: center;
}

.sidebar-right {
  width: 280px;
  background-color: var(--surface);
  border-left: 1px solid var(--border);
  flex-shrink: 0;
}

.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-xs) var(--spacing-md);
  background-color: var(--surface);
  border-top: 1px solid var(--border);
  height: 32px;
  flex-shrink: 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.status-left,
.status-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

/* Responsive design */
@media (max-width: 1200px) {
  .sidebar-right {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .sidebar-left,
  .sidebar-right {
    display: none;
  }
  
  .header-left,
  .header-right {
    flex: 0;
  }
  
  .header-center {
    flex: 1;
  }
  
  .presentation-title {
    max-width: 200px;
  }
}
</style>