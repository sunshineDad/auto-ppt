<template>
  <div
    class="atomic-renderer"
    :class="rendererClasses"
    :style="rendererStyle"
    @mousedown="handleMouseDown"
    @click="handleClick"
    @dblclick="handleDoubleClick"
  >
    <!-- Text Component -->
    <VisualText
      v-if="component.type === 'text'"
      :component="component as TextComponent"
      :selected="selected"
      :editing="editing"
      @update="handleUpdate"
      @edit="handleEdit"
    />

    <!-- Image Component -->
    <VisualImage
      v-else-if="component.type === 'image'"
      :component="component as ImageComponent"
      :selected="selected"
      @update="handleUpdate"
    />

    <!-- Shape Component -->
    <VisualShape
      v-else-if="component.type === 'shape'"
      :component="component as ShapeComponent"
      :selected="selected"
      @update="handleUpdate"
    />

    <!-- Chart Component -->
    <VisualChart
      v-else-if="component.type === 'chart'"
      :component="component as ChartComponent"
      :selected="selected"
      @update="handleUpdate"
    />

    <!-- Table Component -->
    <VisualTable
      v-else-if="component.type === 'table'"
      :component="component as TableComponent"
      :selected="selected"
      :editing="editing"
      @update="handleUpdate"
      @edit="handleEdit"
    />

    <!-- Icon Component -->
    <VisualIcon
      v-else-if="component.type === 'icon'"
      :component="component as IconComponent"
      :selected="selected"
      @update="handleUpdate"
    />

    <!-- Selection Handles -->
    <div
      v-if="selected && !editing"
      class="selection-handles"
    >
      <div
        v-for="handle in selectionHandles"
        :key="handle.position"
        :class="['selection-handle', `handle-${handle.position}`]"
        :style="handle.style"
        @mousedown.stop="handleResizeStart($event, handle.position)"
      ></div>
      
      <!-- Rotation Handle -->
      <div
        class="rotation-handle"
        :style="rotationHandleStyle"
        @mousedown.stop="handleRotationStart"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/>
          <path d="M21 3v5h-5"/>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import type { 
  VisualComponent, 
  TextComponent, 
  ImageComponent, 
  ShapeComponent, 
  ChartComponent, 
  TableComponent, 
  IconComponent,
  ComponentState
} from '../Types/ComponentTypes'

// Import visual components (these will be created next)
import VisualText from '../Text/VisualText.vue'
import VisualImage from '../Images/VisualImage.vue'
import VisualShape from '../Shapes/VisualShape.vue'
import VisualChart from '../Charts/VisualChart.vue'
import VisualTable from '../Tables/VisualTable.vue'
import VisualIcon from '../Icons/VisualIcon.vue'

interface Props {
  component: VisualComponent
  selected?: boolean
  editing?: boolean
  zoom?: number
}

interface Emits {
  (e: 'update', component: VisualComponent, changes: Partial<VisualComponent>): void
  (e: 'select', component: VisualComponent): void
  (e: 'deselect', component: VisualComponent): void
  (e: 'edit', component: VisualComponent): void
  (e: 'delete', component: VisualComponent): void
  (e: 'duplicate', component: VisualComponent): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  editing: false,
  zoom: 1
})

const emit = defineEmits<Emits>()

// Component state
const isDragging = ref(false)
const isResizing = ref(false)
const isRotating = ref(false)
const dragStart = ref({ x: 0, y: 0, componentX: 0, componentY: 0 })
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0, handle: '' })
const rotationStart = ref({ x: 0, y: 0, rotation: 0 })

// Computed styles
const rendererClasses = computed(() => ({
  'atomic-renderer': true,
  'selected': props.selected,
  'editing': props.editing,
  'dragging': isDragging.value,
  'resizing': isResizing.value,
  'rotating': isRotating.value,
  [`component-${props.component.type}`]: true
}))

const rendererStyle = computed(() => ({
  position: 'absolute',
  left: `${props.component.x}px`,
  top: `${props.component.y}px`,
  width: `${props.component.width}px`,
  height: `${props.component.height}px`,
  transform: `rotate(${props.component.rotation || 0}deg)`,
  opacity: props.component.opacity || 1,
  zIndex: props.component.zIndex || 1,
  cursor: isDragging.value ? 'grabbing' : (props.selected ? 'grab' : 'pointer'),
  visibility: props.component.visible !== false ? 'visible' : 'hidden'
}))

// Selection handles
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

const rotationHandleStyle = computed(() => ({
  position: 'absolute',
  top: '-24px',
  left: '50%',
  transform: 'translateX(-50%)',
  width: '16px',
  height: '16px',
  cursor: 'grab'
}))

// Event handlers
function handleMouseDown(event: MouseEvent) {
  if (props.editing) return
  
  event.preventDefault()
  event.stopPropagation()
  
  if (!props.selected) {
    emit('select', props.component)
  }
  
  isDragging.value = true
  dragStart.value = {
    x: event.clientX,
    y: event.clientY,
    componentX: props.component.x,
    componentY: props.component.y
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(event: MouseEvent) {
  if (isDragging.value) {
    const deltaX = (event.clientX - dragStart.value.x) / props.zoom
    const deltaY = (event.clientY - dragStart.value.y) / props.zoom
    
    const newX = dragStart.value.componentX + deltaX
    const newY = dragStart.value.componentY + deltaY
    
    emit('update', props.component, { x: newX, y: newY })
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

function handleClick(event: MouseEvent) {
  event.stopPropagation()
  if (!props.selected) {
    emit('select', props.component)
  }
}

function handleDoubleClick(event: MouseEvent) {
  event.stopPropagation()
  if (props.component.type === 'text' || props.component.type === 'table') {
    emit('edit', props.component)
  }
}

function handleResizeStart(event: MouseEvent, handle: string) {
  event.stopPropagation()
  
  isResizing.value = true
  resizeStart.value = {
    x: event.clientX,
    y: event.clientY,
    width: props.component.width,
    height: props.component.height,
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
  let newX = props.component.x
  let newY = props.component.y
  
  // Handle different resize directions
  if (handle.includes('e')) newWidth += deltaX
  if (handle.includes('w')) {
    newWidth -= deltaX
    newX += deltaX
  }
  if (handle.includes('s')) newHeight += deltaY
  if (handle.includes('n')) {
    newHeight -= deltaY
    newY += deltaY
  }
  
  // Minimum size constraints
  newWidth = Math.max(20, newWidth)
  newHeight = Math.max(20, newHeight)
  
  emit('update', props.component, {
    x: newX,
    y: newY,
    width: newWidth,
    height: newHeight
  })
}

function handleRotationStart(event: MouseEvent) {
  event.stopPropagation()
  
  isRotating.value = true
  rotationStart.value = {
    x: event.clientX,
    y: event.clientY,
    rotation: props.component.rotation || 0
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleRotation(event: MouseEvent) {
  const centerX = props.component.x + props.component.width / 2
  const centerY = props.component.y + props.component.height / 2
  
  const startAngle = Math.atan2(rotationStart.value.y - centerY, rotationStart.value.x - centerX)
  const currentAngle = Math.atan2(event.clientY - centerY, event.clientX - centerX)
  
  const deltaAngle = (currentAngle - startAngle) * (180 / Math.PI)
  const newRotation = (rotationStart.value.rotation + deltaAngle) % 360
  
  emit('update', props.component, { rotation: newRotation })
}

function handleUpdate(component: VisualComponent, changes: Partial<VisualComponent>) {
  emit('update', component, changes)
}

function handleEdit(component: VisualComponent) {
  emit('edit', component)
}
</script>

<style scoped>
.atomic-renderer {
  position: absolute;
  user-select: none;
  transition: box-shadow 0.2s ease;
}

.atomic-renderer.selected {
  box-shadow: 0 0 0 2px var(--primary, #3498db);
}

.atomic-renderer.editing {
  box-shadow: 0 0 0 2px var(--success, #27ae60);
}

.atomic-renderer.dragging {
  cursor: grabbing !important;
  z-index: 1000;
}

.selection-handles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.selection-handle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--primary, #3498db);
  border: 2px solid white;
  border-radius: 50%;
  pointer-events: all;
  cursor: pointer;
}

.selection-handle.handle-nw,
.selection-handle.handle-se {
  cursor: nw-resize;
}

.selection-handle.handle-ne,
.selection-handle.handle-sw {
  cursor: ne-resize;
}

.selection-handle.handle-n,
.selection-handle.handle-s {
  cursor: n-resize;
}

.selection-handle.handle-e,
.selection-handle.handle-w {
  cursor: e-resize;
}

.rotation-handle {
  background: var(--primary, #3498db);
  border: 2px solid white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: grab;
}

.rotation-handle:active {
  cursor: grabbing;
}
</style>