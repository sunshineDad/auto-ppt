<template>
  <div class="visual-shape" :class="shapeClasses">
    <svg
      class="shape-svg"
      :viewBox="viewBox"
      :style="svgStyle"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- Gradient definitions -->
      <defs v-if="component.style.gradient">
        <linearGradient
          v-if="component.style.gradient.type === 'linear'"
          :id="`gradient-${component.id}`"
          :gradientTransform="`rotate(${component.style.gradient.direction || 0})`"
        >
          <stop
            v-for="(stop, index) in component.style.gradient.stops"
            :key="index"
            :offset="`${stop.position}%`"
            :stop-color="stop.color"
          />
        </linearGradient>
        
        <radialGradient
          v-else-if="component.style.gradient.type === 'radial'"
          :id="`gradient-${component.id}`"
        >
          <stop
            v-for="(stop, index) in component.style.gradient.stops"
            :key="index"
            :offset="`${stop.position}%`"
            :stop-color="stop.color"
          />
        </radialGradient>
      </defs>
      
      <!-- Pattern definitions -->
      <defs v-if="component.style.pattern">
        <pattern
          :id="`pattern-${component.id}`"
          :patternUnits="'userSpaceOnUse'"
          :width="component.style.pattern.size + component.style.pattern.spacing"
          :height="component.style.pattern.size + component.style.pattern.spacing"
        >
          <rect
            v-if="component.style.pattern.type === 'dots'"
            :width="component.style.pattern.size"
            :height="component.style.pattern.size"
            :fill="component.style.pattern.color"
            rx="50%"
          />
          <line
            v-else-if="component.style.pattern.type === 'lines'"
            x1="0"
            y1="0"
            :x2="component.style.pattern.size"
            :y2="component.style.pattern.size"
            :stroke="component.style.pattern.color"
            stroke-width="1"
          />
        </pattern>
      </defs>
      
      <!-- Rectangle -->
      <rect
        v-if="component.shape === 'rectangle'"
        :x="strokeWidth / 2"
        :y="strokeWidth / 2"
        :width="shapeWidth - strokeWidth"
        :height="shapeHeight - strokeWidth"
        :rx="component.style.cornerRadius || 0"
        :ry="component.style.cornerRadius || 0"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
      
      <!-- Circle -->
      <circle
        v-else-if="component.shape === 'circle'"
        :cx="shapeWidth / 2"
        :cy="shapeHeight / 2"
        :r="Math.min(shapeWidth, shapeHeight) / 2 - strokeWidth / 2"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
      
      <!-- Ellipse -->
      <ellipse
        v-else-if="component.shape === 'ellipse'"
        :cx="shapeWidth / 2"
        :cy="shapeHeight / 2"
        :rx="shapeWidth / 2 - strokeWidth / 2"
        :ry="shapeHeight / 2 - strokeWidth / 2"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
      
      <!-- Triangle -->
      <polygon
        v-else-if="component.shape === 'triangle'"
        :points="trianglePoints"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
      
      <!-- Star -->
      <polygon
        v-else-if="component.shape === 'star'"
        :points="starPoints"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
      
      <!-- Arrow -->
      <path
        v-else-if="component.shape === 'arrow'"
        :d="arrowPath"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
      
      <!-- Diamond -->
      <polygon
        v-else-if="component.shape === 'diamond'"
        :points="diamondPoints"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
      
      <!-- Hexagon -->
      <polygon
        v-else-if="component.shape === 'hexagon'"
        :points="hexagonPoints"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
      
      <!-- Heart -->
      <path
        v-else-if="component.shape === 'heart'"
        :d="heartPath"
        :fill="fillColor"
        :stroke="component.style.stroke"
        :stroke-width="strokeWidth"
        :stroke-dasharray="component.style.strokeDasharray"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ShapeComponent } from '../Types/ComponentTypes'

interface Props {
  component: ShapeComponent
  selected?: boolean
}

interface Emits {
  (e: 'update', component: ShapeComponent, changes: Partial<ShapeComponent>): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false
})

const emit = defineEmits<Emits>()

// Computed properties
const shapeClasses = computed(() => ({
  'visual-shape': true,
  'selected': props.selected
}))

const viewBox = computed(() => `0 0 ${props.component.width} ${props.component.height}`)
const shapeWidth = computed(() => props.component.width)
const shapeHeight = computed(() => props.component.height)
const strokeWidth = computed(() => props.component.style.strokeWidth || 0)

const svgStyle = computed(() => ({
  width: '100%',
  height: '100%',
  filter: props.component.style.shadow ? buildShadowFilter() : 'none'
}))

const fillColor = computed(() => {
  if (props.component.style.gradient) {
    return `url(#gradient-${props.component.id})`
  }
  if (props.component.style.pattern) {
    return `url(#pattern-${props.component.id})`
  }
  return props.component.style.fill
})

// Shape path calculations
const trianglePoints = computed(() => {
  const w = shapeWidth.value
  const h = shapeHeight.value
  return `${w/2},${strokeWidth.value/2} ${w-strokeWidth.value/2},${h-strokeWidth.value/2} ${strokeWidth.value/2},${h-strokeWidth.value/2}`
})

const starPoints = computed(() => {
  const cx = shapeWidth.value / 2
  const cy = shapeHeight.value / 2
  const outerRadius = Math.min(shapeWidth.value, shapeHeight.value) / 2 - strokeWidth.value / 2
  const innerRadius = outerRadius * 0.4
  const points = []
  
  for (let i = 0; i < 10; i++) {
    const angle = (i * Math.PI) / 5 - Math.PI / 2
    const radius = i % 2 === 0 ? outerRadius : innerRadius
    const x = cx + radius * Math.cos(angle)
    const y = cy + radius * Math.sin(angle)
    points.push(`${x},${y}`)
  }
  
  return points.join(' ')
})

const arrowPath = computed(() => {
  const w = shapeWidth.value
  const h = shapeHeight.value
  const sw = strokeWidth.value / 2
  const headWidth = w * 0.3
  const bodyHeight = h * 0.4
  
  return `M ${sw} ${h/2 - bodyHeight/2} 
          L ${w - headWidth - sw} ${h/2 - bodyHeight/2} 
          L ${w - headWidth - sw} ${sw} 
          L ${w - sw} ${h/2} 
          L ${w - headWidth - sw} ${h - sw} 
          L ${w - headWidth - sw} ${h/2 + bodyHeight/2} 
          L ${sw} ${h/2 + bodyHeight/2} Z`
})

const diamondPoints = computed(() => {
  const w = shapeWidth.value
  const h = shapeHeight.value
  const sw = strokeWidth.value / 2
  return `${w/2},${sw} ${w-sw},${h/2} ${w/2},${h-sw} ${sw},${h/2}`
})

const hexagonPoints = computed(() => {
  const cx = shapeWidth.value / 2
  const cy = shapeHeight.value / 2
  const radius = Math.min(shapeWidth.value, shapeHeight.value) / 2 - strokeWidth.value / 2
  const points = []
  
  for (let i = 0; i < 6; i++) {
    const angle = (i * Math.PI) / 3
    const x = cx + radius * Math.cos(angle)
    const y = cy + radius * Math.sin(angle)
    points.push(`${x},${y}`)
  }
  
  return points.join(' ')
})

const heartPath = computed(() => {
  const w = shapeWidth.value
  const h = shapeHeight.value
  const sw = strokeWidth.value / 2
  
  return `M ${w/2} ${h - sw}
          C ${w/2} ${h - sw}, ${sw} ${h/2}, ${sw} ${h/3}
          C ${sw} ${sw}, ${w/4} ${sw}, ${w/2} ${h/3}
          C ${3*w/4} ${sw}, ${w - sw} ${sw}, ${w - sw} ${h/3}
          C ${w - sw} ${h/2}, ${w/2} ${h - sw}, ${w/2} ${h - sw} Z`
})

// Helper functions
function buildShadowFilter() {
  const shadow = props.component.style.shadow
  if (!shadow) return 'none'
  
  return `drop-shadow(${shadow.offsetX}px ${shadow.offsetY}px ${shadow.blurRadius}px ${shadow.color})`
}
</script>

<style scoped>
.visual-shape {
  width: 100%;
  height: 100%;
  position: relative;
}

.visual-shape.selected {
  outline: 2px solid var(--primary, #3498db);
  outline-offset: 2px;
}

.shape-svg {
  display: block;
  user-select: none;
}

/* Hover effects */
.visual-shape:hover .shape-svg {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

.visual-shape.selected:hover .shape-svg {
  transform: scale(1.05);
}
</style>