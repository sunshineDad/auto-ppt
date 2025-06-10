<template>
  <div class="canvas-editor" ref="canvasContainer">
    <!-- Canvas Background -->
    <div 
      class="canvas-background"
      :style="canvasStyle"
      @click="handleCanvasClick"
      @contextmenu="handleContextMenu"
    >
      <!-- Grid -->
      <div v-if="presentationStore.canvas.gridVisible" class="canvas-grid"></div>
      
      <!-- Slide Content -->
      <div 
        class="slide-content"
        :style="slideStyle"
      >
        <!-- Slide Background -->
        <div 
          class="slide-background"
          :style="slideBackgroundStyle"
        ></div>
        
        <!-- Elements -->
        <ElementRenderer
          v-for="element in currentSlideElements"
          :key="element.id"
          :element="element"
          :selected="isElementSelected(element.id)"
          :zoom="presentationStore.canvas.zoom"
          @select="selectElement"
          @update="updateElement"
          @delete="deleteElement"
        />
        
        <!-- Selection Box -->
        <SelectionBox
          v-if="selectionBox.visible"
          :box="selectionBox"
        />
      </div>
    </div>
    
    <!-- Context Menu -->
    <ContextMenu
      v-if="contextMenu.visible"
      :x="contextMenu.x"
      :y="contextMenu.y"
      :items="contextMenuItems"
      @select="handleContextMenuSelect"
      @close="closeContextMenu"
    />
    
    <!-- Element Toolbar -->
    <ElementToolbar
      v-if="selectedElements.length > 0"
      :elements="selectedElements"
      :position="toolbarPosition"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { usePresentationStore, useAIStore } from '@/stores'
import type { PPTElement } from '@/types/slides'
import ElementRenderer from './ElementRenderer.vue'
import SelectionBox from './SelectionBox.vue'
import ContextMenu from './ContextMenu.vue'
import ElementToolbar from './ElementToolbar.vue'

const presentationStore = usePresentationStore()
const aiStore = useAIStore()

const canvasContainer = ref<HTMLElement>()
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const selectionBox = ref({
  visible: false,
  x: 0,
  y: 0,
  width: 0,
  height: 0
})
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0
})

// Computed properties
const currentSlideElements = computed(() => {
  return presentationStore.currentSlide?.elements || []
})

const selectedElements = computed(() => {
  return currentSlideElements.value.filter(el => 
    presentationStore.selectedElements.includes(el.id)
  )
})

const canvasStyle = computed(() => ({
  transform: `scale(${presentationStore.canvas.zoom})`,
  transformOrigin: 'center center'
}))

const slideStyle = computed(() => {
  const settings = presentationStore.presentation.settings
  return {
    width: `${settings.width}px`,
    height: `${settings.height}px`,
    transform: `translate(${presentationStore.canvas.offsetX}px, ${presentationStore.canvas.offsetY}px)`
  }
})

const slideBackgroundStyle = computed(() => {
  const bg = presentationStore.currentSlide?.background
  if (!bg) return { backgroundColor: '#ffffff' }
  
  switch (bg.type) {
    case 'solid':
      return { backgroundColor: bg.color }
    case 'gradient':
      if (bg.gradient?.type === 'linear') {
        const colors = bg.gradient.colors.map(c => `${c.color} ${c.pos}%`).join(', ')
        return {
          background: `linear-gradient(${bg.gradient.rotate || 0}deg, ${colors})`
        }
      }
      break
    case 'image':
      return {
        backgroundImage: `url(${bg.image?.src})`,
        backgroundSize: bg.image?.size || 'cover',
        backgroundPosition: bg.image?.position || 'center'
      }
  }
  return { backgroundColor: '#ffffff' }
})

const contextMenuItems = computed(() => [
  { label: 'Add Text', action: 'add-text', icon: '📝' },
  { label: 'Add Image', action: 'add-image', icon: '🖼️' },
  { label: 'Add Shape', action: 'add-shape', icon: '🔷' },
  { label: 'Add Chart', action: 'add-chart', icon: '📊' },
  { label: 'Add Table', action: 'add-table', icon: '📋' },
  { type: 'separator' },
  { label: 'Paste', action: 'paste', icon: '📋', disabled: presentationStore.clipboard.length === 0 },
  { type: 'separator' },
  { label: 'AI Suggestions', action: 'ai-suggestions', icon: '🤖' }
])

const toolbarPosition = computed(() => {
  if (selectedElements.value.length === 0) return { x: 0, y: 0 }
  
  const bounds = getElementsBounds(selectedElements.value)
  return {
    x: bounds.x + bounds.width / 2,
    y: bounds.y - 50
  }
})

// Event handlers
function handleCanvasClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    presentationStore.clearSelection()
    closeContextMenu()
  }
}

function handleContextMenu(event: MouseEvent) {
  event.preventDefault()
  
  const rect = canvasContainer.value!.getBoundingClientRect()
  contextMenu.value = {
    visible: true,
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
}

function closeContextMenu() {
  contextMenu.value.visible = false
}

async function handleContextMenuSelect(action: string) {
  closeContextMenu()
  
  const rect = canvasContainer.value!.getBoundingClientRect()
  const canvasRect = canvasContainer.value!.querySelector('.slide-content')!.getBoundingClientRect()
  
  // Calculate position relative to slide
  const x = (contextMenu.value.x - (canvasRect.left - rect.left)) / presentationStore.canvas.zoom
  const y = (contextMenu.value.y - (canvasRect.top - rect.top)) / presentationStore.canvas.zoom
  
  switch (action) {
    case 'add-text':
      await addTextElement(x, y)
      break
    case 'add-image':
      await addImageElement(x, y)
      break
    case 'add-shape':
      await addShapeElement(x, y)
      break
    case 'add-chart':
      await addChartElement(x, y)
      break
    case 'add-table':
      await addTableElement(x, y)
      break
    case 'paste':
      await presentationStore.pasteElements()
      break
    case 'ai-suggestions':
      await aiStore.generateSuggestions(presentationStore.canvas.activeSlide)
      break
  }
}

function selectElement(elementId: string, multiSelect = false) {
  if (multiSelect) {
    presentationStore.toggleElementSelection(elementId)
  } else {
    presentationStore.selectElements([elementId])
  }
}

function isElementSelected(elementId: string): boolean {
  return presentationStore.selectedElements.includes(elementId)
}

async function updateElement(elementId: string, changes: any) {
  await presentationStore.modifyElement(elementId, changes)
}

async function deleteElement(elementId: string) {
  await presentationStore.removeElement(elementId)
  presentationStore.clearSelection()
}

// Element creation helpers
async function addTextElement(x: number, y: number) {
  await presentationStore.addText(presentationStore.canvas.activeSlide, {
    content: 'Click to edit text',
    x: x - 100,
    y: y - 25,
    width: 200,
    height: 50,
    fontSize: 16,
    color: '#333333'
  })
}

async function addImageElement(x: number, y: number) {
  // This would typically open a file picker
  const src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iI2Y1ZjVmNSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiPkltYWdlIFBsYWNlaG9sZGVyPC90ZXh0Pjwvc3ZnPg=='
  
  await presentationStore.addImage(presentationStore.canvas.activeSlide, {
    src,
    x: x - 100,
    y: y - 75,
    width: 200,
    height: 150
  })
}

async function addShapeElement(x: number, y: number) {
  await presentationStore.addShape(presentationStore.canvas.activeSlide, {
    shape: 'rectangle',
    x: x - 50,
    y: y - 25,
    width: 100,
    height: 50,
    fill: '#1976D2',
    stroke: '#1565C0',
    strokeWidth: 2
  })
}

async function addChartElement(x: number, y: number) {
  await presentationStore.addChart(presentationStore.canvas.activeSlide, {
    chartType: 'bar',
    data: {
      labels: ['Q1', 'Q2', 'Q3', 'Q4'],
      datasets: [{
        label: 'Revenue',
        data: [30, 45, 60, 80],
        backgroundColor: '#1976D2'
      }]
    },
    x: x - 150,
    y: y - 100,
    width: 300,
    height: 200
  })
}

async function addTableElement(x: number, y: number) {
  await presentationStore.addTable(presentationStore.canvas.activeSlide, {
    rows: 3,
    columns: 3,
    data: [
      ['Header 1', 'Header 2', 'Header 3'],
      ['Row 1 Col 1', 'Row 1 Col 2', 'Row 1 Col 3'],
      ['Row 2 Col 1', 'Row 2 Col 2', 'Row 2 Col 3']
    ],
    x: x - 150,
    y: y - 75,
    width: 300,
    height: 150
  })
}

// Utility functions
function getElementsBounds(elements: PPTElement[]) {
  if (elements.length === 0) return { x: 0, y: 0, width: 0, height: 0 }
  
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  
  for (const element of elements) {
    minX = Math.min(minX, element.left)
    minY = Math.min(minY, element.top)
    maxX = Math.max(maxX, element.left + element.width)
    maxY = Math.max(maxY, element.top + element.height)
  }
  
  return {
    x: minX,
    y: minY,
    width: maxX - minX,
    height: maxY - minY
  }
}

// Keyboard shortcuts
function handleKeydown(event: KeyboardEvent) {
  if (event.target !== document.body) return
  
  switch (event.key) {
    case 'Delete':
    case 'Backspace':
      if (presentationStore.selectedElements.length > 0) {
        event.preventDefault()
        presentationStore.selectedElements.forEach(id => {
          deleteElement(id)
        })
      }
      break
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  
  // Initialize canvas position
  nextTick(() => {
    centerCanvas()
  })
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

function centerCanvas() {
  if (!canvasContainer.value) return
  
  const container = canvasContainer.value
  const containerRect = container.getBoundingClientRect()
  const settings = presentationStore.presentation.settings
  
  const offsetX = (containerRect.width - settings.width * presentationStore.canvas.zoom) / 2
  const offsetY = (containerRect.height - settings.height * presentationStore.canvas.zoom) / 2
  
  presentationStore.setCanvasOffset(offsetX, offsetY)
}
</script>

<style scoped>
.canvas-editor {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  background: 
    radial-gradient(circle at 20px 20px, #e0e0e0 1px, transparent 1px),
    radial-gradient(circle at 60px 60px, #e0e0e0 1px, transparent 1px);
  background-size: 40px 40px;
  background-position: 0 0, 20px 20px;
}

.canvas-background {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: default;
  position: relative;
}

.canvas-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(to right, rgba(0,0,0,0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0,0,0,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.slide-content {
  position: relative;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  overflow: hidden;
  background: white;
}

.slide-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

/* Responsive design */
@media (max-width: 768px) {
  .canvas-editor {
    background-size: 20px 20px;
    background-position: 0 0, 10px 10px;
  }
}
</style>