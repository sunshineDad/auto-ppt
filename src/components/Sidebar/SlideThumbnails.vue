<template>
  <div class="slide-thumbnails">
    <div class="thumbnails-header">
      <h3>Slides</h3>
      <button class="btn btn-sm btn-primary" @click="addSlide">
        + Add
      </button>
    </div>
    
    <div class="thumbnails-list">
      <div
        v-for="(slide, index) in presentationStore.presentation.slides"
        :key="slide.id"
        :class="[
          'thumbnail-item',
          { active: index === presentationStore.canvas.activeSlide }
        ]"
        @click="selectSlide(index)"
        @contextmenu="showContextMenu($event, index)"
      >
        <div class="thumbnail-preview">
          <div class="slide-number">{{ index + 1 }}</div>
          <div class="slide-content">
            <!-- Mini preview of slide elements -->
            <div
              v-for="element in slide.elements"
              :key="element.id"
              :class="`mini-element mini-${element.type}`"
              :style="getMiniElementStyle(element)"
            >
              <span v-if="element.type === 'text'" class="mini-text">
                {{ getTextPreview(element) }}
              </span>
              <div v-else-if="element.type === 'image'" class="mini-image">🖼️</div>
              <div v-else-if="element.type === 'shape'" class="mini-shape">🔷</div>
              <div v-else-if="element.type === 'chart'" class="mini-chart">📊</div>
              <div v-else-if="element.type === 'table'" class="mini-table">📋</div>
            </div>
          </div>
        </div>
        
        <div class="thumbnail-info">
          <div class="slide-title">
            {{ getSlideTitle(slide) || `Slide ${index + 1}` }}
          </div>
          <div class="element-count">
            {{ slide.elements.length }} elements
          </div>
        </div>
      </div>
    </div>
    
    <!-- Context Menu -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="contextMenuStyle"
      @click.stop
    >
      <button class="context-item" @click="duplicateSlide">
        📋 Duplicate
      </button>
      <button class="context-item" @click="deleteSlide">
        🗑️ Delete
      </button>
      <div class="context-separator"></div>
      <button class="context-item" @click="moveSlideUp">
        ⬆️ Move Up
      </button>
      <button class="context-item" @click="moveSlideDown">
        ⬇️ Move Down
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePresentationStore } from '@/stores'
import type { Slide, PPTElement } from '@/types/slides'

const presentationStore = usePresentationStore()

const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  slideIndex: -1
})

const contextMenuStyle = computed(() => ({
  position: 'fixed',
  left: `${contextMenu.value.x}px`,
  top: `${contextMenu.value.y}px`,
  zIndex: 1000
}))

function selectSlide(index: number) {
  presentationStore.setActiveSlide(index)
}

async function addSlide() {
  await presentationStore.createSlide()
}

function showContextMenu(event: MouseEvent, slideIndex: number) {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    slideIndex
  }
}

function hideContextMenu() {
  contextMenu.value.visible = false
}

async function duplicateSlide() {
  const slideIndex = contextMenu.value.slideIndex
  const slide = presentationStore.presentation.slides[slideIndex]
  
  if (slide) {
    await presentationStore.createSlide({
      layout: slide.layout,
      elements: slide.elements.map(el => ({ ...el }))
    })
  }
  
  hideContextMenu()
}

async function deleteSlide() {
  const slideIndex = contextMenu.value.slideIndex
  
  if (presentationStore.presentation.slides.length > 1) {
    if (confirm('Delete this slide?')) {
      await presentationStore.deleteSlide(slideIndex)
    }
  }
  
  hideContextMenu()
}

async function moveSlideUp() {
  const slideIndex = contextMenu.value.slideIndex
  
  if (slideIndex > 0) {
    const slides = [...presentationStore.presentation.slides]
    const slide = slides.splice(slideIndex, 1)[0]
    slides.splice(slideIndex - 1, 0, slide)
    
    const newOrder = slides.map((_, i) => i)
    await presentationStore.reorderSlides(newOrder)
    
    presentationStore.setActiveSlide(slideIndex - 1)
  }
  
  hideContextMenu()
}

async function moveSlideDown() {
  const slideIndex = contextMenu.value.slideIndex
  const totalSlides = presentationStore.presentation.slides.length
  
  if (slideIndex < totalSlides - 1) {
    const slides = [...presentationStore.presentation.slides]
    const slide = slides.splice(slideIndex, 1)[0]
    slides.splice(slideIndex + 1, 0, slide)
    
    const newOrder = slides.map((_, i) => i)
    await presentationStore.reorderSlides(newOrder)
    
    presentationStore.setActiveSlide(slideIndex + 1)
  }
  
  hideContextMenu()
}

function getMiniElementStyle(element: PPTElement) {
  const slideWidth = 160
  const slideHeight = 90
  const scaleX = slideWidth / presentationStore.presentation.settings.width
  const scaleY = slideHeight / presentationStore.presentation.settings.height
  
  return {
    position: 'absolute',
    left: `${element.left * scaleX}px`,
    top: `${element.top * scaleY}px`,
    width: `${element.width * scaleX}px`,
    height: `${element.height * scaleY}px`,
    transform: `rotate(${element.rotate}deg)`
  }
}

function getTextPreview(element: any): string {
  if (element.type !== 'text') return ''
  
  // Strip HTML tags and get first few words
  const text = element.content.replace(/<[^>]*>/g, '')
  const words = text.split(' ').slice(0, 3)
  return words.join(' ') + (words.length < text.split(' ').length ? '...' : '')
}

function getSlideTitle(slide: Slide): string {
  // Try to find a title element
  const titleElement = slide.elements.find(el => 
    el.type === 'text' && (el as any).style === 'heading'
  )
  
  if (titleElement) {
    return getTextPreview(titleElement)
  }
  
  // Fallback to first text element
  const firstText = slide.elements.find(el => el.type === 'text')
  if (firstText) {
    return getTextPreview(firstText)
  }
  
  return ''
}

function handleClickOutside(event: MouseEvent) {
  if (contextMenu.value.visible) {
    hideContextMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.slide-thumbnails {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--surface);
}

.thumbnails-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border);
}

.thumbnails-header h3 {
  margin: 0;
  font-size: var(--font-size-md);
  color: var(--text-primary);
}

.thumbnails-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.thumbnail-item {
  margin-bottom: var(--spacing-sm);
  border: 2px solid transparent;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--background);
}

.thumbnail-item:hover {
  border-color: var(--border);
}

.thumbnail-item.active {
  border-color: var(--primary);
  background: var(--surface);
}

.thumbnail-preview {
  position: relative;
  width: 100%;
  height: 90px;
  background: white;
  border-radius: var(--border-radius) var(--border-radius) 0 0;
  overflow: hidden;
}

.slide-number {
  position: absolute;
  top: var(--spacing-xs);
  left: var(--spacing-xs);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: var(--border-radius);
  font-size: 10px;
  font-weight: bold;
  z-index: 10;
}

.slide-content {
  position: relative;
  width: 100%;
  height: 100%;
}

.mini-element {
  border-radius: 2px;
  overflow: hidden;
  font-size: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-text {
  background: rgba(51, 51, 51, 0.1);
  color: #333;
  padding: 1px;
  line-height: 1;
  font-size: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-image {
  background: rgba(33, 150, 243, 0.2);
  color: #1976D2;
}

.mini-shape {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.mini-chart {
  background: rgba(255, 152, 0, 0.2);
  color: #FF9800;
}

.mini-table {
  background: rgba(156, 39, 176, 0.2);
  color: #9C27B0;
}

.thumbnail-info {
  padding: var(--spacing-sm);
  border-top: 1px solid var(--border-light);
}

.slide-title {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.element-count {
  font-size: 10px;
  color: var(--text-secondary);
}

/* Context Menu */
.context-menu {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 16px var(--shadow-dark);
  padding: var(--spacing-xs);
  min-width: 120px;
}

.context-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  width: 100%;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: none;
  background: none;
  text-align: left;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  font-size: var(--font-size-xs);
}

.context-item:hover {
  background: var(--border-light);
}

.context-separator {
  height: 1px;
  background: var(--border);
  margin: var(--spacing-xs) 0;
}

/* Scrollbar styling */
.thumbnails-list::-webkit-scrollbar {
  width: 4px;
}

.thumbnails-list::-webkit-scrollbar-track {
  background: transparent;
}

.thumbnails-list::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 2px;
}

.thumbnails-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-disabled);
}
</style>