<template>
  <div class="drag-drop-manager">
    <!-- Drag Preview -->
    <div
      v-if="dragState.isDragging"
      ref="dragPreview"
      class="drag-preview"
      :style="dragPreviewStyle"
    >
      <component
        :is="getDragPreviewComponent()"
        :component="dragState.dragData"
        :preview="true"
      />
    </div>
    
    <!-- Drop Zones -->
    <div
      v-for="zone in dropZones"
      :key="zone.id"
      :class="['drop-zone', { 'active': zone.active, 'valid': zone.valid }]"
      :style="zone.style"
      @dragover.prevent="handleDragOver(zone, $event)"
      @dragenter.prevent="handleDragEnter(zone, $event)"
      @dragleave="handleDragLeave(zone, $event)"
      @drop.prevent="handleDrop(zone, $event)"
    >
      <div class="drop-zone-indicator">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>{{ zone.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import type { VisualComponent } from '../Types/ComponentTypes'
import { AtomicOperation } from '@/types/atoms'

// Import visual components for preview
import VisualText from '../Text/VisualText.vue'
import VisualImage from '../Images/VisualImage.vue'
import VisualShape from '../Shapes/VisualShape.vue'
import VisualChart from '../Charts/VisualChart.vue'
import VisualTable from '../Tables/VisualTable.vue'
import VisualIcon from '../Icons/VisualIcon.vue'

interface DropZone {
  id: string
  label: string
  type: 'slide' | 'canvas' | 'component' | 'trash'
  position: { x: number; y: number; width: number; height: number }
  style: Record<string, any>
  active: boolean
  valid: boolean
  accepts: string[]
}

interface DragState {
  isDragging: boolean
  dragType: 'component' | 'slide' | 'element'
  dragData: any
  startPosition: { x: number; y: number }
  currentPosition: { x: number; y: number }
  offset: { x: number; y: number }
  sourceZone?: string
  validDropZones: string[]
}

interface Emits {
  (e: 'drag-start', data: { type: string; data: any; position: { x: number; y: number } }): void
  (e: 'drag-move', data: { position: { x: number; y: number }; validZones: string[] }): void
  (e: 'drag-end', data: { success: boolean; dropZone?: DropZone; position: { x: number; y: number } }): void
  (e: 'drop', data: { zone: DropZone; dragData: any; position: { x: number; y: number } }): void
  (e: 'component-reorder', data: { componentId: string; newIndex: number }): void
  (e: 'slide-reorder', data: { slideId: string; newIndex: number }): void
}

const emit = defineEmits<Emits>()

// Reactive state
const dragPreview = ref<HTMLElement>()
const dropZones = ref<DropZone[]>([])
const dragState = reactive<DragState>({
  isDragging: false,
  dragType: 'component',
  dragData: null,
  startPosition: { x: 0, y: 0 },
  currentPosition: { x: 0, y: 0 },
  offset: { x: 0, y: 0 },
  validDropZones: []
})

// Computed styles
const dragPreviewStyle = computed(() => ({
  position: 'fixed',
  left: `${dragState.currentPosition.x - dragState.offset.x}px`,
  top: `${dragState.currentPosition.y - dragState.offset.y}px`,
  width: '200px',
  height: '150px',
  pointerEvents: 'none',
  zIndex: 10000,
  opacity: 0.8,
  transform: 'rotate(5deg)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
  borderRadius: '8px',
  overflow: 'hidden',
  background: 'white'
}))

// Drag and Drop API
function startDrag(type: string, data: any, event: MouseEvent | DragEvent) {
  dragState.isDragging = true
  dragState.dragType = type as any
  dragState.dragData = data
  dragState.startPosition = { x: event.clientX, y: event.clientY }
  dragState.currentPosition = { x: event.clientX, y: event.clientY }
  dragState.offset = { x: 50, y: 25 } // Center the preview
  
  // Calculate valid drop zones
  updateValidDropZones()
  
  emit('drag-start', {
    type,
    data,
    position: dragState.startPosition
  })
  
  // Add global mouse move and up listeners
  document.addEventListener('mousemove', handleGlobalMouseMove)
  document.addEventListener('mouseup', handleGlobalMouseUp)
  document.addEventListener('dragover', handleGlobalDragOver)
  document.addEventListener('drop', handleGlobalDrop)
}

function updateDrag(event: MouseEvent | DragEvent) {
  if (!dragState.isDragging) return
  
  dragState.currentPosition = { x: event.clientX, y: event.clientY }
  
  // Update drop zone states
  updateDropZoneStates(event)
  
  emit('drag-move', {
    position: dragState.currentPosition,
    validZones: dragState.validDropZones
  })
}

function endDrag(success: boolean, dropZone?: DropZone) {
  const endData = {
    success,
    dropZone,
    position: dragState.currentPosition
  }
  
  emit('drag-end', endData)
  
  // Reset state
  dragState.isDragging = false
  dragState.dragData = null
  dragState.validDropZones = []
  
  // Reset drop zones
  dropZones.value.forEach(zone => {
    zone.active = false
    zone.valid = false
  })
  
  // Remove global listeners
  document.removeEventListener('mousemove', handleGlobalMouseMove)
  document.removeEventListener('mouseup', handleGlobalMouseUp)
  document.removeEventListener('dragover', handleGlobalDragOver)
  document.removeEventListener('drop', handleGlobalDrop)
}

// Drop Zone Management
function registerDropZone(zone: Omit<DropZone, 'active' | 'valid'>) {
  const newZone: DropZone = {
    ...zone,
    active: false,
    valid: false
  }
  
  dropZones.value.push(newZone)
  return newZone.id
}

function unregisterDropZone(zoneId: string) {
  const index = dropZones.value.findIndex(zone => zone.id === zoneId)
  if (index !== -1) {
    dropZones.value.splice(index, 1)
  }
}

function updateDropZone(zoneId: string, updates: Partial<DropZone>) {
  const zone = dropZones.value.find(z => z.id === zoneId)
  if (zone) {
    Object.assign(zone, updates)
  }
}

// Event Handlers
function handleGlobalMouseMove(event: MouseEvent) {
  updateDrag(event)
}

function handleGlobalMouseUp(event: MouseEvent) {
  endDrag(false)
}

function handleGlobalDragOver(event: DragEvent) {
  event.preventDefault()
  updateDrag(event)
}

function handleGlobalDrop(event: DragEvent) {
  event.preventDefault()
  endDrag(false)
}

function handleDragOver(zone: DropZone, event: DragEvent) {
  event.preventDefault()
  
  if (isValidDropZone(zone)) {
    zone.active = true
    zone.valid = true
  }
}

function handleDragEnter(zone: DropZone, event: DragEvent) {
  event.preventDefault()
  
  if (isValidDropZone(zone)) {
    zone.active = true
    zone.valid = true
  }
}

function handleDragLeave(zone: DropZone, event: DragEvent) {
  // Check if we're actually leaving the zone
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const x = event.clientX
  const y = event.clientY
  
  if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
    zone.active = false
    zone.valid = false
  }
}

function handleDrop(zone: DropZone, event: DragEvent) {
  event.preventDefault()
  
  if (isValidDropZone(zone)) {
    const dropPosition = {
      x: event.clientX - zone.position.x,
      y: event.clientY - zone.position.y
    }
    
    emit('drop', {
      zone,
      dragData: dragState.dragData,
      position: dropPosition
    })
    
    endDrag(true, zone)
  }
}

// Helper Functions
function updateValidDropZones() {
  dragState.validDropZones = dropZones.value
    .filter(zone => isValidDropZone(zone))
    .map(zone => zone.id)
}

function updateDropZoneStates(event: MouseEvent | DragEvent) {
  dropZones.value.forEach(zone => {
    const isOver = isPointInZone(
      { x: event.clientX, y: event.clientY },
      zone.position
    )
    
    zone.active = isOver && isValidDropZone(zone)
    zone.valid = isValidDropZone(zone)
  })
}

function isValidDropZone(zone: DropZone): boolean {
  if (!dragState.isDragging) return false
  
  // Check if the zone accepts this drag type
  return zone.accepts.includes(dragState.dragType) || zone.accepts.includes('*')
}

function isPointInZone(point: { x: number; y: number }, zonePos: DropZone['position']): boolean {
  return (
    point.x >= zonePos.x &&
    point.x <= zonePos.x + zonePos.width &&
    point.y >= zonePos.y &&
    point.y <= zonePos.y + zonePos.height
  )
}

function getDragPreviewComponent() {
  if (!dragState.dragData) return null
  
  switch (dragState.dragData.type) {
    case 'text': return VisualText
    case 'image': return VisualImage
    case 'shape': return VisualShape
    case 'chart': return VisualChart
    case 'table': return VisualTable
    case 'icon': return VisualIcon
    default: return null
  }
}

// Slide Reordering
function handleSlideReorder(slideId: string, newIndex: number) {
  emit('slide-reorder', { slideId, newIndex })
}

// Component Reordering
function handleComponentReorder(componentId: string, newIndex: number) {
  emit('component-reorder', { componentId, newIndex })
}

// Expose public API
defineExpose({
  startDrag,
  endDrag,
  registerDropZone,
  unregisterDropZone,
  updateDropZone,
  isDragging: computed(() => dragState.isDragging),
  dragData: computed(() => dragState.dragData)
})

// Lifecycle
onMounted(() => {
  // Set up default drop zones
  registerDropZone({
    id: 'canvas',
    label: 'Drop here to add to slide',
    type: 'canvas',
    position: { x: 0, y: 0, width: window.innerWidth, height: window.innerHeight },
    style: {},
    accepts: ['component', 'element']
  })
  
  registerDropZone({
    id: 'trash',
    label: 'Drop here to delete',
    type: 'trash',
    position: { x: window.innerWidth - 100, y: window.innerHeight - 100, width: 80, height: 80 },
    style: {
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      width: '80px',
      height: '80px',
      backgroundColor: '#e74c3c',
      borderRadius: '50%',
      display: 'none'
    },
    accepts: ['component', 'element', 'slide']
  })
})

onUnmounted(() => {
  // Clean up listeners
  document.removeEventListener('mousemove', handleGlobalMouseMove)
  document.removeEventListener('mouseup', handleGlobalMouseUp)
  document.removeEventListener('dragover', handleGlobalDragOver)
  document.removeEventListener('drop', handleGlobalDrop)
})
</script>

<style scoped>
.drag-drop-manager {
  position: relative;
  width: 100%;
  height: 100%;
}

.drag-preview {
  border: 2px dashed var(--primary, #3498db);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
}

.drop-zone {
  position: absolute;
  border: 2px dashed transparent;
  border-radius: 8px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
}

.drop-zone.active {
  opacity: 1;
  pointer-events: all;
}

.drop-zone.valid {
  border-color: var(--success, #27ae60);
  background-color: rgba(39, 174, 96, 0.1);
}

.drop-zone.active.valid {
  border-color: var(--primary, #3498db);
  background-color: rgba(52, 152, 219, 0.1);
  transform: scale(1.02);
}

.drop-zone-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--primary, #3498db);
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.drop-zone-indicator svg {
  opacity: 0.7;
}

/* Trash drop zone specific styles */
.drop-zone[data-type="trash"] {
  background-color: #e74c3c;
  border-color: #c0392b;
  border-radius: 50%;
}

.drop-zone[data-type="trash"] .drop-zone-indicator {
  background-color: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 100%;
  height: 100%;
}

.drop-zone[data-type="trash"].active {
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(231, 76, 60, 0.4);
}

/* Animation for drag states */
@keyframes pulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.drop-zone.active {
  animation: pulse 1.5s ease-in-out infinite;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .drop-zone-indicator {
    font-size: 12px;
    padding: 12px;
  }
  
  .drop-zone-indicator svg {
    width: 20px;
    height: 20px;
  }
}
</style>