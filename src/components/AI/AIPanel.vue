<template>
  <div class="ai-panel">
    <button 
      class="ai-toggle-btn"
      :class="{ active: showPanel }"
      @click="togglePanel"
      title="AI Assistant"
    >
      🤖 AI
      <span v-if="aiStore.suggestionCount > 0" class="suggestion-badge">
        {{ aiStore.suggestionCount }}
      </span>
    </button>

    <div v-if="showPanel" class="ai-panel-content">
      <div class="ai-header">
        <h3>AI Assistant</h3>
        <button class="close-btn" @click="showPanel = false">×</button>
      </div>

      <div class="ai-body">
        <!-- AI Status -->
        <div class="ai-status">
          <div class="status-indicator" :class="{ ready: aiStore.isAIReady }"></div>
          <span v-if="aiStore.isAIReady">AI Ready</span>
          <span v-else>Learning... ({{ aiStore.modelMetrics.totalOperations }}/100 operations)</span>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <h4>Quick Actions</h4>
          <button 
            class="action-btn"
            @click="generateSuggestions"
            :disabled="aiStore.isLearning"
          >
            💡 Get Suggestions
          </button>
          <button 
            class="action-btn"
            @click="showGenerateModal = true"
            :disabled="!aiStore.isAIReady"
          >
            ✨ Generate Presentation
          </button>
          <button 
            class="action-btn"
            @click="enhanceCurrentSlide"
            :disabled="!aiStore.isAIReady"
          >
            🎨 Enhance Slide
          </button>
        </div>

        <!-- Current Suggestions -->
        <div v-if="aiStore.suggestionCount > 0" class="suggestions">
          <h4>Suggestions</h4>
          <div class="suggestion-list">
            <div
              v-for="(suggestion, index) in aiStore.aiSuggestions"
              :key="index"
              class="suggestion-item"
            >
              <div class="suggestion-content">
                <div class="suggestion-title">
                  {{ getSuggestionTitle(suggestion) }}
                </div>
                <div class="suggestion-description">
                  {{ getSuggestionDescription(suggestion) }}
                </div>
              </div>
              <div class="suggestion-actions">
                <button 
                  class="btn btn-sm btn-primary"
                  @click="applySuggestion(suggestion)"
                >
                  Apply
                </button>
                <button 
                  class="btn btn-sm btn-ghost"
                  @click="dismissSuggestion(index)"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Metrics -->
        <div class="ai-metrics">
          <h4>AI Performance</h4>
          <div class="metric">
            <span>Accuracy:</span>
            <span>{{ Math.round(aiStore.modelMetrics.accuracy * 100) }}%</span>
          </div>
          <div class="metric">
            <span>Operations:</span>
            <span>{{ aiStore.modelMetrics.totalOperations }}</span>
          </div>
          <div class="metric">
            <span>Successful Predictions:</span>
            <span>{{ aiStore.modelMetrics.successfulPredictions }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Generate Presentation Modal -->
    <div v-if="showGenerateModal" class="modal-overlay" @click="showGenerateModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Generate Presentation</h3>
          <button class="close-btn" @click="showGenerateModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Describe your presentation:</label>
            <textarea
              v-model="generatePrompt"
              placeholder="e.g., A quarterly business review with sales data, market analysis, and future projections"
              rows="4"
            ></textarea>
          </div>
          <div class="form-group">
            <label>Presentation type:</label>
            <select v-model="presentationType">
              <option value="business">Business</option>
              <option value="educational">Educational</option>
              <option value="marketing">Marketing</option>
              <option value="technical">Technical</option>
              <option value="creative">Creative</option>
            </select>
          </div>
          <div class="form-group">
            <label>Number of slides:</label>
            <input 
              type="number" 
              v-model="slideCount" 
              min="3" 
              max="20" 
              placeholder="10"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showGenerateModal = false">
            Cancel
          </button>
          <button 
            class="btn btn-primary"
            @click="generatePresentation"
            :disabled="!generatePrompt.trim() || aiStore.isLearning"
          >
            {{ aiStore.isLearning ? 'Generating...' : 'Generate' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAIStore, usePresentationStore } from '@/stores'
import type { AtomicOperationData } from '@/types/atoms'

const aiStore = useAIStore()
const presentationStore = usePresentationStore()

const showPanel = ref(false)
const showGenerateModal = ref(false)
const generatePrompt = ref('')
const presentationType = ref('business')
const slideCount = ref(10)

function togglePanel() {
  showPanel.value = !showPanel.value
}

async function generateSuggestions() {
  await aiStore.generateSuggestions(presentationStore.canvas.activeSlide)
}

async function enhanceCurrentSlide() {
  // This would analyze the current slide and suggest improvements
  const currentSlide = presentationStore.currentSlide
  if (!currentSlide) return

  // Generate contextual suggestions based on current content
  await aiStore.generateSuggestions(presentationStore.canvas.activeSlide)
}

async function generatePresentation() {
  if (!generatePrompt.value.trim()) return

  try {
    const fullPrompt = `${generatePrompt.value}\n\nType: ${presentationType.value}\nSlides: ${slideCount.value}`
    const sequence = await aiStore.generatePresentation(fullPrompt)
    
    // Clear current presentation
    presentationStore.newPresentation()
    
    // Execute the generated sequence
    await aiStore.executeOperationSequence(sequence)
    
    showGenerateModal.value = false
    generatePrompt.value = ''
  } catch (error) {
    console.error('Failed to generate presentation:', error)
    alert('Failed to generate presentation. Please try again.')
  }
}

async function applySuggestion(suggestion: AtomicOperationData) {
  try {
    await aiStore.executeAISuggestion(suggestion)
  } catch (error) {
    console.error('Failed to apply suggestion:', error)
    alert('Failed to apply suggestion. Please try again.')
  }
}

function dismissSuggestion(index: number) {
  aiStore.aiSuggestions.splice(index, 1)
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
      return `Add a new ${suggestion.type} element to enhance your slide`
    case 'MODIFY':
      return `Improve the styling and positioning of existing elements`
    case 'CREATE':
      return `Create a new slide with optimized layout`
    case 'APPLY':
      return `Apply ${suggestion.type} to improve visual consistency`
    default:
      return `Suggested ${suggestion.op.toLowerCase()} operation`
  }
}
</script>

<style scoped>
.ai-panel {
  position: relative;
}

.ai-toggle-btn {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: var(--font-size-sm);
}

.ai-toggle-btn:hover {
  background: var(--border-light);
}

.ai-toggle-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.suggestion-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--accent);
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
}

.ai-panel-content {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: var(--spacing-sm);
  width: 320px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 8px 32px var(--shadow-dark);
  z-index: 1000;
  max-height: 500px;
  overflow-y: auto;
}

.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border);
}

.ai-header h3 {
  margin: 0;
  font-size: var(--font-size-lg);
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  background: var(--border-light);
}

.ai-body {
  padding: var(--spacing-md);
}

.ai-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-sm);
  background: var(--border-light);
  border-radius: var(--border-radius);
  font-size: var(--font-size-sm);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-disabled);
}

.status-indicator.ready {
  background: #4CAF50;
}

.quick-actions,
.suggestions,
.ai-metrics {
  margin-bottom: var(--spacing-lg);
}

.quick-actions h4,
.suggestions h4,
.ai-metrics h4 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-md);
  color: var(--text-primary);
}

.action-btn {
  display: block;
  width: 100%;
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
  background: var(--border-light);
  border: 1px solid var(--border);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
  font-size: var(--font-size-sm);
}

.action-btn:hover:not(:disabled) {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  background: var(--border-light);
  border-radius: var(--border-radius);
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-weight: 500;
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-xs);
}

.suggestion-description {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.4;
}

.suggestion-actions {
  display: flex;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

.ai-metrics {
  font-size: var(--font-size-sm);
}

.metric {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-xs);
}

.metric span:first-child {
  color: var(--text-secondary);
}

.metric span:last-child {
  font-weight: 500;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: var(--surface);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 8px 32px var(--shadow-dark);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
}

.modal-body {
  padding: var(--spacing-lg);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
  color: var(--text-primary);
}

.form-group textarea,
.form-group select,
.form-group input {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--border);
  border-radius: var(--border-radius);
  font-size: var(--font-size-sm);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}
</style>