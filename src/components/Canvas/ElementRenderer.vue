<template>
  <div
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
      ref="chartContainer"
    ></div>
    
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
  const ctx = chartContainer.value.getContext('2d')
  
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
  
  chartInstance.value = new Chart(ctx, {
    type: el.chartType,
    data: el.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      ...el.options
    }
  })
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
    chartInstance.value.destroy()
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