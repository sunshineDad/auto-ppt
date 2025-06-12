<template>
  <div class="visual-image" :class="imageClasses">
    <img
      ref="imageElement"
      :src="component.src"
      :alt="component.alt"
      :style="imageStyle"
      @load="handleLoad"
      @error="handleError"
      @dragstart.prevent
    />
    
    <!-- Loading state -->
    <div v-if="loading" class="image-loading">
      <div class="loading-spinner"></div>
      <span>Loading...</span>
    </div>
    
    <!-- Error state -->
    <div v-if="error" class="image-error">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
        <circle cx="8.5" cy="8.5" r="1.5"/>
        <polyline points="21,15 16,10 5,21"/>
      </svg>
      <span>Failed to load image</span>
    </div>
    
    <!-- Overlay for effects -->
    <div
      v-if="component.style.overlay"
      class="image-overlay"
      :style="overlayStyle"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ImageComponent } from '../Types/ComponentTypes'

interface Props {
  component: ImageComponent
  selected?: boolean
}

interface Emits {
  (e: 'update', component: ImageComponent, changes: Partial<ImageComponent>): void
  (e: 'load', component: ImageComponent): void
  (e: 'error', component: ImageComponent, error: Event): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false
})

const emit = defineEmits<Emits>()

const imageElement = ref<HTMLImageElement>()
const loading = ref(true)
const error = ref(false)

// Computed classes
const imageClasses = computed(() => ({
  'visual-image': true,
  'selected': props.selected,
  'loading': loading.value,
  'error': error.value
}))

// Computed styles
const imageStyle = computed(() => {
  const style = props.component.style
  return {
    width: '100%',
    height: '100%',
    objectFit: style.objectFit,
    objectPosition: style.objectPosition,
    borderRadius: style.borderRadius ? `${style.borderRadius}px` : '0',
    filter: buildFilterString(style),
    boxShadow: style.shadow ? buildShadowString(style.shadow) : 'none',
    border: style.border ? 
      `${style.border.width}px ${style.border.style} ${style.border.color}` : 
      'none',
    transition: 'all 0.3s ease',
    display: loading.value || error.value ? 'none' : 'block'
  }
})

const overlayStyle = computed(() => {
  const overlay = props.component.style.overlay
  if (!overlay) return {}
  
  return {
    backgroundColor: overlay.color,
    opacity: overlay.opacity,
    mixBlendMode: overlay.blendMode || 'normal'
  }
})

// Helper functions
function buildFilterString(style: ImageComponent['style']) {
  const filters = []
  
  if (style.brightness !== undefined && style.brightness !== 100) {
    filters.push(`brightness(${style.brightness}%)`)
  }
  if (style.contrast !== undefined && style.contrast !== 100) {
    filters.push(`contrast(${style.contrast}%)`)
  }
  if (style.saturation !== undefined && style.saturation !== 100) {
    filters.push(`saturate(${style.saturation}%)`)
  }
  if (style.blur !== undefined && style.blur > 0) {
    filters.push(`blur(${style.blur}px)`)
  }
  if (style.filter) {
    filters.push(style.filter)
  }
  
  return filters.length > 0 ? filters.join(' ') : 'none'
}

function buildShadowString(shadow: NonNullable<ImageComponent['style']['shadow']>) {
  return `${shadow.offsetX}px ${shadow.offsetY}px ${shadow.blurRadius}px ${shadow.spreadRadius || 0}px ${shadow.color}${shadow.inset ? ' inset' : ''}`
}

// Event handlers
function handleLoad() {
  loading.value = false
  error.value = false
  emit('load', props.component)
}

function handleError(event: Event) {
  loading.value = false
  error.value = true
  emit('error', props.component, event)
}

// Watch for src changes
watch(() => props.component.src, () => {
  loading.value = true
  error.value = false
})

// Expose methods
defineExpose({
  reload() {
    if (imageElement.value) {
      loading.value = true
      error.value = false
      imageElement.value.src = props.component.src
    }
  }
})
</script>

<style scoped>
.visual-image {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
}

.visual-image.selected {
  outline: 2px solid var(--primary, #3498db);
  outline-offset: 2px;
}

.image-loading,
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #6c757d;
  font-size: 14px;
  text-align: center;
  padding: 20px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e9ecef;
  border-top: 3px solid var(--primary, #3498db);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.image-error svg {
  color: #6c757d;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* Hover effects */
.visual-image:hover img {
  transform: scale(1.02);
}

.visual-image.selected:hover img {
  transform: scale(1.05);
}

/* Responsive image */
img {
  max-width: 100%;
  max-height: 100%;
  user-select: none;
  -webkit-user-drag: none;
}
</style>