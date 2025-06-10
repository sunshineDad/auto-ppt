<template>
  <div
    class="context-menu"
    :style="menuStyle"
    @click.stop
  >
    <div
      v-for="(item, index) in items"
      :key="index"
      :class="[
        'menu-item',
        { 
          'separator': item.type === 'separator',
          'disabled': item.disabled
        }
      ]"
      @click="handleItemClick(item)"
    >
      <template v-if="item.type !== 'separator'">
        <span class="menu-icon">{{ item.icon }}</span>
        <span class="menu-label">{{ item.label }}</span>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'

interface MenuItem {
  label?: string
  action?: string
  icon?: string
  type?: 'separator'
  disabled?: boolean
}

interface Props {
  x: number
  y: number
  items: MenuItem[]
}

interface Emits {
  (e: 'select', action: string): void
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const menuStyle = computed(() => ({
  position: 'fixed',
  left: `${props.x}px`,
  top: `${props.y}px`,
  zIndex: 2000
}))

function handleItemClick(item: MenuItem) {
  if (item.type === 'separator' || item.disabled) return
  
  if (item.action) {
    emit('select', item.action)
  }
  emit('close')
}

function handleClickOutside(event: MouseEvent) {
  emit('close')
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('contextmenu', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('contextmenu', handleClickOutside)
})
</script>

<style scoped>
.context-menu {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 8px 32px var(--shadow-dark);
  padding: var(--spacing-xs);
  min-width: 180px;
  font-size: var(--font-size-sm);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.menu-item:hover:not(.disabled):not(.separator) {
  background-color: var(--border-light);
}

.menu-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-item.separator {
  height: 1px;
  background-color: var(--border);
  margin: var(--spacing-xs) 0;
  padding: 0;
  cursor: default;
}

.menu-icon {
  width: 16px;
  text-align: center;
}

.menu-label {
  flex: 1;
}
</style>