<template>
  <!-- Use new AtomicRenderer for enhanced functionality -->
  <AtomicRenderer
    v-if="useNewRenderer"
    :component="convertToVisualComponent(element)"
    :selected="selected"
    :editing="isEditing"
    :zoom="zoom"
    @update="handleVisualUpdate"
    @select="handleSelect"
    @edit="handleEdit"
    @delete="handleDelete"
    @duplicate="handleDuplicate"
  />
  
  <!-- Fallback to legacy renderer -->
  <div
    v-else
    class="element-renderer"
    :class="{ 
      'selected': selected,
      'dragging': isDragging,
      [`element-${element.type}`]: true
    }"
    :style="elementStyle"
    @mousedown="handleMouseDown"
    @click="handleClick"
    @dblclick="handleDoubleClick"
  >
    <!-- Text Element -->
    <div
      v-if="element.type === 'text'"
      class="text-element"
      :style="textStyle"
      :contenteditable="isEditing"
      @blur="handleTextBlur"
      @input="handleTextInput"
      v-html="element.content"
    ></div>
    
    <!-- Image Element -->
    <img
      v-else-if="element.type === 'image'"
      class="image-element"
      :src="element.src"
      :style="imageStyle"
      @load="handleImageLoad"
      @error="handleImageError"
    />
    
    <!-- Shape Element -->
    <svg
      v-else-if="element.type === 'shape'"
      class="shape-element"
      :style="shapeStyle"
      :viewBox="shapeViewBox"
    >
      <path
        :d="shapePath"
        :fill="element.fill"
        :stroke="element.stroke"
        :stroke-width="element.strokeWidth"
      />
    </svg>
    
    <!-- Chart Element -->
    <div
      v-else-if="element.type === 'chart'"
      class="chart-element"
      :style="{ width: '100%', height: '100%' }"
    >
      <canvas
        ref="chartContainer"
        :width="element.width || 400"
        :height="element.height || 300"
        :style="{ 
          width: '100%', 
          height: '100%',
          display: 'block'
        }"
      ></canvas>
    </div>
    
    <!-- Table Element -->
    <table
      v-else-if="element.type === 'table'"
      class="table-element"
      :style="tableStyle"
    >
      <tr v-for="(row, rowIndex) in element.data" :key="rowIndex">
        <td
          v-for="(cell, colIndex) in row"
          :key="colIndex"
          :style="getCellStyle(rowIndex, colIndex)"
          @dblclick="editCell(rowIndex, colIndex)"
        >
          {{ cell }}
        </td>
      </tr>
    </table>
    
    <!-- Video Element -->
    <video
      v-else-if="element.type === 'video'"
      class="video-element"
      :src="element.src"
      :poster="element.poster"
      :autoplay="element.autoplay"
      :loop="element.loop"
      :controls="element.controls"
      :style="videoStyle"
    ></video>
    
    <!-- Audio Element -->
    <div
      v-else-if="element.type === 'audio'"
      class="audio-element"
      :style="audioStyle"
    >
      <div class="audio-icon" :style="{ color: element.iconColor }">🔊</div>
      <audio
        :src="element.src"
        :autoplay="element.autoplay"
        :loop="element.loop"
        controls
      ></audio>
    </div>
    
    <!-- Selection Handles -->
    <div v-if="selected && !isEditing" class="selection-handles">
      <div
        v-for="handle in selectionHandles"
        :key="handle.position"
        :class="`handle handle-${handle.position}`"
        :style="handle.style"
        @mousedown="handleResizeStart($event, handle.position)"
      ></div>
    </div>
    
    <!-- Rotation Handle -->
    <div
      v-if="selected && !isEditing"
      class="rotation-handle"
      @mousedown="handleRotationStart"
    >
      <div class="rotation-icon">↻</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import type { PPTElement } from '@/types/slides'
import { Chart, registerables } from 'chart.js'
import AtomicRenderer from '../Visual/Core/AtomicRenderer.vue'
import type { VisualComponent, TextComponent, ImageComponent, ShapeComponent, ChartComponent, TableComponent } from '../Visual/Types/ComponentTypes'
import { ElementType } from '@/types/atoms'

Chart.register(...registerables)

interface Props {
  element: PPTElement
  selected: boolean
  zoom: number
}

interface Emits {
  (e: 'select', elementId: string, multiSelect?: boolean): void
  (e: 'update', elementId: string, changes: any): void
  (e: 'delete', elementId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isDragging = ref(false)
const isResizing = ref(false)
const isRotating = ref(false)
const isEditing = ref(false)
const dragStart = ref({ x: 0, y: 0, elementX: 0, elementY: 0 })
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0, handle: '' })
const rotationStart = ref({ x: 0, y: 0, rotation: 0 })
const chartContainer = ref<HTMLElement>()
const chartInstance = ref<Chart | null>(null)

// New visual component system integration
const useNewRenderer = ref(true) // Toggle to enable new renderer
const visualComponent = ref<VisualComponent | null>(null)

// Convert legacy element to visual component
function convertToVisualComponent(element: PPTElement): VisualComponent {
  const baseComponent = {
    id: element.id,
    type: element.type as ElementType,
    x: element.left || 0,
    y: element.top || 0,
    width: element.width || 100,
    height: element.height || 100,
    rotation: element.rotation || 0,
    opacity: element.opacity || 1,
    zIndex: element.zIndex || 1,
    locked: false,
    visible: true,
    metadata: {
      createdAt: Date.now(),
      updatedAt: Date.now(),
      version: '1.0.0'
    }
  }

  switch (element.type) {
    case 'text':
      return {
        ...baseComponent,
        content: element.content || 'Text',
        style: {
          fontSize: element.fontSize || 16,
          fontFamily: element.fontFamily || 'Inter, sans-serif',
          fontWeight: element.bold ? 'bold' : 'normal',
          fontStyle: element.italic ? 'italic' : 'normal',
          color: element.color || '#000000',
          textAlign: element.align || 'left',
          verticalAlign: 'top',
          lineHeight: 1.4,
          textDecoration: element.underline ? 'underline' : 'none'
        },
        editable: true
      } as TextComponent

    case 'image':
      return {
        ...baseComponent,
        src: element.src || '',
        alt: element.alt || 'Image',
        style: {
          objectFit: 'cover',
          objectPosition: 'center',
          borderRadius: 0
        }
      } as ImageComponent

    case 'shape':
      return {
        ...baseComponent,
        shape: element.shape || 'rectangle',
        style: {
          fill: element.fill || '#3498db',
          stroke: element.stroke || '#2980b9',
          strokeWidth: element.strokeWidth || 2,
          cornerRadius: element.cornerRadius || 0
        }
      } as ShapeComponent

    case 'chart':
      return {
        ...baseComponent,
        chartType: element.chartType || 'bar',
        data: element.data || { labels: [], datasets: [] },
        options: element.options || {},
        style: {
          backgroundColor: '#ffffff',
          borderRadius: 8
        }
      } as ChartComponent

    case 'table':
      return {
        ...baseComponent,
        data: element.data || { headers: [], rows: [] },
        style: {
          variant: 'modern',
          headerStyle: {
            backgroundColor: '#f8f9fa',
            color: '#2c3e50',
            fontWeight: 'bold',
            textAlign: 'left',
            padding: { top: 12, right: 16, bottom: 12, left: 16 }
          },
          cellStyle: {
            backgroundColor: '#ffffff',
            color: '#2c3e50',
            textAlign: 'left',
            padding: { top: 8, right: 16, bottom: 8, left: 16 }
          },
          borderCollapse: 'collapse'
        }
      } as TableComponent

    default:
      return baseComponent as VisualComponent
  }
}

// Handle visual component updates
function handleVisualUpdate(component: VisualComponent, changes: Partial<VisualComponent>) {
  // Convert back to legacy format for compatibility
  const legacyChanges: any = {}
  
  if (changes.x !== undefined) legacyChanges.left = changes.x
  if (changes.y !== undefined) legacyChanges.top = changes.y
  if (changes.width !== undefined) legacyChanges.width = changes.width
  if (changes.height !== undefined) legacyChanges.height = changes.height
  if (changes.rotation !== undefined) legacyChanges.rotation = changes.rotation
  if (changes.opacity !== undefined) legacyChanges.opacity = changes.opacity
  if (changes.zIndex !== undefined) legacyChanges.zIndex = changes.zIndex
  
  // Handle type-specific changes
  if (component.type === ElementType.TEXT && 'content' in changes) {
    legacyChanges.content = (changes as any).content
  }
  
  emit('update', component.id, legacyChanges)
}

function handleSelect(component: VisualComponent) {
  emit('select', component.id)
}

function handleEdit(component: VisualComponent) {
  isEditing.value = true
}

function handleDelete(component: VisualComponent) {
  emit('delete', component.id)
}

function handleDuplicate(component: VisualComponent) {
  // Emit a duplicate event or handle duplication logic
  console.log('Duplicate component:', component.id)
}

// Computed styles
const elementStyle = computed(() => ({
  position: 'absolute',
  left: `${props.element.left}px`,
  top: `${props.element.top}px`,
  width: `${props.element.width}px`,
  height: `${props.element.height}px`,
  transform: `rotate(${props.element.rotate}deg)`,
  zIndex: props.element.zIndex || 1,
  opacity: props.element.opacity || 1,
  cursor: isDragging.value ? 'grabbing' : 'grab'
}))

const textStyle = computed(() => {
  if (props.element.type !== 'text') return {}
  const el = props.element as any
  return {
    fontFamily: el.fontFamily || el.defaultFontName,
    fontSize: `${el.fontSize || 16}px`,
    color: el.color || el.defaultColor,
    fontWeight: el.bold ? 'bold' : 'normal',
    fontStyle: el.italic ? 'italic' : 'normal',
    textDecoration: el.underline ? 'underline' : 'none',
    textAlign: el.align || 'left',
    lineHeight: el.lineHeight || 1.5,
    padding: '8px',
    outline: 'none',
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    backgroundColor: el.fill || 'transparent'
  }
})

const imageStyle = computed(() => {
  if (props.element.type !== 'image') return {}
  const el = props.element as any
  return {
    width: '100%',
    height: '100%',
    objectFit: el.fit || 'contain',
    borderRadius: el.borderRadius ? `${el.borderRadius}px` : '0',
    filter: el.filter || 'none',
    transform: `scaleX(${el.flipH ? -1 : 1}) scaleY(${el.flipV ? -1 : 1})`,
    boxShadow: el.shadow ? '0 4px 8px rgba(0,0,0,0.2)' : 'none'
  }
})

const shapeStyle = computed(() => ({
  width: '100%',
  height: '100%'
}))

const shapeViewBox = computed(() => {
  return `0 0 ${props.element.width} ${props.element.height}`
})

const shapePath = computed(() => {
  if (props.element.type !== 'shape') return ''
  const el = props.element as any
  
  switch (el.shape) {
    case 'rectangle':
      return `M 0 0 L ${props.element.width} 0 L ${props.element.width} ${props.element.height} L 0 ${props.element.height} Z`
    case 'circle':
      const cx = props.element.width / 2
      const cy = props.element.height / 2
      const r = Math.min(cx, cy)
      return `M ${cx} ${cy} m -${r} 0 a ${r} ${r} 0 1 0 ${r * 2} 0 a ${r} ${r} 0 1 0 -${r * 2} 0`
    case 'triangle':
      return `M ${props.element.width / 2} 0 L ${props.element.width} ${props.element.height} L 0 ${props.element.height} Z`
    default:
      return `M 0 0 L ${props.element.width} 0 L ${props.element.width} ${props.element.height} L 0 ${props.element.height} Z`
  }
})

const tableStyle = computed(() => {
  if (props.element.type !== 'table') return {}
  const el = props.element as any
  return {
    width: '100%',
    height: '100%',
    borderCollapse: 'collapse',
    border: `${el.style?.borderWidth || 1}px solid ${el.style?.borderColor || '#ddd'}`
  }
})

const videoStyle = computed(() => ({
  width: '100%',
  height: '100%',
  objectFit: 'contain'
}))

const audioStyle = computed(() => ({
  width: '100%',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '8px'
}))

const selectionHandles = computed(() => [
  { position: 'nw', style: { top: '-4px', left: '-4px' } },
  { position: 'n', style: { top: '-4px', left: '50%', transform: 'translateX(-50%)' } },
  { position: 'ne', style: { top: '-4px', right: '-4px' } },
  { position: 'e', style: { top: '50%', right: '-4px', transform: 'translateY(-50%)' } },
  { position: 'se', style: { bottom: '-4px', right: '-4px' } },
  { position: 's', style: { bottom: '-4px', left: '50%', transform: 'translateX(-50%)' } },
  { position: 'sw', style: { bottom: '-4px', left: '-4px' } },
  { position: 'w', style: { top: '50%', left: '-4px', transform: 'translateY(-50%)' } }
])

// Event handlers
function handleClick(event: MouseEvent) {
  event.stopPropagation()
  emit('select', props.element.id, event.ctrlKey || event.metaKey)
}

function handleDoubleClick(event: MouseEvent) {
  event.stopPropagation()
  if (props.element.type === 'text') {
    isEditing.value = true
    nextTick(() => {
      const textEl = event.target as HTMLElement
      textEl.focus()
    })
  }
}

function handleMouseDown(event: MouseEvent) {
  if (isEditing.value) return
  
  event.preventDefault()
  event.stopPropagation()
  
  isDragging.value = true
  dragStart.value = {
    x: event.clientX,
    y: event.clientY,
    elementX: props.element.left,
    elementY: props.element.top
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(event: MouseEvent) {
  if (!isDragging.value && !isResizing.value && !isRotating.value) return
  
  if (isDragging.value) {
    const deltaX = (event.clientX - dragStart.value.x) / props.zoom
    const deltaY = (event.clientY - dragStart.value.y) / props.zoom
    
    emit('update', props.element.id, {
      left: dragStart.value.elementX + deltaX,
      top: dragStart.value.elementY + deltaY
    })
  } else if (isResizing.value) {
    handleResize(event)
  } else if (isRotating.value) {
    handleRotation(event)
  }
}

function handleMouseUp() {
  isDragging.value = false
  isResizing.value = false
  isRotating.value = false
  
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

function handleResizeStart(event: MouseEvent, handle: string) {
  event.stopPropagation()
  
  isResizing.value = true
  resizeStart.value = {
    x: event.clientX,
    y: event.clientY,
    width: props.element.width,
    height: props.element.height,
    handle
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleResize(event: MouseEvent) {
  const deltaX = (event.clientX - resizeStart.value.x) / props.zoom
  const deltaY = (event.clientY - resizeStart.value.y) / props.zoom
  const handle = resizeStart.value.handle
  
  let newWidth = resizeStart.value.width
  let newHeight = resizeStart.value.height
  let newLeft = props.element.left
  let newTop = props.element.top
  
  // Handle different resize directions
  if (handle.includes('e')) newWidth += deltaX
  if (handle.includes('w')) {
    newWidth -= deltaX
    newLeft += deltaX
  }
  if (handle.includes('s')) newHeight += deltaY
  if (handle.includes('n')) {
    newHeight -= deltaY
    newTop += deltaY
  }
  
  // Minimum size constraints
  newWidth = Math.max(20, newWidth)
  newHeight = Math.max(20, newHeight)
  
  emit('update', props.element.id, {
    width: newWidth,
    height: newHeight,
    left: newLeft,
    top: newTop
  })
}

function handleRotationStart(event: MouseEvent) {
  event.stopPropagation()
  
  isRotating.value = true
  rotationStart.value = {
    x: event.clientX,
    y: event.clientY,
    rotation: props.element.rotate
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleRotation(event: MouseEvent) {
  const centerX = props.element.left + props.element.width / 2
  const centerY = props.element.top + props.element.height / 2
  
  const startAngle = Math.atan2(rotationStart.value.y - centerY, rotationStart.value.x - centerX)
  const currentAngle = Math.atan2(event.clientY - centerY, event.clientX - centerX)
  
  const deltaAngle = (currentAngle - startAngle) * (180 / Math.PI)
  const newRotation = rotationStart.value.rotation + deltaAngle
  
  emit('update', props.element.id, {
    rotate: newRotation % 360
  })
}

function handleTextBlur() {
  isEditing.value = false
}

function handleTextInput(event: Event) {
  const target = event.target as HTMLElement
  emit('update', props.element.id, {
    content: target.innerHTML
  })
}

function handleImageLoad() {
  // Image loaded successfully
}

function handleImageError() {
  console.error('Failed to load image:', props.element.id)
}

function getCellStyle(rowIndex: number, colIndex: number) {
  if (props.element.type !== 'table') return {}
  const el = props.element as any
  
  const isHeader = rowIndex === 0
  return {
    padding: `${el.style?.cellPadding || 8}px`,
    border: `1px solid ${el.style?.borderColor || '#ddd'}`,
    backgroundColor: isHeader ? (el.style?.headerBg || '#f5f5f5') : 'transparent',
    color: isHeader ? (el.style?.headerColor || '#333') : '#333',
    fontWeight: isHeader ? 'bold' : 'normal'
  }
}

function editCell(rowIndex: number, colIndex: number) {
  // This would implement inline cell editing
  console.log('Edit cell:', rowIndex, colIndex)
}

// Chart handling
function createChart() {
  if (props.element.type !== 'chart' || !chartContainer.value) return
  
  const el = props.element as any
  
  // Ensure we have a canvas element
  let canvas = chartContainer.value
  if (!(canvas instanceof HTMLCanvasElement)) {
    console.error('Chart container is not a canvas element')
    return
  }
  
  // Wait for canvas to be properly mounted
  if (!canvas.offsetParent && canvas.offsetWidth === 0 && canvas.offsetHeight === 0) {
    // Canvas not yet in DOM, retry after next tick
    nextTick(() => createChart())
    return
  }
  
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    console.error('Failed to get 2D context from canvas')
    return
  }
  
  // Destroy existing chart instance
  if (chartInstance.value) {
    try {
      chartInstance.value.destroy()
    } catch (e) {
      console.warn('Error destroying chart:', e)
    }
    chartInstance.value = null
  }
  
  // Ensure canvas has proper dimensions
  if (canvas.width === 0 || canvas.height === 0) {
    canvas.width = el.width || 400
    canvas.height = el.height || 300
  }
  
  try {
    chartInstance.value = new Chart(ctx, {
      type: el.chartType || 'bar',
      data: el.data || {
        labels: ['Sample'],
        datasets: [{
          label: 'Data',
          data: [1],
          backgroundColor: '#3498db'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 0 // Disable animations to prevent context issues
        },
        plugins: {
          legend: {
            display: true
          }
        },
        ...el.options
      }
    })
  } catch (error) {
    console.error('Failed to create chart:', error)
  }
}

// Watchers
watch(() => props.element, () => {
  if (props.element.type === 'chart') {
    nextTick(() => {
      createChart()
    })
  }
}, { deep: true })

// Lifecycle
onMounted(() => {
  if (props.element.type === 'chart') {
    nextTick(() => {
      createChart()
    })
  }
})

onUnmounted(() => {
  if (chartInstance.value) {
    try {
      chartInstance.value.destroy()
    } catch (e) {
      console.warn('Error destroying chart on unmount:', e)
    }
    chartInstance.value = null
  }
})
</script>

<style scoped>
.element-renderer {
  border: 2px solid transparent;
  transition: border-color 0.15s ease;
}

.element-renderer.selected {
  border-color: var(--primary);
}

.element-renderer.dragging {
  cursor: grabbing !important;
}

.text-element {
  cursor: text;
}

.text-element:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.image-element {
  display: block;
}

.shape-element {
  display: block;
}

.chart-element {
  width: 100%;
  height: 100%;
}

.table-element {
  font-size: 14px;
}

.video-element {
  display: block;
}

.audio-element .audio-icon {
  font-size: 24px;
}

.selection-handles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.handle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--primary);
  border: 1px solid white;
  border-radius: 50%;
  pointer-events: all;
  cursor: pointer;
}

.handle-nw, .handle-se { cursor: nw-resize; }
.handle-ne, .handle-sw { cursor: ne-resize; }
.handle-n, .handle-s { cursor: n-resize; }
.handle-e, .handle-w { cursor: e-resize; }

.rotation-handle {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 20px;
  background: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  color: white;
  font-size: 12px;
}

.rotation-handle:hover {
  background: var(--primary-dark);
}

.rotation-icon {
  pointer-events: none;
}
</style>