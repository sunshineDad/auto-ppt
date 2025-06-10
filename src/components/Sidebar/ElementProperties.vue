<template>
  <div class="element-properties">
    <div class="property-section">
      <h4>{{ getElementTypeName(element.type) }}</h4>
      
      <!-- Position & Size -->
      <div class="property-group">
        <label>Position & Size</label>
        <div class="input-row">
          <div class="input-group">
            <label>X</label>
            <input 
              type="number" 
              :value="Math.round(element.left)"
              @input="updateProperty('left', Number($event.target.value))"
            />
          </div>
          <div class="input-group">
            <label>Y</label>
            <input 
              type="number" 
              :value="Math.round(element.top)"
              @input="updateProperty('top', Number($event.target.value))"
            />
          </div>
        </div>
        <div class="input-row">
          <div class="input-group">
            <label>Width</label>
            <input 
              type="number" 
              :value="Math.round(element.width)"
              @input="updateProperty('width', Number($event.target.value))"
            />
          </div>
          <div class="input-group">
            <label>Height</label>
            <input 
              type="number" 
              :value="Math.round(element.height)"
              @input="updateProperty('height', Number($event.target.value))"
            />
          </div>
        </div>
        <div class="input-row">
          <div class="input-group">
            <label>Rotation</label>
            <input 
              type="number" 
              :value="Math.round(element.rotate)"
              @input="updateProperty('rotate', Number($event.target.value))"
              min="0"
              max="360"
            />
          </div>
          <div class="input-group">
            <label>Opacity</label>
            <input 
              type="range" 
              :value="(element.opacity || 1) * 100"
              @input="updateProperty('opacity', Number($event.target.value) / 100)"
              min="0"
              max="100"
            />
          </div>
        </div>
      </div>
      
      <!-- Text Properties -->
      <div v-if="element.type === 'text'" class="property-group">
        <label>Text</label>
        <textarea 
          :value="getTextContent(element)"
          @input="updateProperty('content', $event.target.value)"
          rows="3"
        ></textarea>
        
        <div class="input-row">
          <div class="input-group">
            <label>Font Size</label>
            <input 
              type="number" 
              :value="element.fontSize || 16"
              @input="updateProperty('fontSize', Number($event.target.value))"
              min="8"
              max="72"
            />
          </div>
          <div class="input-group">
            <label>Font Family</label>
            <select 
              :value="element.fontFamily || 'Arial'"
              @change="updateProperty('fontFamily', $event.target.value)"
            >
              <option value="Arial">Arial</option>
              <option value="Helvetica">Helvetica</option>
              <option value="Times New Roman">Times New Roman</option>
              <option value="Georgia">Georgia</option>
              <option value="Verdana">Verdana</option>
            </select>
          </div>
        </div>
        
        <div class="input-row">
          <div class="input-group">
            <label>Color</label>
            <input 
              type="color" 
              :value="element.color || element.defaultColor"
              @input="updateProperty('color', $event.target.value)"
            />
          </div>
          <div class="input-group">
            <label>Align</label>
            <select 
              :value="element.align || 'left'"
              @change="updateProperty('align', $event.target.value)"
            >
              <option value="left">Left</option>
              <option value="center">Center</option>
              <option value="right">Right</option>
            </select>
          </div>
        </div>
        
        <div class="checkbox-row">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              :checked="element.bold || false"
              @change="updateProperty('bold', $event.target.checked)"
            />
            Bold
          </label>
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              :checked="element.italic || false"
              @change="updateProperty('italic', $event.target.checked)"
            />
            Italic
          </label>
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              :checked="element.underline || false"
              @change="updateProperty('underline', $event.target.checked)"
            />
            Underline
          </label>
        </div>
      </div>
      
      <!-- Image Properties -->
      <div v-if="element.type === 'image'" class="property-group">
        <label>Image</label>
        <div class="input-row">
          <div class="input-group">
            <label>Fit</label>
            <select 
              :value="element.fit || 'contain'"
              @change="updateProperty('fit', $event.target.value)"
            >
              <option value="contain">Contain</option>
              <option value="cover">Cover</option>
              <option value="fill">Fill</option>
            </select>
          </div>
          <div class="input-group">
            <label>Border Radius</label>
            <input 
              type="number" 
              :value="element.borderRadius || 0"
              @input="updateProperty('borderRadius', Number($event.target.value))"
              min="0"
            />
          </div>
        </div>
        
        <div class="checkbox-row">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              :checked="element.shadow || false"
              @change="updateProperty('shadow', $event.target.checked)"
            />
            Shadow
          </label>
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              :checked="element.flipH || false"
              @change="updateProperty('flipH', $event.target.checked)"
            />
            Flip H
          </label>
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              :checked="element.flipV || false"
              @change="updateProperty('flipV', $event.target.checked)"
            />
            Flip V
          </label>
        </div>
      </div>
      
      <!-- Shape Properties -->
      <div v-if="element.type === 'shape'" class="property-group">
        <label>Shape</label>
        <div class="input-row">
          <div class="input-group">
            <label>Fill</label>
            <input 
              type="color" 
              :value="element.fill || '#4CAF50'"
              @input="updateProperty('fill', $event.target.value)"
            />
          </div>
          <div class="input-group">
            <label>Stroke</label>
            <input 
              type="color" 
              :value="element.stroke || '#2E7D32'"
              @input="updateProperty('stroke', $event.target.value)"
            />
          </div>
        </div>
        
        <div class="input-row">
          <div class="input-group">
            <label>Stroke Width</label>
            <input 
              type="number" 
              :value="element.strokeWidth || 2"
              @input="updateProperty('strokeWidth', Number($event.target.value))"
              min="0"
            />
          </div>
        </div>
      </div>
      
      <!-- Chart Properties -->
      <div v-if="element.type === 'chart'" class="property-group">
        <label>Chart</label>
        <div class="input-row">
          <div class="input-group">
            <label>Type</label>
            <select 
              :value="element.chartType"
              @change="updateProperty('chartType', $event.target.value)"
            >
              <option value="bar">Bar</option>
              <option value="line">Line</option>
              <option value="pie">Pie</option>
              <option value="doughnut">Doughnut</option>
              <option value="scatter">Scatter</option>
              <option value="area">Area</option>
            </select>
          </div>
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
          <button class="btn btn-sm" @click="bringForward">
            ↑ Forward
          </button>
          <button class="btn btn-sm" @click="sendBackward">
            ↓ Backward
          </button>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="property-group">
        <label>Actions</label>
        <div class="button-row">
          <button class="btn btn-sm" @click="duplicateElement">
            📋 Duplicate
          </button>
          <button class="btn btn-sm btn-danger" @click="deleteElement">
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePresentationStore } from '@/stores'
import type { PPTElement } from '@/types/slides'

interface Props {
  element: PPTElement
}

const props = defineProps<Props>()
const presentationStore = usePresentationStore()

async function updateProperty(property: string, value: any) {
  await presentationStore.modifyElement(props.element.id, {
    [property]: value
  })
}

function getElementTypeName(type: string): string {
  const typeNames = {
    text: 'Text',
    image: 'Image',
    shape: 'Shape',
    chart: 'Chart',
    table: 'Table',
    video: 'Video',
    audio: 'Audio'
  }
  return typeNames[type as keyof typeof typeNames] || type
}

function getTextContent(element: any): string {
  if (element.type !== 'text') return ''
  // Strip HTML tags for editing
  return element.content.replace(/<[^>]*>/g, '')
}

async function bringToFront() {
  const currentSlide = presentationStore.currentSlide
  if (!currentSlide) return
  
  const maxZIndex = Math.max(
    ...currentSlide.elements.map(el => el.zIndex || 1)
  )
  
  await updateProperty('zIndex', maxZIndex + 1)
}

async function sendToBack() {
  const currentSlide = presentationStore.currentSlide
  if (!currentSlide) return
  
  const minZIndex = Math.min(
    ...currentSlide.elements.map(el => el.zIndex || 1)
  )
  
  await updateProperty('zIndex', Math.max(0, minZIndex - 1))
}

async function bringForward() {
  const currentZIndex = props.element.zIndex || 1
  await updateProperty('zIndex', currentZIndex + 1)
}

async function sendBackward() {
  const currentZIndex = props.element.zIndex || 1
  await updateProperty('zIndex', Math.max(0, currentZIndex - 1))
}

async function duplicateElement() {
  presentationStore.copyElements([props.element.id])
  await presentationStore.pasteElements()
}

async function deleteElement() {
  if (confirm('Delete this element?')) {
    await presentationStore.removeElement(props.element.id)
    presentationStore.clearSelection()
  }
}
</script>

<style scoped>
.element-properties {
  font-size: var(--font-size-sm);
}

.property-section h4 {
  margin: 0 0 var(--spacing-md) 0;
  font-size: var(--font-size-md);
  color: var(--text-primary);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border);
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
.input-group select,
.input-group textarea {
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

textarea {
  resize: vertical;
  min-height: 60px;
}
</style>