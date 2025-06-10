<template>
  <div
    class="element-toolbar"
    :style="toolbarStyle"
  >
    <div class="toolbar-content">
      <!-- Common tools -->
      <button class="tool-btn" @click="bringToFront" title="Bring to Front">
        ⬆️
      </button>
      <button class="tool-btn" @click="sendToBack" title="Send to Back">
        ⬇️
      </button>
      <div class="toolbar-separator"></div>
      
      <!-- Text-specific tools -->
      <template v-if="hasTextElements">
        <button 
          class="tool-btn" 
          :class="{ active: isBold }"
          @click="toggleBold"
          title="Bold"
        >
          <strong>B</strong>
        </button>
        <button 
          class="tool-btn"
          :class="{ active: isItalic }"
          @click="toggleItalic"
          title="Italic"
        >
          <em>I</em>
        </button>
        <button 
          class="tool-btn"
          :class="{ active: isUnderline }"
          @click="toggleUnderline"
          title="Underline"
        >
          <u>U</u>
        </button>
        <div class="toolbar-separator"></div>
      </template>
      
      <!-- Alignment tools -->
      <button class="tool-btn" @click="alignLeft" title="Align Left">
        ⬅️
      </button>
      <button class="tool-btn" @click="alignCenter" title="Align Center">
        ↔️
      </button>
      <button class="tool-btn" @click="alignRight" title="Align Right">
        ➡️
      </button>
      <div class="toolbar-separator"></div>
      
      <!-- Actions -->
      <button class="tool-btn" @click="duplicateElements" title="Duplicate">
        📋
      </button>
      <button class="tool-btn danger" @click="deleteElements" title="Delete">
        🗑️
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePresentationStore } from '@/stores'
import type { PPTElement } from '@/types/slides'

interface Props {
  elements: PPTElement[]
  position: { x: number; y: number }
}

const props = defineProps<Props>()
const presentationStore = usePresentationStore()

const toolbarStyle = computed(() => ({
  position: 'absolute',
  left: `${props.position.x}px`,
  top: `${props.position.y}px`,
  transform: 'translateX(-50%)',
  zIndex: 1000
}))

const hasTextElements = computed(() => {
  return props.elements.some(el => el.type === 'text')
})

const isBold = computed(() => {
  return props.elements
    .filter(el => el.type === 'text')
    .every(el => (el as any).bold)
})

const isItalic = computed(() => {
  return props.elements
    .filter(el => el.type === 'text')
    .every(el => (el as any).italic)
})

const isUnderline = computed(() => {
  return props.elements
    .filter(el => el.type === 'text')
    .every(el => (el as any).underline)
})

async function toggleBold() {
  const textElements = props.elements.filter(el => el.type === 'text')
  const newBold = !isBold.value
  
  for (const element of textElements) {
    await presentationStore.modifyElement(element.id, { bold: newBold })
  }
}

async function toggleItalic() {
  const textElements = props.elements.filter(el => el.type === 'text')
  const newItalic = !isItalic.value
  
  for (const element of textElements) {
    await presentationStore.modifyElement(element.id, { italic: newItalic })
  }
}

async function toggleUnderline() {
  const textElements = props.elements.filter(el => el.type === 'text')
  const newUnderline = !isUnderline.value
  
  for (const element of textElements) {
    await presentationStore.modifyElement(element.id, { underline: newUnderline })
  }
}

async function alignLeft() {
  for (const element of props.elements) {
    if (element.type === 'text') {
      await presentationStore.modifyElement(element.id, { align: 'left' })
    }
  }
}

async function alignCenter() {
  for (const element of props.elements) {
    if (element.type === 'text') {
      await presentationStore.modifyElement(element.id, { align: 'center' })
    }
  }
}

async function alignRight() {
  for (const element of props.elements) {
    if (element.type === 'text') {
      await presentationStore.modifyElement(element.id, { align: 'right' })
    }
  }
}

async function bringToFront() {
  const maxZIndex = Math.max(
    ...presentationStore.currentSlide!.elements.map(el => el.zIndex || 1)
  )
  
  for (const element of props.elements) {
    await presentationStore.modifyElement(element.id, { zIndex: maxZIndex + 1 })
  }
}

async function sendToBack() {
  const minZIndex = Math.min(
    ...presentationStore.currentSlide!.elements.map(el => el.zIndex || 1)
  )
  
  for (const element of props.elements) {
    await presentationStore.modifyElement(element.id, { zIndex: Math.max(0, minZIndex - 1) })
  }
}

async function duplicateElements() {
  presentationStore.copyElements(props.elements.map(el => el.id))
  await presentationStore.pasteElements()
}

async function deleteElements() {
  for (const element of props.elements) {
    await presentationStore.removeElement(element.id)
  }
  presentationStore.clearSelection()
}
</script>

<style scoped>
.element-toolbar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 4px 16px var(--shadow-dark);
  padding: var(--spacing-xs);
}

.toolbar-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.tool-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 14px;
}

.tool-btn:hover {
  background: var(--border-light);
}

.tool-btn.active {
  background: var(--primary);
  color: white;
}

.tool-btn.danger:hover {
  background: var(--accent);
  color: white;
}

.toolbar-separator {
  width: 1px;
  height: 20px;
  background: var(--border);
  margin: 0 var(--spacing-xs);
}
</style>