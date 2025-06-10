<template>
  <div class="multi-element-properties">
    <!-- Alignment Tools -->
    <div class="property-group">
      <label>Alignment</label>
      <div class="alignment-grid">
        <button class="align-btn" @click="alignElements('left')" title="Align Left">
          ⬅️
        </button>
        <button class="align-btn" @click="alignElements('center-h')" title="Align Center">
          ↔️
        </button>
        <button class="align-btn" @click="alignElements('right')" title="Align Right">
          ➡️
        </button>
        <button class="align-btn" @click="alignElements('top')" title="Align Top">
          ⬆️
        </button>
        <button class="align-btn" @click="alignElements('center-v')" title="Align Middle">
          ↕️
        </button>
        <button class="align-btn" @click="alignElements('bottom')" title="Align Bottom">
          ⬇️
        </button>
      </div>
    </div>

    <!-- Distribution -->
    <div class="property-group">
      <label>Distribution</label>
      <div class="button-row">
        <button class="btn btn-sm" @click="distributeElements('horizontal')">
          ↔️ Horizontal
        </button>
        <button class="btn btn-sm" @click="distributeElements('vertical')">
          ↕️ Vertical
        </button>
      </div>
    </div>

    <!-- Spacing -->
    <div class="property-group">
      <label>Spacing</label>
      <div class="input-row">
        <div class="input-group">
          <label>Horizontal</label>
          <input 
            type="number" 
            v-model="spacing.horizontal"
            @change="applySpacing"
            min="0"
          />
        </div>
        <div class="input-group">
          <label>Vertical</label>
          <input 
            type="number" 
            v-model="spacing.vertical"
            @change="applySpacing"
            min="0"
          />
        </div>
      </div>
    </div>

    <!-- Common Properties -->
    <div class="property-group">
      <label>Common Properties</label>
      
      <!-- Opacity -->
      <div class="input-row">
        <div class="input-group">
          <label>Opacity</label>
          <input 
            type="range" 
            :value="commonOpacity * 100"
            @input="updateCommonProperty('opacity', Number($event.target.value) / 100)"
            min="0"
            max="100"
          />
        </div>
      </div>

      <!-- Rotation -->
      <div class="input-row">
        <div class="input-group">
          <label>Rotation</label>
          <input 
            type="number" 
            :value="commonRotation"
            @input="updateCommonProperty('rotate', Number($event.target.value))"
            min="0"
            max="360"
          />
        </div>
      </div>
    </div>

    <!-- Text Properties (if all selected elements are text) -->
    <div v-if="allElementsAreText" class="property-group">
      <label>Text Properties</label>
      
      <div class="input-row">
        <div class="input-group">
          <label>Font Size</label>
          <input 
            type="number" 
            :value="commonFontSize"
            @input="updateCommonProperty('fontSize', Number($event.target.value))"
            min="8"
            max="72"
          />
        </div>
        <div class="input-group">
          <label>Color</label>
          <input 
            type="color" 
            :value="commonColor"
            @input="updateCommonProperty('color', $event.target.value)"
          />
        </div>
      </div>

      <div class="checkbox-row">
        <label class="checkbox-label">
          <input 
            type="checkbox" 
            :checked="commonBold"
            @change="updateCommonProperty('bold', $event.target.checked)"
          />
          Bold
        </label>
        <label class="checkbox-label">
          <input 
            type="checkbox" 
            :checked="commonItalic"
            @change="updateCommonProperty('italic', $event.target.checked)"
          />
          Italic
        </label>
      </div>
    </div>

    <!-- Layer Controls -->
    <div class="property-group">
      <label>Layer</label>
      <div class="button-row">
        <button class="btn btn-sm" @click="bringToFront">
          ⬆️ Front
        </button>
        <button class="btn btn-sm" @click="sendToBack">
          ⬇️ Back
        </button>
      </div>
    </div>

    <!-- Group Controls -->
    <div class="property-group">
      <label>Group</label>
      <div class="button-row">
        <button class="btn btn-sm" @click="groupElements">
          🔗 Group
        </button>
        <button class="btn btn-sm" @click="ungroupElements">
          🔓 Ungroup
        </button>
      </div>
    </div>

    <!-- Actions -->
    <div class="property-group">
      <label>Actions</label>
      <div class="button-row">
        <button class="btn btn-sm" @click="duplicateElements">
          📋 Duplicate
        </button>
        <button class="btn btn-sm btn-danger" @click="deleteElements">
          🗑️ Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePresentationStore } from '@/stores'
import type { PPTElement } from '@/types/slides'
import { v4 as uuidv4 } from 'uuid'

interface Props {
  elements: PPTElement[]
}

const props = defineProps<Props>()
const presentationStore = usePresentationStore()

const spacing = ref({
  horizontal: 20,
  vertical: 20
})

// Computed properties for common values
const allElementsAreText = computed(() => {
  return props.elements.every(el => el.type === 'text')
})

const commonOpacity = computed(() => {
  const opacities = props.elements.map(el => el.opacity || 1)
  return opacities.every(o => o === opacities[0]) ? opacities[0] : 1
})

const commonRotation = computed(() => {
  const rotations = props.elements.map(el => el.rotate)
  return rotations.every(r => r === rotations[0]) ? rotations[0] : 0
})

const commonFontSize = computed(() => {
  if (!allElementsAreText.value) return 16
  const fontSizes = props.elements.map(el => (el as any).fontSize || 16)
  return fontSizes.every(s => s === fontSizes[0]) ? fontSizes[0] : 16
})

const commonColor = computed(() => {
  if (!allElementsAreText.value) return '#333333'
  const colors = props.elements.map(el => (el as any).color || (el as any).defaultColor)
  return colors.every(c => c === colors[0]) ? colors[0] : '#333333'
})

const commonBold = computed(() => {
  if (!allElementsAreText.value) return false
  const bolds = props.elements.map(el => (el as any).bold || false)
  return bolds.every(b => b === bolds[0]) ? bolds[0] : false
})

const commonItalic = computed(() => {
  if (!allElementsAreText.value) return false
  const italics = props.elements.map(el => (el as any).italic || false)
  return italics.every(i => i === italics[0]) ? italics[0] : false
})

// Alignment functions
async function alignElements(alignment: string) {
  const bounds = getElementsBounds()
  
  for (const element of props.elements) {
    let newLeft = element.left
    let newTop = element.top
    
    switch (alignment) {
      case 'left':
        newLeft = bounds.left
        break
      case 'center-h':
        newLeft = bounds.left + (bounds.width - element.width) / 2
        break
      case 'right':
        newLeft = bounds.left + bounds.width - element.width
        break
      case 'top':
        newTop = bounds.top
        break
      case 'center-v':
        newTop = bounds.top + (bounds.height - element.height) / 2
        break
      case 'bottom':
        newTop = bounds.top + bounds.height - element.height
        break
    }
    
    await presentationStore.modifyElement(element.id, {
      left: newLeft,
      top: newTop
    })
  }
}

async function distributeElements(direction: 'horizontal' | 'vertical') {
  if (props.elements.length < 3) return
  
  const sortedElements = [...props.elements].sort((a, b) => {
    return direction === 'horizontal' ? a.left - b.left : a.top - b.top
  })
  
  const first = sortedElements[0]
  const last = sortedElements[sortedElements.length - 1]
  
  const totalSpace = direction === 'horizontal' 
    ? (last.left + last.width) - first.left
    : (last.top + last.height) - first.top
  
  const totalElementSize = sortedElements.reduce((sum, el) => {
    return sum + (direction === 'horizontal' ? el.width : el.height)
  }, 0)
  
  const spacing = (totalSpace - totalElementSize) / (sortedElements.length - 1)
  
  let currentPos = direction === 'horizontal' ? first.left : first.top
  
  for (let i = 1; i < sortedElements.length - 1; i++) {
    const element = sortedElements[i]
    const prevElement = sortedElements[i - 1]
    
    currentPos += (direction === 'horizontal' ? prevElement.width : prevElement.height) + spacing
    
    await presentationStore.modifyElement(element.id, {
      [direction === 'horizontal' ? 'left' : 'top']: currentPos
    })
  }
}

async function applySpacing() {
  // Apply uniform spacing between elements
  const sortedElements = [...props.elements].sort((a, b) => a.left - b.left)
  
  for (let i = 1; i < sortedElements.length; i++) {
    const prevElement = sortedElements[i - 1]
    const currentElement = sortedElements[i]
    
    await presentationStore.modifyElement(currentElement.id, {
      left: prevElement.left + prevElement.width + spacing.value.horizontal,
      top: prevElement.top + spacing.value.vertical
    })
  }
}

async function updateCommonProperty(property: string, value: any) {
  for (const element of props.elements) {
    await presentationStore.modifyElement(element.id, {
      [property]: value
    })
  }
}

async function bringToFront() {
  const currentSlide = presentationStore.currentSlide
  if (!currentSlide) return
  
  const maxZIndex = Math.max(
    ...currentSlide.elements.map(el => el.zIndex || 1)
  )
  
  for (const element of props.elements) {
    await presentationStore.modifyElement(element.id, {
      zIndex: maxZIndex + 1
    })
  }
}

async function sendToBack() {
  const currentSlide = presentationStore.currentSlide
  if (!currentSlide) return
  
  const minZIndex = Math.min(
    ...currentSlide.elements.map(el => el.zIndex || 1)
  )
  
  for (const element of props.elements) {
    await presentationStore.modifyElement(element.id, {
      zIndex: Math.max(0, minZIndex - 1)
    })
  }
}

async function groupElements() {
  const groupId = uuidv4()
  
  for (const element of props.elements) {
    await presentationStore.modifyElement(element.id, {
      groupId
    })
  }
}

async function ungroupElements() {
  for (const element of props.elements) {
    await presentationStore.modifyElement(element.id, {
      groupId: undefined
    })
  }
}

async function duplicateElements() {
  presentationStore.copyElements(props.elements.map(el => el.id))
  await presentationStore.pasteElements()
}

async function deleteElements() {
  if (confirm(`Delete ${props.elements.length} elements?`)) {
    for (const element of props.elements) {
      await presentationStore.removeElement(element.id)
    }
    presentationStore.clearSelection()
  }
}

function getElementsBounds() {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  
  for (const element of props.elements) {
    minX = Math.min(minX, element.left)
    minY = Math.min(minY, element.top)
    maxX = Math.max(maxX, element.left + element.width)
    maxY = Math.max(maxY, element.top + element.height)
  }
  
  return {
    left: minX,
    top: minY,
    width: maxX - minX,
    height: maxY - minY
  }
}
</script>

<style scoped>
.multi-element-properties {
  font-size: var(--font-size-sm);
}

.property-group {
  margin-bottom: var(--spacing-lg);
}

.property-group > label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.alignment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.align-btn {
  aspect-ratio: 1;
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.align-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.input-row {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.input-group {
  flex: 1;
}

.input-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.input-group input,
.input-group select {
  width: 100%;
  padding: var(--spacing-xs);
  border: 1px solid var(--border);
  border-radius: var(--border-radius);
  font-size: var(--font-size-xs);
}

.input-group input[type="color"] {
  height: 32px;
  padding: 2px;
}

.input-group input[type="range"] {
  padding: 0;
}

.checkbox-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.button-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.btn-danger {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.btn-danger:hover {
  background: #D32F2F;
  border-color: #D32F2F;
}
</style>