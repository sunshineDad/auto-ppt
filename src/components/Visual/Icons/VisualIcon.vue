<template>
  <div class="visual-icon" :class="iconClasses" :style="iconContainerStyle">
    <!-- Feather Icons -->
    <svg
      v-if="component.iconSet === 'feather'"
      :width="component.style.size"
      :height="component.style.size"
      :style="iconStyle"
      viewBox="0 0 24 24"
      fill="none"
      :stroke="component.style.color"
      :stroke-width="component.style.strokeWidth || 2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <component :is="getFeatherIcon(component.iconName)" />
    </svg>
    
    <!-- Material Icons -->
    <span
      v-else-if="component.iconSet === 'material'"
      class="material-icons"
      :style="materialIconStyle"
    >
      {{ component.iconName }}
    </span>
    
    <!-- Heroicons -->
    <svg
      v-else-if="component.iconSet === 'heroicons'"
      :width="component.style.size"
      :height="component.style.size"
      :style="iconStyle"
      viewBox="0 0 24 24"
      :fill="component.style.fill ? component.style.color : 'none'"
      :stroke="component.style.fill ? 'none' : component.style.color"
      :stroke-width="component.style.strokeWidth || 2"
    >
      <component :is="getHeroIcon(component.iconName)" />
    </svg>
    
    <!-- Lucide Icons -->
    <svg
      v-else-if="component.iconSet === 'lucide'"
      :width="component.style.size"
      :height="component.style.size"
      :style="iconStyle"
      viewBox="0 0 24 24"
      fill="none"
      :stroke="component.style.color"
      :stroke-width="component.style.strokeWidth || 2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <component :is="getLucideIcon(component.iconName)" />
    </svg>
    
    <!-- Custom/Fallback Icon -->
    <div v-else class="custom-icon" :style="customIconStyle">
      {{ component.iconName.charAt(0).toUpperCase() }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import type { IconComponent } from '../Types/ComponentTypes'

interface Props {
  component: IconComponent
  selected?: boolean
}

interface Emits {
  (e: 'update', component: IconComponent, changes: Partial<IconComponent>): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false
})

const emit = defineEmits<Emits>()

// Computed properties
const iconClasses = computed(() => ({
  'visual-icon': true,
  'selected': props.selected,
  [`icon-set-${props.component.iconSet}`]: true
}))

const iconContainerStyle = computed(() => ({
  width: '100%',
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  position: 'relative',
  transform: `rotate(${props.component.style.rotation || 0}deg)`,
  filter: props.component.style.shadow ? buildShadowFilter() : 'none'
}))

const iconStyle = computed(() => ({
  width: `${props.component.style.size}px`,
  height: `${props.component.style.size}px`,
  color: props.component.style.color,
  fill: props.component.style.fill ? props.component.style.color : 'none',
  stroke: props.component.style.fill ? 'none' : props.component.style.color,
  strokeWidth: props.component.style.strokeWidth || 2,
  transition: 'all 0.2s ease',
  background: props.component.style.gradient ? buildGradientString() : 'transparent'
}))

const materialIconStyle = computed(() => ({
  fontSize: `${props.component.style.size}px`,
  color: props.component.style.color,
  lineHeight: 1,
  userSelect: 'none',
  transition: 'all 0.2s ease'
}))

const customIconStyle = computed(() => ({
  width: `${props.component.style.size}px`,
  height: `${props.component.style.size}px`,
  backgroundColor: props.component.style.color,
  color: 'white',
  borderRadius: '50%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: `${props.component.style.size * 0.6}px`,
  fontWeight: 'bold',
  userSelect: 'none'
}))

// Helper functions
function buildShadowFilter() {
  const shadow = props.component.style.shadow
  if (!shadow) return 'none'
  
  return `drop-shadow(${shadow.offsetX}px ${shadow.offsetY}px ${shadow.blurRadius}px ${shadow.color})`
}

function buildGradientString() {
  const gradient = props.component.style.gradient
  if (!gradient) return 'transparent'
  
  const stops = gradient.stops.map(stop => `${stop.color} ${stop.position}%`).join(', ')
  
  if (gradient.type === 'linear') {
    return `linear-gradient(${gradient.direction || 0}deg, ${stops})`
  } else if (gradient.type === 'radial') {
    return `radial-gradient(circle, ${stops})`
  }
  
  return 'transparent'
}

// Icon component getters - using inline SVG paths for simplicity
function getFeatherIcon(iconName: string) {
  const iconPaths: Record<string, string> = {
    star: 'M12 2l3.09 6.26L22 9l-5 4.87L18.18 21 12 17.77 5.82 21 7 13.87 2 9l6.91-1.26L12 2z',
    heart: 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z',
    home: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10',
    user: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
    settings: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
    search: 'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z M21 21l-4.35-4.35',
    mail: 'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z M22 6l-10 7L2 6',
    phone: 'M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z',
    calendar: 'M3 4a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4z M8 2v4 M16 2v4 M3 10h18',
    clock: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M12 6v6l4 2',
    download: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M7 10l5 5 5-5 M12 15V3',
    upload: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M17 8l-5-5-5 5 M12 3v12',
    edit: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7 M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z',
    trash: 'M3 6h18 M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2',
    plus: 'M12 5v14 M5 12h14',
    minus: 'M5 12h14',
    check: 'M20 6L9 17l-5-5',
    x: 'M18 6L6 18 M6 6l12 12',
    arrow_right: 'M5 12h14 M12 5l7 7-7 7',
    arrow_left: 'M19 12H5 M12 19l-7-7 7-7',
    arrow_up: 'M12 19V5 M5 12l7-7 7 7',
    arrow_down: 'M12 5v14 M19 12l-7 7-7-7'
  }
  
  return iconPaths[iconName] || iconPaths.star
}

function getHeroIcon(iconName: string) {
  // Use same paths for now
  return getFeatherIcon(iconName)
}

function getLucideIcon(iconName: string) {
  // Use same paths for now
  return getFeatherIcon(iconName)
}
</script>

<style scoped>
.visual-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  user-select: none;
}

.visual-icon.selected {
  outline: 2px solid var(--primary, #3498db);
  outline-offset: 2px;
}

/* Icon set specific styles */
.icon-set-material .material-icons {
  font-family: 'Material Icons';
  font-weight: normal;
  font-style: normal;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
}

.icon-set-feather svg,
.icon-set-heroicons svg,
.icon-set-lucide svg {
  display: block;
}

.custom-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Hover effects */
.visual-icon:hover {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}

.visual-icon.selected:hover {
  transform: scale(1.15);
}

/* Animation effects */
.visual-icon svg {
  transition: all 0.2s ease;
}

.visual-icon:hover svg {
  filter: brightness(1.1);
}

/* Responsive sizing */
@media (max-width: 768px) {
  .visual-icon {
    min-width: 24px;
    min-height: 24px;
  }
}
</style>