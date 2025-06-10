<template>
  <div class="toolbar-main">
    <div class="toolbar-section">
      <!-- File operations -->
      <button class="btn btn-ghost btn-sm" @click="newPresentation" title="New">
        📄
      </button>
      <button class="btn btn-ghost btn-sm" @click="openPresentation" title="Open">
        📁
      </button>
      <button class="btn btn-ghost btn-sm" @click="savePresentation" title="Save">
        💾
      </button>
      <div class="toolbar-divider"></div>
    </div>

    <div class="toolbar-section">
      <!-- History -->
      <button 
        class="btn btn-ghost btn-sm" 
        :disabled="!presentationStore.canUndo"
        @click="presentationStore.undo()"
        title="Undo"
      >
        ↶
      </button>
      <button 
        class="btn btn-ghost btn-sm"
        :disabled="!presentationStore.canRedo"
        @click="presentationStore.redo()"
        title="Redo"
      >
        ↷
      </button>
      <div class="toolbar-divider"></div>
    </div>

    <div class="toolbar-section">
      <!-- Add elements -->
      <div class="dropdown" ref="addDropdown">
        <button 
          class="btn btn-ghost btn-sm dropdown-trigger"
          @click="toggleAddDropdown"
          title="Add Element"
        >
          ➕ Add
        </button>
        <div v-if="showAddDropdown" class="dropdown-menu">
          <button class="dropdown-item" @click="addText">
            📝 Text
          </button>
          <button class="dropdown-item" @click="addImage">
            🖼️ Image
          </button>
          <button class="dropdown-item" @click="addShape">
            🔷 Shape
          </button>
          <button class="dropdown-item" @click="addChart">
            📊 Chart
          </button>
          <button class="dropdown-item" @click="addTable">
            📋 Table
          </button>
        </div>
      </div>
      <div class="toolbar-divider"></div>
    </div>

    <div class="toolbar-section">
      <!-- Slide operations -->
      <button class="btn btn-ghost btn-sm" @click="addSlide" title="New Slide">
        📄+
      </button>
      <button 
        class="btn btn-ghost btn-sm"
        :disabled="presentationStore.totalSlides <= 1"
        @click="deleteSlide"
        title="Delete Slide"
      >
        🗑️
      </button>
      <button class="btn btn-ghost btn-sm" @click="duplicateSlide" title="Duplicate Slide">
        📋
      </button>
      <div class="toolbar-divider"></div>
    </div>

    <div class="toolbar-section">
      <!-- Themes -->
      <div class="dropdown" ref="themeDropdown">
        <button 
          class="btn btn-ghost btn-sm dropdown-trigger"
          @click="toggleThemeDropdown"
          title="Themes"
        >
          🎨 Theme
        </button>
        <div v-if="showThemeDropdown" class="dropdown-menu">
          <button 
            v-for="theme in themes"
            :key="theme.name"
            class="dropdown-item theme-item"
            @click="applyTheme(theme)"
          >
            <div class="theme-preview" :style="getThemePreview(theme)"></div>
            {{ theme.name }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { usePresentationStore } from '@/stores'

const presentationStore = usePresentationStore()

const showAddDropdown = ref(false)
const showThemeDropdown = ref(false)
const addDropdown = ref<HTMLElement>()
const themeDropdown = ref<HTMLElement>()

const themes = ref([
  {
    name: 'Default',
    colors: {
      primary: '#1976D2',
      secondary: '#424242',
      background: '#FFFFFF',
      text: '#333333',
      accent: '#FF5722'
    }
  },
  {
    name: 'Dark',
    colors: {
      primary: '#BB86FC',
      secondary: '#03DAC6',
      background: '#121212',
      text: '#FFFFFF',
      accent: '#CF6679'
    }
  },
  {
    name: 'Nature',
    colors: {
      primary: '#4CAF50',
      secondary: '#8BC34A',
      background: '#F1F8E9',
      text: '#2E7D32',
      accent: '#FF9800'
    }
  },
  {
    name: 'Ocean',
    colors: {
      primary: '#2196F3',
      secondary: '#00BCD4',
      background: '#E3F2FD',
      text: '#0D47A1',
      accent: '#FF5722'
    }
  },
  {
    name: 'Sunset',
    colors: {
      primary: '#FF5722',
      secondary: '#FF9800',
      background: '#FFF3E0',
      text: '#BF360C',
      accent: '#9C27B0'
    }
  }
])

function toggleAddDropdown() {
  showAddDropdown.value = !showAddDropdown.value
  showThemeDropdown.value = false
}

function toggleThemeDropdown() {
  showThemeDropdown.value = !showThemeDropdown.value
  showAddDropdown.value = false
}

function closeDropdowns() {
  showAddDropdown.value = false
  showThemeDropdown.value = false
}

// File operations
function newPresentation() {
  if (confirm('Create a new presentation? Unsaved changes will be lost.')) {
    presentationStore.newPresentation()
  }
}

function openPresentation() {
  // This would typically open a file picker or presentation browser
  console.log('Open presentation')
}

async function savePresentation() {
  try {
    const data = presentationStore.exportPresentation()
    const response = await fetch(`/api/presentations/${data.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    
    if (response.ok) {
      console.log('✅ Presentation saved')
    } else {
      console.error('❌ Failed to save presentation')
    }
  } catch (error) {
    console.error('Save error:', error)
  }
}

// Add elements
async function addText() {
  closeDropdowns()
  const slideIndex = presentationStore.canvas.activeSlide
  await presentationStore.addText(slideIndex, {
    content: 'Click to edit text',
    x: 100,
    y: 100,
    width: 300,
    height: 60,
    fontSize: 18,
    color: '#333333'
  })
}

async function addImage() {
  closeDropdowns()
  // This would typically open a file picker
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = async (e) => {
        const src = e.target?.result as string
        const slideIndex = presentationStore.canvas.activeSlide
        await presentationStore.addImage(slideIndex, {
          src,
          x: 100,
          y: 100,
          width: 300,
          height: 200
        })
      }
      reader.readAsDataURL(file)
    }
  }
  input.click()
}

async function addShape() {
  closeDropdowns()
  const slideIndex = presentationStore.canvas.activeSlide
  await presentationStore.addShape(slideIndex, {
    shape: 'rectangle',
    x: 100,
    y: 100,
    width: 150,
    height: 100,
    fill: '#1976D2',
    stroke: '#1565C0',
    strokeWidth: 2
  })
}

async function addChart() {
  closeDropdowns()
  const slideIndex = presentationStore.canvas.activeSlide
  await presentationStore.addChart(slideIndex, {
    chartType: 'bar',
    data: {
      labels: ['Q1', 'Q2', 'Q3', 'Q4'],
      datasets: [{
        label: 'Sales',
        data: [30, 45, 60, 80],
        backgroundColor: '#1976D2'
      }]
    },
    x: 100,
    y: 100,
    width: 400,
    height: 250
  })
}

async function addTable() {
  closeDropdowns()
  const slideIndex = presentationStore.canvas.activeSlide
  await presentationStore.addTable(slideIndex, {
    rows: 3,
    columns: 3,
    data: [
      ['Header 1', 'Header 2', 'Header 3'],
      ['Cell 1', 'Cell 2', 'Cell 3'],
      ['Cell 4', 'Cell 5', 'Cell 6']
    ],
    x: 100,
    y: 100,
    width: 400,
    height: 200
  })
}

// Slide operations
async function addSlide() {
  await presentationStore.createSlide()
}

async function deleteSlide() {
  if (confirm('Delete this slide?')) {
    await presentationStore.deleteSlide(presentationStore.canvas.activeSlide)
  }
}

async function duplicateSlide() {
  const currentSlide = presentationStore.currentSlide
  if (currentSlide) {
    await presentationStore.createSlide({
      layout: currentSlide.layout,
      elements: currentSlide.elements.map(el => ({ ...el }))
    })
  }
}

// Theme operations
async function applyTheme(theme: any) {
  closeDropdowns()
  await presentationStore.applyTheme(theme)
}

function getThemePreview(theme: any) {
  return {
    background: `linear-gradient(45deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
    width: '20px',
    height: '20px',
    borderRadius: '4px'
  }
}

// Click outside handler
function handleClickOutside(event: MouseEvent) {
  if (addDropdown.value && !addDropdown.value.contains(event.target as Node)) {
    showAddDropdown.value = false
  }
  if (themeDropdown.value && !themeDropdown.value.contains(event.target as Node)) {
    showThemeDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.toolbar-main {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  background: var(--surface);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 2px 8px var(--shadow);
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: var(--border);
  margin: 0 var(--spacing-xs);
}

.dropdown {
  position: relative;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: var(--spacing-xs);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 8px 32px var(--shadow-dark);
  padding: var(--spacing-xs);
  min-width: 150px;
  z-index: 1000;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  width: 100%;
  padding: var(--spacing-sm);
  border: none;
  background: none;
  text-align: left;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  font-size: var(--font-size-sm);
}

.dropdown-item:hover {
  background: var(--border-light);
}

.theme-item {
  justify-content: flex-start;
}

.theme-preview {
  flex-shrink: 0;
}

/* Responsive design */
@media (max-width: 768px) {
  .toolbar-main {
    gap: var(--spacing-xs);
    padding: var(--spacing-xs);
  }
  
  .toolbar-section {
    gap: 2px;
  }
  
  .btn-sm {
    padding: var(--spacing-xs);
    font-size: 12px;
  }
  
  .toolbar-divider {
    margin: 0 2px;
  }
}
</style>