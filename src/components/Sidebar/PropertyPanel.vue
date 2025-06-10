<template>
  <div class="property-panel">
    <div class="panel-header">
      <h3>Properties</h3>
    </div>
    
    <div class="panel-content">
      <!-- No selection state -->
      <div v-if="selectedElements.length === 0" class="no-selection">
        <div class="no-selection-icon">🎯</div>
        <p>Select an element to edit its properties</p>
      </div>
      
      <!-- Single element selected -->
      <div v-else-if="selectedElements.length === 1" class="single-element">
        <ElementProperties :element="selectedElements[0]" />
      </div>
      
      <!-- Multiple elements selected -->
      <div v-else class="multiple-elements">
        <div class="selection-info">
          <strong>{{ selectedElements.length }} elements selected</strong>
        </div>
        <MultiElementProperties :elements="selectedElements" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePresentationStore } from '@/stores'
import ElementProperties from './ElementProperties.vue'
import MultiElementProperties from './MultiElementProperties.vue'

const presentationStore = usePresentationStore()

const selectedElements = computed(() => {
  const currentSlide = presentationStore.currentSlide
  if (!currentSlide) return []
  
  return currentSlide.elements.filter(el => 
    presentationStore.selectedElements.includes(el.id)
  )
})
</script>

<style scoped>
.property-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--surface);
}

.panel-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border);
}

.panel-header h3 {
  margin: 0;
  font-size: var(--font-size-md);
  color: var(--text-primary);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  text-align: center;
  color: var(--text-secondary);
}

.no-selection-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.no-selection p {
  margin: 0;
  font-size: var(--font-size-sm);
}

.selection-info {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-sm);
  background: var(--border-light);
  border-radius: var(--border-radius);
  text-align: center;
  font-size: var(--font-size-sm);
}

/* Scrollbar styling */
.panel-content::-webkit-scrollbar {
  width: 4px;
}

.panel-content::-webkit-scrollbar-track {
  background: transparent;
}

.panel-content::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 2px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: var(--text-disabled);
}
</style>