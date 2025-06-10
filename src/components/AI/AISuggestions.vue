<template>
  <div class="ai-suggestions-overlay">
    <div class="suggestions-container">
      <div class="suggestions-header">
        <h3>🤖 AI Suggestions</h3>
        <button class="close-btn" @click="aiStore.clearSuggestions()">×</button>
      </div>
      
      <div class="suggestions-content">
        <div
          v-for="(suggestion, index) in aiStore.aiSuggestions"
          :key="index"
          class="suggestion-card"
          @click="applySuggestion(suggestion)"
        >
          <div class="suggestion-icon">
            {{ getSuggestionIcon(suggestion) }}
          </div>
          <div class="suggestion-details">
            <div class="suggestion-title">
              {{ getSuggestionTitle(suggestion) }}
            </div>
            <div class="suggestion-description">
              {{ getSuggestionDescription(suggestion) }}
            </div>
            <div class="suggestion-confidence">
              Confidence: {{ Math.round((suggestion as any).confidence * 100) || 85 }}%
            </div>
          </div>
          <div class="suggestion-actions">
            <button 
              class="action-btn apply-btn"
              @click.stop="applySuggestion(suggestion)"
            >
              Apply
            </button>
            <button 
              class="action-btn dismiss-btn"
              @click.stop="dismissSuggestion(index)"
            >
              ×
            </button>
          </div>
        </div>
      </div>
      
      <div class="suggestions-footer">
        <button class="btn btn-ghost btn-sm" @click="aiStore.clearSuggestions()">
          Dismiss All
        </button>
        <button class="btn btn-primary btn-sm" @click="generateMore">
          Generate More
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAIStore, usePresentationStore } from '@/stores'
import type { AtomicOperationData } from '@/types/atoms'

const aiStore = useAIStore()
const presentationStore = usePresentationStore()

async function applySuggestion(suggestion: AtomicOperationData) {
  try {
    await aiStore.executeAISuggestion(suggestion)
  } catch (error) {
    console.error('Failed to apply suggestion:', error)
  }
}

function dismissSuggestion(index: number) {
  aiStore.aiSuggestions.splice(index, 1)
}

async function generateMore() {
  await aiStore.generateSuggestions(presentationStore.canvas.activeSlide)
}

function getSuggestionIcon(suggestion: AtomicOperationData): string {
  const icons = {
    ADD: {
      text: '📝',
      image: '🖼️',
      shape: '🔷',
      chart: '📊',
      table: '📋'
    },
    MODIFY: '✏️',
    CREATE: '➕',
    DELETE: '🗑️',
    REMOVE: '❌',
    REORDER: '🔄',
    APPLY: '🎨'
  }
  
  if (suggestion.op === 'ADD' && typeof suggestion.type === 'string') {
    return icons.ADD[suggestion.type as keyof typeof icons.ADD] || '➕'
  }
  
  return icons[suggestion.op as keyof typeof icons] || '💡'
}

function getSuggestionTitle(suggestion: AtomicOperationData): string {
  const opTitles = {
    ADD: 'Add',
    REMOVE: 'Remove',
    MODIFY: 'Modify',
    CREATE: 'Create',
    DELETE: 'Delete',
    REORDER: 'Reorder',
    APPLY: 'Apply'
  }
  
  const typeNames = {
    text: 'Text',
    image: 'Image',
    shape: 'Shape',
    chart: 'Chart',
    table: 'Table',
    slide: 'Slide',
    theme: 'Theme'
  }
  
  return `${opTitles[suggestion.op]} ${typeNames[suggestion.type as keyof typeof typeNames] || suggestion.type}`
}

function getSuggestionDescription(suggestion: AtomicOperationData): string {
  switch (suggestion.op) {
    case 'ADD':
      switch (suggestion.type) {
        case 'text':
          return 'Add a title or content text to improve slide structure'
        case 'image':
          return 'Add a relevant image to enhance visual appeal'
        case 'shape':
          return 'Add a shape to create visual hierarchy'
        case 'chart':
          return 'Add a chart to visualize data effectively'
        case 'table':
          return 'Add a table to organize information clearly'
        default:
          return `Add a new ${suggestion.type} element`
      }
    case 'MODIFY':
      return 'Improve styling and positioning for better visual impact'
    case 'CREATE':
      return 'Create a new slide with optimized layout'
    case 'APPLY':
      if (suggestion.type === 'theme') {
        return 'Apply a cohesive theme for professional appearance'
      }
      return `Apply ${suggestion.type} improvements`
    case 'REORDER':
      return 'Reorganize elements for better flow and readability'
    default:
      return `AI suggests this ${suggestion.op.toLowerCase()} operation`
  }
}
</script>

<style scoped>
.ai-suggestions-overlay {
  position: fixed;
  bottom: var(--spacing-lg);
  right: var(--spacing-lg);
  z-index: 1500;
  max-width: 400px;
  max-height: 60vh;
}

.suggestions-container {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--border-radius-xl);
  box-shadow: 0 8px 32px var(--shadow-dark);
  overflow: hidden;
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.suggestions-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  color: white;
}

.suggestions-header h3 {
  margin: 0;
  font-size: var(--font-size-md);
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color var(--transition-fast);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.suggestions-content {
  max-height: 300px;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.suggestion-card {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  background: var(--border-light);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 2px solid transparent;
}

.suggestion-card:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px var(--shadow);
}

.suggestion-card:last-child {
  margin-bottom: 0;
}

.suggestion-icon {
  font-size: 24px;
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface);
  border-radius: 50%;
}

.suggestion-card:hover .suggestion-icon {
  background: white;
}

.suggestion-details {
  flex: 1;
  min-width: 0;
}

.suggestion-title {
  font-weight: 600;
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-xs);
}

.suggestion-description {
  font-size: var(--font-size-xs);
  line-height: 1.4;
  margin-bottom: var(--spacing-xs);
  opacity: 0.8;
}

.suggestion-confidence {
  font-size: 10px;
  opacity: 0.7;
  font-weight: 500;
}

.suggestion-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

.action-btn {
  padding: var(--spacing-xs);
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: var(--font-size-xs);
  font-weight: 500;
  transition: all var(--transition-fast);
  min-width: 50px;
}

.apply-btn {
  background: var(--primary);
  color: white;
}

.apply-btn:hover {
  background: var(--primary-dark);
}

.dismiss-btn {
  background: var(--text-disabled);
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  min-width: auto;
}

.dismiss-btn:hover {
  background: var(--accent);
}

.suggestion-card:hover .apply-btn {
  background: white;
  color: var(--primary);
}

.suggestion-card:hover .dismiss-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.suggestions-footer {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-top: 1px solid var(--border);
  background: var(--border-light);
}

/* Scrollbar styling */
.suggestions-content::-webkit-scrollbar {
  width: 4px;
}

.suggestions-content::-webkit-scrollbar-track {
  background: transparent;
}

.suggestions-content::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 2px;
}

.suggestions-content::-webkit-scrollbar-thumb:hover {
  background: var(--text-disabled);
}

/* Responsive design */
@media (max-width: 768px) {
  .ai-suggestions-overlay {
    bottom: var(--spacing-md);
    right: var(--spacing-md);
    left: var(--spacing-md);
    max-width: none;
  }
  
  .suggestion-card {
    flex-direction: column;
    text-align: center;
  }
  
  .suggestion-actions {
    flex-direction: row;
    justify-content: center;
  }
}
</style>